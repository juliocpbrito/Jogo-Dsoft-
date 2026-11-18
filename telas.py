# Arquivo: telas.py
# Autor: Julio (A)
# Uso de IA: código escrito com auxílio do Claude (Anthropic) e revisado,
# testado e entendido pelo autor. Detalhes na seção "Uso de IA" do README.
import math
import os
import pygame
from config import LARGURA, ALTURA, COR_FUNDO, COR_TEXTO  # constantes do config.py


def escrever(tela, texto, tamanho, y):
    """Escreve um texto centralizado na horizontal, na altura y."""
    fonte = pygame.font.Font(None, tamanho)  # None = fonte padrão do PyGame, no tamanho pedido
    imagem = fonte.render(texto, True, COR_TEXTO)  # transforma o texto numa imagem (True = bordas suaves)
    retangulo = imagem.get_rect(center=(LARGURA // 2, y))  # Rect da imagem, com o centro em (meio da tela, y)
    tela.blit(imagem, retangulo)  # cola a imagem na tela, na posição do retângulo


_fontes = {}  # guarda as fontes já criadas: criar fonte a cada quadro seria lento
_imagens = {}  # guarda imagens prontas (degradê, painel) pelo mesmo motivo


def obter_fonte(tamanho):
    """Fonte grossa para o título. Tenta Arial Black ou Impact; se o computador não tiver, usa a padrão."""
    if tamanho not in _fontes:  # ainda não criamos essa fonte neste tamanho?
        try:
            _fontes[tamanho] = pygame.font.SysFont("arialblack,impact,arial", tamanho, bold=True)
        except Exception:  # qualquer problema com fontes do sistema: usamos a padrão do PyGame
            _fontes[tamanho] = pygame.font.Font(None, tamanho)
    return _fontes[tamanho]


def escrever_contorno(tela, texto, tamanho, cor, cor_contorno, centro, espessura=4):
    """Texto com contorno: escreve o texto várias vezes deslocado na cor do contorno e, por cima, na cor certa."""
    fonte = obter_fonte(tamanho)
    contorno = fonte.render(texto, True, cor_contorno)
    miolo = fonte.render(texto, True, cor)
    retangulo = miolo.get_rect(center=centro)
    for dx in range(-espessura, espessura + 1):
        for dy in range(-espessura, espessura + 1):
            if dx * dx + dy * dy <= espessura * espessura:  # só os deslocamentos dentro de um círculo
                tela.blit(contorno, retangulo.move(dx, dy))  # move() devolve o retângulo deslocado
    tela.blit(miolo, retangulo)


def escrever_esquerda(tela, texto, tamanho, x, y, cor):
    """Texto alinhado à esquerda: o lado esquerdo do texto fica em x (e o meio na altura y)."""
    imagem = pygame.font.Font(None, tamanho).render(texto, True, cor)
    tela.blit(imagem, imagem.get_rect(midleft=(x, y)))


def desenhar_tecla(tela, x, y, simbolo):
    """Desenha uma tecla do teclado com uma seta ou uma letra dentro. (x, y) é o centro da tecla."""
    caixa = pygame.Rect(0, 0, 30, 30)
    caixa.center = (x, y)
    pygame.draw.rect(tela, (235, 235, 235), caixa, border_radius=6)       # corpo da tecla
    pygame.draw.rect(tela, (120, 120, 120), caixa, 2, border_radius=6)    # borda
    setas = {"esq": [(x - 7, y), (x + 5, y - 8), (x + 5, y + 8)],
             "dir": [(x + 7, y), (x - 5, y - 8), (x - 5, y + 8)],
             "cima": [(x, y - 7), (x - 8, y + 5), (x + 8, y + 5)],
             "baixo": [(x, y + 7), (x - 8, y - 5), (x + 8, y - 5)]}
    if simbolo in setas:  # setas: um triângulo
        pygame.draw.polygon(tela, (40, 40, 40), setas[simbolo])
    else:  # qualquer outra coisa é uma letra
        letra = pygame.font.Font(None, 28).render(simbolo, True, (40, 40, 40))
        tela.blit(letra, letra.get_rect(center=(x, y)))


def painel_inferior():
    """Retângulo arredondado preto e semitransparente, onde ficam o recorde e os controles."""
    if "painel" not in _imagens:
        imagem = pygame.Surface((440, 156), pygame.SRCALPHA)
        pygame.draw.rect(imagem, (0, 0, 0, 185), (0, 0, 440, 156), border_radius=18)
        _imagens["painel"] = imagem
    return _imagens["painel"]


CAMINHO_FUNDO_MENU = os.path.join("assets", "imagens", "menu.png")  # arte da capa do jogo


def fundo_menu():
    """Carrega a arte do menu uma vez só e a ajusta ao tamanho da janela. Se faltar o arquivo, devolve None."""
    if "fundo" not in _imagens:
        try:
            imagem = pygame.image.load(CAMINHO_FUNDO_MENU).convert()  # convert(): deixa a imagem no formato rápido da tela
            _imagens["fundo"] = pygame.transform.smoothscale(imagem, (LARGURA, ALTURA))  # ajusta ao tamanho da janela
        except (pygame.error, FileNotFoundError):
            _imagens["fundo"] = None  # sem a imagem, o menu usa o título em texto
    return _imagens["fundo"]


def desenhar_menu(tela, melhor, quadro):
    """Menu inicial. 'quadro' é um contador que cresce sempre: é ele que faz o aviso piscar."""
    fundo = fundo_menu()
    if fundo is not None:
        tela.blit(fundo, (0, 0))  # a arte já traz o título "Delivery Surfers" desenhado
    else:
        # Plano B, se a imagem não existir: fundo liso e título em texto.
        tela.fill(COR_FUNDO)
        balanco = int(math.sin(quadro * 0.06) * 5)
        escrever_contorno(tela, "DELIVERY", 82, (255, 205, 45), (70, 35, 0), (LARGURA // 2, 150 + balanco))
        escrever_contorno(tela, "SURFERS", 82, (70, 215, 120), (10, 70, 35), (LARGURA // 2, 235 - balanco))

    # Painel de baixo, sobre a parte vazia da rua.
    tela.blit(painel_inferior(), (20, 638))
    escrever(tela, "Recorde: " + str(melhor) + " m", 40, 664)
    if (quadro // 30) % 2 == 0:  # pisca: aparece por meio segundo, some por meio segundo
        escrever(tela, "Aperte ESPAÇO para jogar", 36, 706)

    # Controles, com desenho das teclas.
    y = 758
    desenhar_tecla(tela, 40, y, "esq")
    desenhar_tecla(tela, 74, y, "dir")
    escrever_esquerda(tela, "pista", 24, 94, y, (230, 230, 230))
    desenhar_tecla(tela, 180, y, "cima")
    escrever_esquerda(tela, "pular", 24, 200, y, (230, 230, 230))
    desenhar_tecla(tela, 280, y, "baixo")
    escrever_esquerda(tela, "deslizar", 24, 300, y, (230, 230, 230))
    desenhar_tecla(tela, 392, y, "P")
    escrever_esquerda(tela, "pausa", 24, 412, y, (230, 230, 230))


def desenhar_placar(tela, distancia):
    # int() corta a parte decimal: 12.8 vira 12
    escrever(tela, "Distância: " + str(int(distancia)) + " m", 36, 30)  # y = 30: no topo da tela


def desenhar_game_over(tela, distancia, melhor):
    tela.fill(COR_FUNDO)
    escrever(tela, "GAME OVER", 64, ALTURA // 3)
    escrever(tela, "Distância: " + str(int(distancia)) + " m", 40, ALTURA // 2)
    escrever(tela, "Recorde: " + str(melhor) + " m", 40, ALTURA // 2 + 50)
    escrever(tela, "Aperte ESPAÇO para jogar de novo", 28, ALTURA // 2 + 110)


def desenhar_pausa(tela):
    """Escurece a tela e mostra o aviso de pausa por cima do jogo."""
    escurecer = pygame.Surface((LARGURA, ALTURA))  # Surface = uma "folha" em branco do tamanho da tela
    escurecer.set_alpha(150)  # transparência: 0 = invisível, 255 = totalmente opaco
    escurecer.fill((0, 0, 0))  # pinta a folha de preto
    tela.blit(escurecer, (0, 0))  # cola a folha preta semitransparente por cima do jogo, a partir do canto
    escrever(tela, "PAUSADO", 64, ALTURA // 3)
    escrever(tela, "Aperte P para continuar", 32, ALTURA // 2)