import pygame
from config import LARGURA, ALTURA, FPS, COR_FUNDO, COR_LINHA
import telas


def desenhar_pista(tela):
    tela.fill(COR_FUNDO)
    for x in (LARGURA // 3, 2 * LARGURA // 3):
        pygame.draw.line(tela, COR_LINHA, (x, 0), (x, ALTURA), 3)


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Delivery Surfers")
    relogio = pygame.time.Clock()

    estado = "menu"  # "menu", "jogando" ou "game_over"
    pontos = 0

    rodando = True
    while rodando:
        # 1) Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    if estado == "menu" or estado == "game_over":
                        estado = "jogando"
                        pontos = 0
                elif evento.key == pygame.K_ESCAPE and estado == "jogando":
                    estado = "game_over"  # TEMPORÁRIO: simula perder o jogo

        # 2) Atualização e 3) Desenho, de acordo com o estado
        if estado == "menu":
            telas.desenhar_menu(tela)
        elif estado == "jogando":
            pontos += 1  # TEMPORÁRIO: depois vira distância percorrida
            desenhar_pista(tela)
            telas.desenhar_placar(tela, pontos)
        else:
            telas.desenhar_game_over(tela, pontos)

        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()