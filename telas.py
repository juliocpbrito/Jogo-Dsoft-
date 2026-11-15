import pygame
from config import LARGURA, ALTURA, COR_FUNDO, COR_TEXTO


def escrever(tela, texto, tamanho, y):
    """Escreve um texto centralizado na horizontal, na altura y."""
    fonte = pygame.font.Font(None, tamanho)
    imagem = fonte.render(texto, True, COR_TEXTO)
    retangulo = imagem.get_rect(center=(LARGURA // 2, y))
    tela.blit(imagem, retangulo)


def desenhar_menu(tela):
    tela.fill(COR_FUNDO)
    escrever(tela, "DELIVERY SURFERS", 56, ALTURA // 3)
    escrever(tela, "Aperte ESPAÇO para jogar", 32, ALTURA // 2)


def desenhar_placar(tela, pontos):
    escrever(tela, "Pontos: " + str(pontos), 36, 30)


def desenhar_game_over(tela, pontos):
    tela.fill(COR_FUNDO)
    escrever(tela, "GAME OVER", 64, ALTURA // 3)
    escrever(tela, "Pontos: " + str(pontos), 40, ALTURA // 2)
    escrever(tela, "Aperte ESPAÇO para jogar de novo", 28, ALTURA // 2 + 60)