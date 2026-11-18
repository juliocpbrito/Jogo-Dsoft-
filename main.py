import pygame
from config import (LARGURA, ALTURA, FPS, COR_FUNDO, COR_LINHA, COR_CALCADA,
                    LARGURA_RUA_TOPO, LARGURA_RUA_BASE)  # os parênteses permitem quebrar a linha
import telas             # nosso telas.py: usamos como telas.desenhar_menu(...)
import recorde           # nosso recorde.py: carregar() e salvar()
from jogador import Jogador  # a classe do entregador, feita pelo B

METROS_POR_QUADRO = 0.2  # quanto a distância aumenta a cada quadro (a 60 quadros por segundo: 12 m/s)


def desenhar_pista(tela):
    tela.fill(COR_CALCADA)  # pinta tudo de verde (a calçada); a rua é desenhada por cima
    meio = LARGURA // 2             # x do meio da tela
    topo = LARGURA_RUA_TOPO // 2    # meia largura da rua no alto
    base = LARGURA_RUA_BASE // 2    # meia largura da rua embaixo

    # O asfalto é um trapézio: 2 cantos no alto e 2 embaixo (uma lista de 4 pontos (x, y)).
    pygame.draw.polygon(tela, COR_FUNDO, [(meio - topo, 0), (meio + topo, 0),
                                          (meio + base, ALTURA), (meio - base, ALTURA)])

    # As 2 linhas que separam as pistas ficam a 1/3 de cada lado do meio, no alto e embaixo.
    # Como a rua é mais estreita no alto, as linhas se aproximam ao longe (a perspectiva).
    pygame.draw.line(tela, COR_LINHA, (meio - topo // 3, 0), (meio - base // 3, ALTURA), 3)
    pygame.draw.line(tela, COR_LINHA, (meio + topo // 3, 0), (meio + base // 3, ALTURA), 3)


def main():
    pygame.init()  # liga os módulos do PyGame
    tela = pygame.display.set_mode((LARGURA, ALTURA))  # cria a janela e devolve a tela onde desenhamos
    pygame.display.set_caption("Delivery Surfers")     # título da janela
    relogio = pygame.time.Clock()  # relógio para controlar a velocidade do jogo

    estado = "menu"  # em qual tela estamos: "menu", "jogando", "pausado" ou "game_over"
    distancia = 0.0  # metros percorridos (número decimal)
    melhor = recorde.carregar()  # lê o recorde salvo no arquivo
    jogador = Jogador()  # cria o entregador

    rodando = True
    while rodando:  # o loop principal: cada volta é um quadro do jogo
        # 1) Eventos: o que o jogador fez
        for evento in pygame.event.get():  # lista de tudo o que aconteceu desde o último quadro
            if evento.type == pygame.QUIT:  # clicou no X da janela
                rodando = False
            elif evento.type == pygame.KEYDOWN:  # apertou uma tecla (uma vez por aperto)
                if evento.key == pygame.K_SPACE:
                    if estado == "menu" or estado == "game_over":  # só começa partida nessas telas
                        estado = "jogando"
                        distancia = 0.0  # zera a distância
                        jogador = Jogador()  # entregador novo a cada partida
                elif evento.key == pygame.K_p:  # tecla P: pausa e continua
                    if estado == "jogando":
                        estado = "pausado"
                    elif estado == "pausado":
                        estado = "jogando"
                elif evento.key == pygame.K_ESCAPE and estado == "jogando":
                    estado = "game_over"  # TEMPORÁRIO: simula perder o jogo
                elif estado == "jogando":  # qualquer outra tecla, durante o jogo
                    jogador.tratar_tecla(evento.key)  # o jogador decide o que fazer: ← → pista, ↑ pula, ↓ desliza
                    if evento.key == pygame.K_b:  # TEMPORÁRIO: simula batida até o C terminar
                        jogador.bater()

        # 2) Atualização e 3) Desenho, de acordo com o estado
        if estado == "menu":
            telas.desenhar_menu(tela, melhor)
        elif estado == "jogando":
            distancia += METROS_POR_QUADRO  # anda mais um pouquinho
            desenhar_pista(tela)   # primeiro o fundo...
            jogador.atualizar()    # ...move o jogador (pulo, deslize, perseguidor)...
            jogador.desenhar(tela) # ...e desenha por cima
            if jogador.perdeu():   # 2 batidas seguidas
                estado = "game_over"
            telas.desenhar_placar(tela, distancia)  # o placar por último, para ficar por cima de tudo
        elif estado == "pausado":
            # Nada se move: desenha o jogo parado com o aviso por cima
            desenhar_pista(tela)
            jogador.desenhar(tela)
            telas.desenhar_placar(tela, distancia)
            telas.desenhar_pausa(tela)
        else:  # estado == "game_over"
            # Se bateu o recorde, guarda no arquivo. Depois de salvar, melhor fica igual
            # à distância, então a condição deixa de valer e só salva uma vez.
            if int(distancia) > melhor:
                melhor = int(distancia)
                recorde.salvar(melhor)
            telas.desenhar_game_over(tela, distancia, melhor)

        pygame.display.flip()  # mostra na janela o quadro que acabamos de desenhar
        relogio.tick(FPS)      # espera o tempo certo para rodar a 60 quadros por segundo

    pygame.quit()  # desliga o PyGame ao sair do loop


if __name__ == "__main__":  # só roda main() quando executamos este arquivo diretamente
    main()