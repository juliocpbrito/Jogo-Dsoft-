# Arquivo: main.py
# Autor: Julio (A)
# Uso de IA: código escrito com auxílio do Claude (Anthropic) e revisado,
# testado e entendido pelo autor. Detalhes na seção "Uso de IA" do README.
import pygame
from config import LARGURA, ALTURA, FPS
import cenario           # nosso cenario.py: a rua, os prédios, os postes (cenario.desenhar(...))
import telas             # nosso telas.py: usamos como telas.desenhar_menu(...)
import recorde           # nosso recorde.py: carregar() e salvar()
import audio             # nosso audio.py: música e efeitos sonoros
from jogador import Jogador  # a classe do entregador, feita pelo B
from mundo import Mundo      # obstáculos e colisão, feitos pelo C

METROS_POR_QUADRO = 0.2  # quanto a distância aumenta a cada quadro (a 60 quadros por segundo: 12 m/s)


def main():
    pygame.init()  # liga os módulos do PyGame
    tela = pygame.display.set_mode((LARGURA, ALTURA))  # cria a janela e devolve a tela onde desenhamos
    pygame.display.set_caption("Delivery Surfers")     # título da janela
    audio.iniciar()  # prepara a música e os efeitos (se os arquivos existirem)
    relogio = pygame.time.Clock()  # relógio para controlar a velocidade do jogo

    estado = "menu"  # em qual tela estamos: "menu", "jogando", "pausado" ou "game_over"
    distancia = 0.0  # metros percorridos (número decimal)
    deslocamento = 0.0  # quanto a rua já andou; faz as faixas descerem
    melhor = recorde.carregar()  # lê o recorde salvo no arquivo
    jogador = Jogador()  # cria o entregador
    mundo = Mundo()  # cria a rua com os obstáculos

    quadro_menu = 0  # conta os quadros no menu: faz o aviso de ESPAÇO piscar

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
                        deslocamento = 0.0  # a rua recomeça
                        audio.tocar_musica()  # música de fundo, do começo
                        jogador = Jogador()  # entregador novo a cada partida
                        mundo = Mundo()  # obstáculos novos a cada partida
                elif evento.key == pygame.K_p:  # tecla P: pausa e continua
                    if estado == "jogando":
                        estado = "pausado"
                        audio.pausar_musica()
                    elif estado == "pausado":
                        estado = "jogando"
                        audio.retomar_musica()
                elif estado == "jogando":  # qualquer outra tecla, durante o jogo
                    if (evento.key == pygame.K_UP or evento.key == pygame.K_w) and not jogador.pulando:
                        audio.tocar_efeito("pulo")  # só toca se ele realmente vai pular (não já no ar)
                    pista_antes = jogador.pista  # guarda a pista para ver se ela muda
                    jogador.tratar_tecla(evento.key)
                    if jogador.pista != pista_antes:  # trocou mesmo de faixa (não estava na borda)
                        audio.tocar_efeito("troca")  # som de troca de faixa

        # 2) Atualização e 3) Desenho, de acordo com o estado
        if estado == "menu":
            quadro_menu += 1
            telas.desenhar_menu(tela, melhor, quadro_menu)  # arte de capa, recorde e controles
        elif estado == "jogando":
            distancia += METROS_POR_QUADRO  # anda mais um pouquinho
            deslocamento += mundo.velocidade  # a rua anda junto: as faixas descem
            mundo.atualizar()      # obstáculos descem e novos aparecem
            jogador.atualizar()    # move o jogador (pulo, deslize, perseguidor)
            if mundo.colisao(jogador):  # bateu num obstáculo sem desviar
                audio.tocar_efeito("batida")
            cenario.desenhar(tela, deslocamento)   # primeiro o fundo...
            mundo.desenhar(tela, False)  # ...os obstáculos que ainda estão à frente do entregador...
            jogador.desenhar(tela) # ...o entregador...
            mundo.desenhar(tela, True)   # ...e os que já passaram por ele, por cima
            if jogador.perdeu():   # 2 batidas seguidas
                estado = "game_over"
                audio.parar_musica()
                audio.tocar_efeito("game_over")
            telas.desenhar_placar(tela, distancia)  # o placar por último, para ficar por cima de tudo
        elif estado == "pausado":
            # Nada se move: desenha o jogo parado com o aviso por cima
            cenario.desenhar(tela, deslocamento)  # mesmo deslocamento: a rua fica parada
            mundo.desenhar(tela, False)
            jogador.desenhar(tela)
            mundo.desenhar(tela, True)
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