import customtkinter as ctk
import tkinter
from tkinter import filedialog
import pygame
import os
import random
from mutagen.mp3 import MP3
from PIL import Image, ImageTk # Importa as bibliotecas necessárias para a imagem

# --- Classe Principal da Aplicação ---
class MusicPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Esconde a janela principal inicialmente
        self.setup_splash_screen()

    def setup_splash_screen(self):
        # Cria a janela de splash screen
        self.splash = ctk.CTkToplevel(self.root)
        self.splash.geometry("400x250")
        self.splash.overrideredirect(True)  # Remove a barra de título e bordas
        self.splash.attributes("-topmost", True)

        # Centraliza a splash screen
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width / 2) - (400 / 2)
        y = (screen_height / 2) - (250 / 2)
        self.splash.geometry(f'+{int(x)}+{int(y)}')

        # --- ALTERAÇÃO DE COR DA TELA DE BOAS-VINDAS ---
        # Frame com fundo claro
        splash_frame = ctk.CTkFrame(self.splash, corner_radius=15, fg_color="#F0F0F0")
        splash_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Título e ícone com cores de alto contraste
        icon_label = ctk.CTkLabel(splash_frame, text="🎵", font=ctk.CTkFont(size=60), text_color="#1DB954")
        icon_label.pack(pady=(30, 10))

        title_label = ctk.CTkLabel(splash_frame, text="Meu Player de Música", font=ctk.CTkFont(size=24, weight="bold"), text_color="black")
        title_label.pack(pady=5)

        version_label = ctk.CTkLabel(splash_frame, text="Versão 1.0", font=ctk.CTkFont(size=12), text_color="#505050")
        version_label.pack(pady=5)

        # Força a atualização da janela para desenhar os widgets
        self.splash.update()

        # Agenda a transição para a janela principal após 3 segundos (3000 ms)
        self.splash.after(3000, self.show_main_window)

    def show_main_window(self):
        self.splash.destroy()  # Destrói a splash screen
        self.root.deiconify()  # Mostra a janela principal
        self.setup_main_ui()   # Configura a UI do player

    def setup_main_ui(self):
        # --- Configurações da Janela Principal ---
        self.root.title("🎵 Player de Música Moderno")
        self.root.geometry("600x680")
        self.root.resizable(False, False)

        # --- Variáveis de Instância ---
        self.musicas = []
        self.nomes_musicas = []
        self.musica_atual = ""
        self.indice_atual = -1
        self.pausado = False
        self.duracao_total_musica = 0
        self.posicao_seek = 0
        self.modo_aleatorio = False
        self.playlist_aleatoria = []

        # --- Cores ---
        self.ACTIVE_COLOR = "#1DB954"
        self.INACTIVE_COLOR = "black"
        self.HOVER_COLOR = "#333333"

        # --- Interface Gráfica ---
        frame_principal = ctk.CTkFrame(self.root)
        frame_principal.pack(pady=20, padx=20, fill="both", expand=True)
        
        titulo = ctk.CTkLabel(frame_principal, text="🎶 Meu Player de Música", font=ctk.CTkFont(size=20, weight="bold"))
        titulo.pack(pady=10)
        
        botao_pasta = ctk.CTkButton(frame_principal, text="📂 Carregar Pasta de Músicas", command=self.carregar_pasta, width=220)
        botao_pasta.pack(pady=5)
        
        frame_playlist = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_playlist.pack(pady=5)
        
        self.btn_salvar = ctk.CTkButton(frame_playlist, text="💾 Salvar Playlist", command=self.salvar_playlist, width=160)
        self.btn_salvar.grid(row=0, column=0, padx=5)
        
        self.btn_carregar = ctk.CTkButton(frame_playlist, text="📂 Carregar Playlist", command=self.carregar_playlist, width=160)
        self.btn_carregar.grid(row=0, column=1, padx=5)
        
        self.lista_musicas = tkinter.Listbox(
            frame_principal, height=10, width=60, bg="#2B2B2B", fg="white",
            selectbackground=self.ACTIVE_COLOR, selectforeground="white", borderwidth=0,
            highlightthickness=1, highlightbackground="#565B5E"
        )
        self.lista_musicas.pack(pady=10, padx=10, fill="x")
        self.lista_musicas.bind('<<ListboxSelect>>', self.selecionar_musica)
        
        self.label_musica_tocando = ctk.CTkLabel(frame_principal, text="", font=ctk.CTkFont(size=12), wraplength=400)
        self.label_musica_tocando.pack(pady=(5, 10))
        
        frame_controles = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_controles.pack(pady=10)
        
        self.btn_anterior = ctk.CTkButton(frame_controles, text="⏮️", command=self.anterior_musica, width=50, fg_color=self.INACTIVE_COLOR, hover_color=self.HOVER_COLOR)
        self.btn_anterior.grid(row=0, column=0, padx=5)
        self.btn_play = ctk.CTkButton(frame_controles, text="▶️", command=self.tocar, width=70, font=ctk.CTkFont(size=18, weight="bold"), fg_color=self.ACTIVE_COLOR, hover_color="#1ED760")
        self.btn_play.grid(row=0, column=1, padx=5)
        self.btn_pause = ctk.CTkButton(frame_controles, text="⏸️", command=self.pausar, width=50, fg_color=self.INACTIVE_COLOR, hover_color=self.HOVER_COLOR)
        self.btn_pause.grid(row=0, column=2, padx=5)
        self.btn_stop = ctk.CTkButton(frame_controles, text="⏹️", command=self.parar, width=50, fg_color=self.INACTIVE_COLOR, hover_color=self.HOVER_COLOR)
        self.btn_stop.grid(row=0, column=3, padx=5)
        self.btn_proxima = ctk.CTkButton(frame_controles, text="⏭️", command=self.proxima_musica, width=50, fg_color=self.INACTIVE_COLOR, hover_color=self.HOVER_COLOR)
        self.btn_proxima.grid(row=0, column=4, padx=5)
        self.btn_aleatorio = ctk.CTkButton(frame_controles, text="🔀", command=self.alternar_aleatorio, width=50, fg_color=self.INACTIVE_COLOR, hover_color=self.HOVER_COLOR)
        self.btn_aleatorio.grid(row=0, column=5, padx=5)

        frame_progresso = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_progresso.pack(pady=5, padx=10, fill="x")
        self.label_tempo_atual = ctk.CTkLabel(frame_progresso, text="00:00", font=ctk.CTkFont(size=12))
        self.label_tempo_atual.grid(row=0, column=0, padx=5)
        self.progress_slider = ctk.CTkSlider(frame_progresso, from_=0, to=1, command=self.seek, number_of_steps=1000, button_color=self.ACTIVE_COLOR, progress_color=self.ACTIVE_COLOR)
        self.progress_slider.set(0)
        self.progress_slider.configure(state="disabled")
        self.progress_slider.grid(row=0, column=1, sticky="ew", padx=5)
        self.label_tempo_total = ctk.CTkLabel(frame_progresso, text="00:00", font=ctk.CTkFont(size=12))
        self.label_tempo_total.grid(row=0, column=2, padx=5)
        frame_progresso.grid_columnconfigure(1, weight=1)

        self.label_volume = ctk.CTkLabel(frame_principal, text="🔊 Volume: 70", pady=10)
        self.label_volume.pack()
        slider_volume = ctk.CTkSlider(frame_principal, from_=0, to=100, command=self.ajustar_volume, width=250, button_color=self.ACTIVE_COLOR, progress_color=self.ACTIVE_COLOR)
        slider_volume.set(70)
        pygame.mixer.music.set_volume(0.7)
        slider_volume.pack(pady=5)
        
        self.status_bar = ctk.CTkLabel(self.root, text="Pronto.", anchor="w", font=ctk.CTkFont(size=12))
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=5)
        
        self.root.after(1000, self.atualizar_barra_progresso)

    # --- Métodos da Classe ---
    def flash_button_color(self, button):
        # Muda a cor do botão para verde ativo e depois volta para preto inativo
        button.configure(fg_color=self.ACTIVE_COLOR)
        self.root.after(150, lambda: button.configure(fg_color=self.INACTIVE_COLOR))

    def formatar_tempo(self, total_seconds):
        if total_seconds is None: return "00:00"
        minutes, seconds = divmod(int(total_seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def seek(self, value):
        if self.duracao_total_musica > 0 and self.musica_atual:
            self.posicao_seek = self.duracao_total_musica * float(value)
            self.reproduzir_musica(self.indice_atual, manter_posicao=True)
            if self.pausado:
                pygame.mixer.music.pause()

    def atualizar_barra_progresso(self):
        if self.musica_atual and not self.pausado:
            if pygame.mixer.music.get_busy():
                posicao_atual_segundos = self.posicao_seek + (pygame.mixer.music.get_pos() / 1000)
                self.label_tempo_atual.configure(text=self.formatar_tempo(posicao_atual_segundos))
                if self.duracao_total_musica > 0:
                    progresso = min(posicao_atual_segundos / self.duracao_total_musica, 1.0)
                    if abs(self.progress_slider.get() - progresso) > 0.01:
                         self.progress_slider.set(progresso)
            else:
                if self.duracao_total_musica > 0:
                     self.proxima_musica()
        self.root.after(1000, self.atualizar_barra_progresso)

    def atualizar_estado(self, mensagem, cor="black"):
        self.status_bar.configure(text=mensagem, text_color=cor)

    def salvar_playlist(self):
        if not self.musicas:
            self.atualizar_estado("Nenhuma música na lista para salvar.", cor="black")
            return
        caminho_arquivo = filedialog.asksaveasfilename(
            title="Salvar playlist como", defaultextension=".txt",
            filetypes=[("Ficheiros de Texto", "*.txt"), ("Todos os ficheiros", "*.*")]
        )
        if caminho_arquivo:
            try:
                with open(os.path.normpath(caminho_arquivo), 'w', encoding='utf-8') as f:
                    for caminho_musica in self.musicas:
                        f.write(f"{os.path.normpath(caminho_musica)}\n")
                self.atualizar_estado("Playlist salva com sucesso!", cor="black")
            except Exception as e:
                self.atualizar_estado(f"Erro ao salvar: {e}", cor="black")

    def carregar_playlist(self):
        caminho_arquivo = filedialog.askopenfilename(
            title="Abrir playlist", filetypes=[("Ficheiros de Texto", "*.txt"), ("Todos os ficheiros", "*.*")]
        )
        if caminho_arquivo:
            self.parar()
            self.musicas.clear(); self.nomes_musicas.clear(); self.lista_musicas.delete(0, tkinter.END)
            try:
                with open(os.path.normpath(caminho_arquivo), 'r', encoding='utf-8') as f:
                    musicas_carregadas = 0
                    for linha in f:
                        caminho_musica = os.path.normpath(linha.strip())
                        if os.path.exists(caminho_musica):
                            self.musicas.append(caminho_musica)
                            self.nomes_musicas.append(os.path.basename(caminho_musica))
                            self.lista_musicas.insert(tkinter.END, os.path.basename(caminho_musica))
                            musicas_carregadas += 1
                    if musicas_carregadas > 0:
                        self.atualizar_estado(f"Playlist carregada: {musicas_carregadas} músicas.", cor="black")
                    else:
                        self.atualizar_estado("Playlist vazia ou ficheiros não encontrados.", cor="black")
            except Exception as e:
                self.atualizar_estado(f"Erro ao carregar: {e}", cor="black")

    def carregar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta com músicas")
        if pasta:
            self.parar()
            self.musicas.clear(); self.nomes_musicas.clear(); self.lista_musicas.delete(0, tkinter.END)
            for arquivo in os.listdir(pasta):
                if arquivo.lower().endswith((".mp3", ".wav")):
                    caminho = os.path.join(pasta, arquivo)
                    self.musicas.append(caminho)
                    self.nomes_musicas.append(arquivo)
                    self.lista_musicas.insert(tkinter.END, arquivo)
            self.atualizar_estado(f"{len(self.musicas)} músicas carregadas da pasta.")

    def reproduzir_musica(self, indice_da_musica, manter_posicao=False):
        if not manter_posicao:
            self.posicao_seek = 0
        lista_usada = self.playlist_aleatoria if self.modo_aleatorio else self.musicas
        if not lista_usada or not (0 <= indice_da_musica < len(lista_usada)):
            return
        try:
            self.indice_atual = indice_da_musica
            self.musica_atual = lista_usada[self.indice_atual]
            pygame.mixer.music.load(self.musica_atual)
            pygame.mixer.music.play(start=self.posicao_seek)
            self.pausado = False
            self.progress_slider.configure(state="normal")
            audio = MP3(self.musica_atual)
            self.duracao_total_musica = audio.info.length
            self.label_tempo_total.configure(text=self.formatar_tempo(self.duracao_total_musica))
            self.atualizar_titulo_musica()
            self.atualizar_selecao()
            # Atualiza cores dos botões para o estado "A tocar"
            self.btn_play.configure(fg_color=self.INACTIVE_COLOR)
            self.btn_pause.configure(fg_color=self.ACTIVE_COLOR, hover_color="#1ED760")
        except Exception as e:
            self.atualizar_estado(f"Não foi possível tocar: {os.path.basename(self.musica_atual)}", cor="black")

    def tocar(self):
        if self.pausado:
            pygame.mixer.music.unpause()
            self.pausado = False
            self.atualizar_titulo_musica()
            # Atualiza cores dos botões para o estado "A tocar"
            self.btn_play.configure(fg_color=self.INACTIVE_COLOR)
            self.btn_pause.configure(fg_color=self.ACTIVE_COLOR, hover_color="#1ED760")
        elif not pygame.mixer.music.get_busy():
            indice_a_tocar = self.indice_atual if self.indice_atual != -1 else 0
            self.reproduzir_musica(indice_a_tocar)

    def pausar(self):
        if self.musica_atual:
            pygame.mixer.music.pause()
            self.pausado = True
            self.atualizar_estado("Música pausada.")
            # Atualiza cores dos botões para o estado "Pausado"
            self.btn_play.configure(fg_color=self.ACTIVE_COLOR, hover_color="#1ED760")
            self.btn_pause.configure(fg_color=self.INACTIVE_COLOR)

    def parar(self):
        self.flash_button_color(self.btn_stop)
        pygame.mixer.music.stop()
        self.label_musica_tocando.configure(text="")
        self.root.title("🎵 Player de Música Moderno")
        self.pausado = False
        self.indice_atual = -1
        self.musica_atual = ""
        self.posicao_seek = 0
        self.progress_slider.set(0)
        self.label_tempo_atual.configure(text="00:00")
        self.label_tempo_total.configure(text="00:00")
        self.progress_slider.configure(state="disabled")
        self.atualizar_estado("Pronto.")
        # Reseta as cores dos botões para o estado "Parado"
        self.btn_play.configure(fg_color=self.ACTIVE_COLOR, hover_color="#1ED760")
        self.btn_pause.configure(fg_color=self.INACTIVE_COLOR)
        
    def proxima_musica(self):
        if not self.musicas: return
        self.flash_button_color(self.btn_proxima)
        lista_usada = self.playlist_aleatoria if self.modo_aleatorio else self.musicas
        proximo_indice = (self.indice_atual + 1) % len(lista_usada)
        self.reproduzir_musica(proximo_indice)

    def anterior_musica(self):
        if not self.musicas: return
        self.flash_button_color(self.btn_anterior)
        lista_usada = self.playlist_aleatoria if self.modo_aleatorio else self.musicas
        indice_anterior = (self.indice_atual - 1 + len(self.musicas)) % len(lista_usada)
        self.reproduzir_musica(indice_anterior)

    def alternar_aleatorio(self):
        if not self.musicas: return
        self.modo_aleatorio = not self.modo_aleatorio
        if self.modo_aleatorio:
            self.btn_aleatorio.configure(fg_color=self.ACTIVE_COLOR, hover_color="#1ED760")
            self.playlist_aleatoria = self.musicas[:]
            random.shuffle(self.playlist_aleatoria)
            if self.musica_atual in self.playlist_aleatoria:
                self.indice_atual = self.playlist_aleatoria.index(self.musica_atual)
            else:
                self.indice_atual = -1
            self.atualizar_estado("Modo aleatório ativado.", cor="black")
        else:
            self.btn_aleatorio.configure(fg_color=self.INACTIVE_COLOR)
            if self.musica_atual in self.musicas:
                self.indice_atual = self.musicas.index(self.musica_atual)
            self.atualizar_estado("Modo aleatório desativado.")

    def selecionar_musica(self, event=None):
        selecao = self.lista_musicas.curselection()
        if not selecao: return
        if self.modo_aleatorio:
            self.modo_aleatorio = False
            self.btn_aleatorio.configure(fg_color=self.INACTIVE_COLOR)
        indice_clicado = selecao[0]
        self.reproduzir_musica(indice_clicado)

    def atualizar_selecao(self):
        if self.musica_atual in self.musicas:
            indice_visual = self.musicas.index(self.musica_atual)
            self.lista_musicas.selection_clear(0, tkinter.END)
            self.lista_musicas.selection_set(indice_visual)
            self.lista_musicas.activate(indice_visual)
            self.lista_musicas.see(indice_visual)

    def atualizar_titulo_musica(self):
        if self.musica_atual in self.musicas:
            nome_musica = self.nomes_musicas[self.musicas.index(self.musica_atual)]
            self.label_musica_tocando.configure(text=f"A tocar: {nome_musica}")
            self.root.title(f"🎵 A tocar: {nome_musica}")
            self.atualizar_estado(f"A tocar: {nome_musica}")

    def ajustar_volume(self, val):
        volume = float(val) / 100
        pygame.mixer.music.set_volume(volume)
        self.label_volume.configure(text=f"🔊 Volume: {int(val)}")

# --- Ponto de Entrada da Aplicação ---
if __name__ == "__main__":
    # Inicializa o mixer do Pygame
    pygame.mixer.init()
    
    # Define o tema de cores
    ctk.set_default_color_theme("green")

    # Configura a janela principal do CustomTkinter
    root = ctk.CTk()
    app = MusicPlayerApp(root)
    root.mainloop()
