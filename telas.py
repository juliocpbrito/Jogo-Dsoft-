import pygame
from config import LARGURA, ALTURA, COR_FUNDO, COR_TEXTO  # constantes do config.py


def escrever(tela, texto, tamanho, y):
    """Escreve um texto centralizado na horizontal, na altura y."""
    fonte = pygame.font.Font(None, tamanho)  # None = fonte padrão do PyGame, no tamanho pedido
    imagem = fonte.render(texto, True, COR_TEXTO)  # transforma o texto numa imagem (True = bordas suaves)
    retangulo = imagem.get_rect(center=(LARGURA // 2, y))  # Rect da imagem, com o centro em (meio da tela, y)
    tela.blit(imagem, retangulo)  # cola a imagem na tela, na posição do retângulo


def desenhar_menu(tela, melhor):
    tela.fill(COR_FUNDO)  # pinta a tela inteira com a cor de fundo
    escrever(tela, "DELIVERY SURFERS", 56, ALTURA // 3)  # título, a 1/3 da altura
    escrever(tela, "Recorde: " + str(melhor) + " m", 36, ALTURA // 2 - 50)  # str() transforma o número em texto
    escrever(tela, "Aperte ESPAÇO para jogar", 32, ALTURA // 2 + 10)


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