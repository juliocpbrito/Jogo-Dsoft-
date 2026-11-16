import pygame
from config import LARGURA, ALTURA, FPS, COR_FUNDO, COR_LINHA
import telas
from jogador import Jogador  # NOVO (B): a classe do entregador


# SUGESTÃO (B) para o A: rua em perspectiva, estreita no alto e larga embaixo.
# Larguras escolhidas para que, na altura do entregador, as pistas fiquem
# exatamente nos x de PISTAS (por isso o jogador.py não muda nada).
LARGURA_RUA_TOPO = 160  # largura da rua no alto da tela (lá longe)
LARGURA_RUA_BASE = 536  # largura da rua no pé da tela (mais larga que a janela)
COR_CALCADA = (90, 120, 80)  # verde: o que fica fora da rua


def desenhar_pista(tela):
    tela.fill(COR_CALCADA)
    meio = LARGURA // 2  # a rua é centralizada
    topo = LARGURA_RUA_TOPO // 2  # meia largura no alto
    base = LARGURA_RUA_BASE // 2  # meia largura embaixo

    # O asfalto é um trapézio: 2 cantos no alto e 2 embaixo.
    pygame.draw.polygon(tela, COR_FUNDO, [(meio - topo, 0), (meio + topo, 0), (meio + base, ALTURA), (meio - base, ALTURA)])

    # As 2 linhas que separam as pistas ficam a 1/3 da largura de cada borda,
    # tanto no alto quanto embaixo; ligando os pontos, elas "convergem" ao longe.
    pygame.draw.line(tela, COR_LINHA, (meio - topo // 3, 0), (meio - base // 3, ALTURA), 3)
    pygame.draw.line(tela, COR_LINHA, (meio + topo // 3, 0), (meio + base // 3, ALTURA), 3)


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Delivery Surfers")
    relogio = pygame.time.Clock()

    estado = "menu"  # "menu", "jogando" ou "game_over"
    pontos = 0
    jogador = Jogador()  # NOVO (B): cria o entregador

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
                        jogador = Jogador()  # NOVO (B): entregador novo a cada partida
                elif evento.key == pygame.K_ESCAPE and estado == "jogando":
                    estado = "game_over"  # TEMPORÁRIO: simula perder o jogo
                # NOVO (B): durante o jogo, as setas controlam o entregador
                elif estado == "jogando":
                    jogador.tratar_tecla(evento.key)  # ← → trocam de pista, ↑ pula, ↓ desliza
                    if evento.key == pygame.K_b:  # TEMPORÁRIO (B): simula batida até o C terminar
                        jogador.bater()

        # 2) Atualização e 3) Desenho, de acordo com o estado
        if estado == "menu":
            telas.desenhar_menu(tela)
        elif estado == "jogando":
            pontos += 1  # TEMPORÁRIO: depois vira distância percorrida
            desenhar_pista(tela)
            # NOVO (B): move, desenha e confere se perdeu
            jogador.atualizar()
            jogador.desenhar(tela)
            if jogador.perdeu():
                estado = "game_over"
            telas.desenhar_placar(tela, pontos)
        else:
            telas.desenhar_game_over(tela, pontos)

        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
