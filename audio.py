# Arquivo: audio.py
# Autor: Julio (A)
# Uso de IA: código escrito com auxílio do Claude (Anthropic) e revisado,
# testado e entendido pelo autor. Detalhes na seção "Uso de IA" do README.
#
# Música de fundo e efeitos sonoros. Se um arquivo de som não existir (ou o computador
# não tiver saída de áudio), o jogo continua normalmente, só sem aquele som.
#
# Arquivos esperados na pasta assets/sons (pode ser .ogg, .wav ou .mp3):
#   musica   - música de fundo (toca em loop durante a partida)
#   pulo     - efeito ao pular
#   batida   - efeito ao bater num obstáculo
#   game_over - efeito ao perder
#   gorjeta  - efeito ao pegar uma gorjeta (opcional, para o mundo.py do C)

import os
import pygame

PASTA = os.path.join("assets", "sons")     # os.path.join monta o caminho certo em qualquer sistema
EXTENSOES = [".ogg", ".wav", ".mp3"]        # formatos que tentamos, nessa ordem
NOMES_EFEITOS = ["pulo", "batida", "game_over", "gorjeta"]
VOLUME_MUSICA = 0.4   # de 0.0 (mudo) a 1.0 (máximo); a música não pode abafar os efeitos
VOLUME_EFEITOS = 0.7

sons = {}              # efeitos já carregados: nome -> pygame.mixer.Sound
caminho_musica = None  # arquivo da música, se existir
ativo = False          # só vira True se o sistema de áudio funcionar


def achar_arquivo(nome):
    """Procura assets/sons/<nome> com cada extensão e devolve o primeiro caminho que existe (ou None)."""
    for extensao in EXTENSOES:
        caminho = os.path.join(PASTA, nome + extensao)
        if os.path.exists(caminho):  # existe esse arquivo?
            return caminho
    return None  # nenhum encontrado


def iniciar():
    """Prepara o áudio. Chamar uma vez, depois do pygame.init()."""
    global caminho_musica, ativo  # global: vamos mudar as variáveis lá de cima, não criar locais
    ativo = pygame.mixer.get_init() is not None  # None = o mixer não conseguiu ligar (sem som no computador)
    if not ativo:
        return
    caminho_musica = achar_arquivo("musica")
    for nome in NOMES_EFEITOS:
        caminho = achar_arquivo(nome)
        if caminho is not None:
            try:
                som = pygame.mixer.Sound(caminho)  # carrega o efeito inteiro na memória
                som.set_volume(VOLUME_EFEITOS)
                sons[nome] = som
            except pygame.error:  # arquivo estragado ou formato que o pygame não lê
                print("Aviso: não consegui carregar o som", caminho)


def tocar_efeito(nome):
    """Toca um efeito curto, como 'pulo' ou 'batida'. Se não existir, não faz nada."""
    if ativo and nome in sons:
        sons[nome].play()


def tocar_musica():
    """Começa a música de fundo do início e repete sem parar."""
    if ativo and caminho_musica is not None:
        try:
            pygame.mixer.music.load(caminho_musica)  # a música é lida aos poucos (é grande)
            pygame.mixer.music.set_volume(VOLUME_MUSICA)
            pygame.mixer.music.play(-1)  # -1 = repete para sempre
        except pygame.error:
            print("Aviso: não consegui tocar a música", caminho_musica)


def parar_musica():
    if ativo:
        pygame.mixer.music.stop()


def pausar_musica():
    if ativo:
        pygame.mixer.music.pause()


def retomar_musica():
    if ativo:
        pygame.mixer.music.unpause()