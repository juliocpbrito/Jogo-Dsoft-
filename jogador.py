# Arquivo: jogador.py
# Autor: B (lógica do jogador); visual do entregador e do cliente (métodos desenhar_*)
# feitos com auxílio do Claude (Anthropic) e integrados por Julio (A).
# Uso de IA: código gerado/ajustado com IA, revisado e testado pelo grupo.
# Detalhes na seção "Uso de IA" do README.
import math
import pygame
from config import PISTAS, ALTURA, FPS

# Constantes do jogador. Ficam aqui porque o config.py é do A.
LARGURA_JOGADOR = 40
ALTURA_JOGADOR = 60
ALTURA_DESLIZANDO = 30  # altura do entregador abaixado
COR_JOGADOR = (240, 170, 40)  # laranja: o entregador
COR_PERSEGUIDOR = (200, 60, 60)  # vermelho: o cliente com fome
COR_SOMBRA = (35, 35, 35)  # sombra no chão
COR_CAPACETE = (40, 40, 50)  # capacete do entregador
COR_MOCHILA = (20, 160, 70)  # mochila de entrega (verde)
COR_MOCHILA_TAMPA = (90, 210, 120)  # tampa da mochila (verde mais claro)
COR_SHORTS = (40, 50, 90)  # shorts do entregador
COR_PELE_ENTREGADOR = (200, 150, 110)  # pernas e braços do entregador
COR_HAVAIANAS = (245, 245, 245)  # havaianas brancas
COR_PELE = (240, 200, 160)  # pele do cliente
COR_CAMISA_CLIENTE = (200, 60, 60)  # camisa do cliente (vermelha)
COR_CALCA_CLIENTE = (70, 50, 40)  # calça do cliente
COR_OLHO = (255, 255, 255)
COR_PELE_BRAVO = (235, 150, 130)  # rosto do cliente, meio vermelho de raiva
COR_CABELO = (90, 55, 30)  # cabelo bagunçado
COR_GUARDANAPO = (245, 245, 245)  # guardanapo no colarinho
COR_MOLHO = (220, 110, 30)  # mancha de molho
COR_TALHER = (200, 200, 210)  # faca e garfo
COR_LINGUA = (210, 70, 90)
COR_BABA = (150, 200, 255)  # baba azulada, para aparecer no fundo cinza
COR_CONTORNO = (20, 20, 20)  # preto para olhos, boca e sobrancelhas
DISTANCIA_LONGE = 100  # perseguidor quase fora da tela (sem batidas)
DISTANCIA_PERTO = 10  # perseguidor colado no entregador (depois de uma batida)
TEMPO_PARA_ESQUECER = 5 * FPS  # 5 segundos sem bater zera as batidas
TEMPO_INVENCIVEL = FPS  # 1 segundo sem poder bater de novo
FORCA_PULO = 15  # velocidade para cima no início do pulo (pixels por quadro)
GRAVIDADE = 0.8  # quanto a velocidade do pulo diminui a cada quadro
TEMPO_DESLIZE = 2 * FPS // 3  # o deslize dura 2/3 de segundo
VELOCIDADE_TROCA = 12  # pixels por quadro na troca de pista (160 pixels entre pistas: cerca de 13 quadros, 0,2 s)
VELOCIDADE_CLIENTE = 6  # o cliente acompanha o entregador de lado mais devagar, então fica um pouco atrás
INCLINACAO = 4  # pixels que o corpo se inclina para o lado ao trocar de pista


class Jogador:
    """O entregador e o cliente que o persegue: posição, pulo, deslize, batidas e desenho."""
    def __init__(self):
        """Cria o entregador na pista do meio, sem batidas, com o cliente bem longe."""
        self.pista = 1  # 0 = esquerda, 1 = meio, 2 = direita
        self.rect = pygame.Rect(0, 0, LARGURA_JOGADOR, ALTURA_JOGADOR)  # retângulo do entregador (no chão)
        self.rect.centerx = PISTAS[self.pista]  # centro do retângulo no centro da pista
        self.x = float(PISTAS[self.pista])  # posição horizontal de verdade (decimal), que anda até a pista de destino
        self.direcao = 0  # -1 indo para a esquerda, 1 para a direita, 0 parado numa pista
        self.x_cliente = float(PISTAS[self.pista])  # posição horizontal do cliente, que vem atrás
        self.chao = ALTURA - 120  # y dos pés do entregador; sobra espaço embaixo para o perseguidor
        self.rect.bottom = self.chao

        self.batidas = 0  # quantas batidas seguidas ele levou
        self.tempo_desde_batida = 0  # quadros desde a última batida
        self.invencivel = 0  # quadros que faltam para poder bater de novo
        self.distancia_perseguidor = DISTANCIA_LONGE  # pixels entre o entregador e o cliente

        self.pulando = False  # está no ar?
        self.altura_pulo = 0  # quantos pixels acima do chão ele está
        self.velocidade_pulo = 0  # positivo = subindo, negativo = descendo

        self.deslizando = False  # está abaixado?
        self.tempo_deslize = 0  # quadros que faltam para levantar

        self.perseguidor = pygame.Rect(0, 0, LARGURA_JOGADOR, 50)  # retângulo do cliente com fome

        # Texto da mochila: criado uma vez só aqui, porque renderizar fonte a cada quadro é lento.
        fonte = pygame.font.Font(None, 14)  # fonte padrão do pygame, tamanho 14
        self.texto_mochila = fonte.render("RANGO", True, (255, 255, 255))  # letras brancas (nome inventado: sem marca de app real)

        self.quadro = 0  # conta os quadros desde o início; usado para animar as pernas

    def esquerda(self):
        """Passa para a pista da esquerda (se não estiver na borda)."""
        if self.pista > 0:  # só anda se não estiver na pista da esquerda
            self.pista -= 1

    def direita(self):
        """Passa para a pista da direita (se não estiver na borda)."""
        if self.pista < len(PISTAS) - 1:  # só anda se não estiver na pista da direita
            self.pista += 1

    def pular(self):
        """Começa um pulo. Não pula de novo se já estiver no ar."""
        if not self.pulando:  # não dá para pular de novo no ar
            self.deslizando = False  # pular cancela o deslize
            self.pulando = True
            self.velocidade_pulo = FORCA_PULO

    def deslizar(self):
        # No ar, apertar ↓ faz ele cair rápido (como nos jogos do gênero).
        """No chão, abaixa por um tempo; no ar, faz o entregador cair rápido."""
        if self.pulando:
            self.velocidade_pulo = -FORCA_PULO
        # No chão, abaixa e começa a contar o tempo do deslize.
        else:
            self.deslizando = True
            self.tempo_deslize = TEMPO_DESLIZE

    def tratar_tecla(self, tecla):
        """Recebe uma tecla (setas ou A, D, W, S) e chama a ação certa."""
        if tecla == pygame.K_LEFT or tecla == pygame.K_a:
            self.esquerda()
        elif tecla == pygame.K_RIGHT or tecla == pygame.K_d:
            self.direita()
        elif tecla == pygame.K_UP or tecla == pygame.K_w:
            self.pular()
        elif tecla == pygame.K_DOWN or tecla == pygame.K_s:
            self.deslizar()

    def desvia(self, tipo):
        # Diz se o entregador passa pelo obstáculo sem bater.
        # Pulando: passa por cima de cone, lombada e buraco (mas não de carro).
        # Deslizando: passa por baixo de barreira (se o C criar esse tipo).
        """Diz se o entregador passa por um obstáculo do tipo dado sem bater (pulando ou deslizando)."""
        if self.pulando and (tipo == "cone" or tipo == "lombada" or tipo == "buraco"):
            return True
        if self.deslizando and tipo == "barreira":
            return True
        return False

    def bater(self):
        # Ainda piscando da batida anterior: ignora, senão o mesmo obstáculo
        # contaria uma batida por quadro enquanto estiver encostado.
        """Conta uma batida, aproxima o cliente e liga a invencibilidade. Devolve False se ainda estiver invencível."""
        if self.invencivel > 0:
            return False

        # Conta a batida, traz o perseguidor para perto e zera os contadores.
        self.batidas += 1
        self.distancia_perseguidor = DISTANCIA_PERTO
        self.tempo_desde_batida = 0
        self.invencivel = TEMPO_INVENCIVEL
        return True  # avisa o main que a batida valeu (útil para tocar som)

    def perdeu(self):
        """True quando o entregador levou 2 batidas seguidas (fim de jogo)."""
        return self.batidas >= 2  # 2 batidas seguidas = game over

    def atualizar(self):
        """Avança um quadro: troca de pista, pulo, deslize, contagem de batidas e posição do cliente."""
        self.quadro += 1  # mais um quadro de animação

        # Troca de pista com animação: 'pista' é o destino; x anda até lá, VELOCIDADE_TROCA por quadro.
        alvo = PISTAS[self.pista]  # x do centro da pista de destino
        if abs(self.x - alvo) <= VELOCIDADE_TROCA:  # falta menos que um passo: chegou
            self.x = alvo
            self.direcao = 0
        else:
            self.direcao = 1 if alvo > self.x else -1  # para que lado está indo
            self.x += self.direcao * VELOCIDADE_TROCA
        self.rect.centerx = round(self.x)  # o retângulo (usado nas colisões) acompanha o desenho

        # Pulo: a altura muda pela velocidade, e a gravidade vai freando a subida
        # até ele começar a descer. Quando chega no chão, o pulo acaba.
        if self.pulando:
            self.altura_pulo += self.velocidade_pulo
            self.velocidade_pulo -= GRAVIDADE
            if self.altura_pulo <= 0:
                self.altura_pulo = 0
                self.pulando = False

        # Deslize: conta o tempo e levanta quando acaba.
        if self.deslizando:
            self.tempo_deslize -= 1
            if self.tempo_deslize <= 0:
                self.deslizando = False

        # O retângulo fica baixinho enquanto desliza; os pés continuam no chão.
        if self.deslizando:
            self.rect.height = ALTURA_DESLIZANDO
        else:
            self.rect.height = ALTURA_JOGADOR
        self.rect.bottom = self.chao

        self.tempo_desde_batida += 1  # mais um quadro sem bater
        if self.invencivel > 0:
            self.invencivel -= 1

        # Se passou tempo suficiente sem bater, o cliente "desiste" um pouco:
        # as batidas zeram e ele vai se afastando 1 pixel por quadro.
        if self.tempo_desde_batida > TEMPO_PARA_ESQUECER:
            self.batidas = 0
            if self.distancia_perseguidor < DISTANCIA_LONGE:
                self.distancia_perseguidor += 1

        # O perseguidor fica na mesma pista, logo atrás (embaixo) do entregador.
        # O cliente também anda até a posição do entregador, só que mais devagar.
        if abs(self.x_cliente - self.x) <= VELOCIDADE_CLIENTE:
            self.x_cliente = self.x
        elif self.x > self.x_cliente:
            self.x_cliente += VELOCIDADE_CLIENTE
        else:
            self.x_cliente -= VELOCIDADE_CLIENTE
        self.perseguidor.centerx = round(self.x_cliente)
        self.perseguidor.top = self.chao + self.distancia_perseguidor

    def desenhar(self, tela):
        # Sombra no chão, sempre: no ar ela mostra a altura do pulo.
        """Desenha a sombra, o cliente e o entregador (que pisca enquanto está invencível)."""
        sombra = pygame.Rect(0, 0, LARGURA_JOGADOR, 12)
        sombra.centerx = self.rect.centerx
        sombra.centery = self.chao
        pygame.draw.ellipse(tela, COR_SOMBRA, sombra)

        # O cliente é desenhado antes, para o entregador ficar na frente dele.
        self.desenhar_cliente(tela)

        # Enquanto invencível, o entregador pisca: some a cada 5 quadros.
        if (self.invencivel // 5) % 2 == 0:
            self.desenhar_entregador(tela)

    # feito com Claude
    def desenhar_entregador(self, tela):
        """Desenha o entregador: pernas, braços, jaqueta, mochila e capacete, em pé, pulando ou deslizando."""
        cx = self.rect.centerx  # centro horizontal das pernas
        cc = cx + INCLINACAO * self.direcao  # centro do corpo: se inclina para o lado em que está indo
        pes = self.chao - int(self.altura_pulo)  # y dos pés (sobe junto com o pulo)

        # Balanço das pernas e braços: seno vai de -1 a 1 conforme o quadro passa.
        balanco = int(math.sin(self.quadro * 0.4) * 5)

        if self.deslizando:
            # Abaixado: corpo largo e baixo, com a mochila nas costas.
            self.desenhar_perna(tela, cx - 14, pes - 8, pes, 10)  # perna esquerda
            self.desenhar_perna(tela, cx + 4, pes - 8, pes, 10)  # perna direita
            pygame.draw.ellipse(tela, COR_JOGADOR, (cc - 20, pes - 24, 40, 20))  # corpo deitado
            pygame.draw.rect(tela, COR_MOCHILA, (cc - 16, pes - 30, 32, 14), border_radius=3)  # mochila
            pygame.draw.rect(tela, COR_MOCHILA_TAMPA, (cc - 16, pes - 30, 32, 5), border_radius=3)  # tampa
            pygame.draw.circle(tela, COR_CAPACETE, (cc, pes - 22), 8)  # capacete
            return

        if self.pulando:
            # No ar: pernas abertas e braços para cima.
            self.desenhar_perna(tela, cx - 14, pes - 16, pes, 10)  # perna esquerda
            self.desenhar_perna(tela, cx + 4, pes - 16, pes, 10)  # perna direita
            braco_y = pes - 56  # mãos para cima
        else:
            # Correndo: uma perna sobe enquanto a outra desce.
            self.desenhar_perna(tela, cx - 12, pes - 20 + balanco, pes, 9)  # perna esquerda
            self.desenhar_perna(tela, cx + 3, pes - 20 - balanco, pes, 9)  # perna direita
            braco_y = pes - 36 + balanco  # braços balançando

        # Braços (atrás do corpo, ficam só nas laterais).
        pygame.draw.rect(tela, COR_JOGADOR, (cc - 20, braco_y, 6, 16), border_radius=3)
        pygame.draw.rect(tela, COR_JOGADOR, (cc + 14, braco_y - 2 * (balanco // 2), 6, 16), border_radius=3)

        # Corpo: jaqueta laranja.
        pygame.draw.rect(tela, COR_JOGADOR, (cc - 14, pes - 44, 28, 28), border_radius=4)

        # Mochila de entrega: caixa grande nas costas, com tampa mais clara.
        pygame.draw.rect(tela, COR_MOCHILA, (cc - 17, pes - 48, 34, 30), border_radius=4)
        pygame.draw.rect(tela, COR_MOCHILA_TAMPA, (cc - 17, pes - 48, 34, 8), border_radius=4)
        # Nome escrito na mochila, centralizado no meio da caixa.
        tela.blit(self.texto_mochila, self.texto_mochila.get_rect(center=(cc, pes - 30)))

        # Capacete (visto de trás).
        pygame.draw.circle(tela, COR_CAPACETE, (cc, pes - 54), 10)

    # feito com Claude
    def desenhar_perna(self, tela, x, topo, base, largura):
        # Uma perna do entregador: shorts em cima, perna de fora e havaiana branca no pé.
        """Desenha uma perna do entregador: shorts, perna de fora e havaiana."""
        altura_shorts = min(9, base - topo)  # em perna curta o shorts ocupa tudo
        pygame.draw.rect(tela, COR_PELE_ENTREGADOR, (x, topo, largura, base - topo))  # perna
        pygame.draw.rect(tela, COR_SHORTS, (x - 1, topo, largura + 2, altura_shorts))  # shorts
        pygame.draw.rect(tela, COR_HAVAIANAS, (x - 1, base - 3, largura + 2, 3))  # havaiana branca

    # feito com Claude
    def desenhar_cliente(self, tela):
        """Desenha o cliente faminto que persegue o entregador, com rosto bravo e talheres."""
        topo = self.perseguidor.top
        # Só desenha se o cliente já apareceu na tela.
        if topo > ALTURA:
            return

        # Quando está colado no entregador, o cliente treme de raiva (±1 pixel).
        tremor = 0
        if self.distancia_perseguidor <= DISTANCIA_PERTO + 20:
            tremor = int(math.sin(self.quadro * 1.8) * 1.5)
        cx = self.perseguidor.centerx + tremor

        balanco = int(math.sin(self.quadro * 0.4 + 1) * 4)  # balanço das pernas
        aceno = int(math.sin(self.quadro * 0.25) * 3)  # braços subindo e descendo

        # Pernas correndo, com tênis.
        pygame.draw.rect(tela, COR_CALCA_CLIENTE, (cx - 12, topo + 34 + balanco, 9, 14))
        pygame.draw.rect(tela, COR_CALCA_CLIENTE, (cx + 3, topo + 34 - balanco, 9, 14))
        pygame.draw.rect(tela, COR_CONTORNO, (cx - 13, topo + 46 + balanco, 11, 4))  # tênis esquerdo
        pygame.draw.rect(tela, COR_CONTORNO, (cx + 2, topo + 46 - balanco, 11, 4))  # tênis direito

        # Corpo: camisa vermelha, com barriguinha.
        pygame.draw.rect(tela, COR_CAMISA_CLIENTE, (cx - 15, topo + 17, 30, 22), border_radius=6)

        # Guardanapo preso no colarinho (triângulo branco) com uma mancha de molho.
        pygame.draw.polygon(tela, COR_GUARDANAPO, [(cx - 8, topo + 18), (cx + 8, topo + 18), (cx, topo + 31)])
        pygame.draw.circle(tela, COR_MOLHO, (cx + 2, topo + 24), 2)

        # Braços levantados com talheres: faca na esquerda, garfo na direita.
        mao_e = (cx - 23, topo + 3 - aceno)  # posição da mão esquerda
        mao_d = (cx + 23, topo + 3 + aceno)  # posição da mão direita
        pygame.draw.line(tela, COR_CAMISA_CLIENTE, (cx - 13, topo + 22), mao_e, 5)  # manga esquerda
        pygame.draw.line(tela, COR_CAMISA_CLIENTE, (cx + 13, topo + 22), mao_d, 5)  # manga direita
        pygame.draw.circle(tela, COR_PELE, mao_e, 3)  # mão esquerda
        pygame.draw.circle(tela, COR_PELE, mao_d, 3)  # mão direita
        # Faca (lâmina cinza).
        pygame.draw.line(tela, COR_TALHER, mao_e, (mao_e[0], mao_e[1] - 15), 3)
        # Garfo (cabo + base + 3 dentes).
        pygame.draw.line(tela, COR_TALHER, mao_d, (mao_d[0], mao_d[1] - 13), 2)
        for dx in (-3, 0, 3):  # os três dentes
            pygame.draw.line(tela, COR_TALHER, (mao_d[0] + dx, mao_d[1] - 13), (mao_d[0] + dx, mao_d[1] - 18), 1)

        # Cabeça: rosto vermelho de raiva.
        pygame.draw.circle(tela, COR_PELE_BRAVO, (cx, topo + 9), 12)
        # Cabelo bagunçado: faixa marrom em cima e tufos.
        pygame.draw.ellipse(tela, COR_CABELO, (cx - 12, topo - 3, 24, 11))
        for dx in (-7, 0, 7):
            pygame.draw.line(tela, COR_CABELO, (cx + dx, topo - 1), (cx + dx + dx // 3, topo - 6), 2)
        # Olhos arregalados com pupila.
        pygame.draw.circle(tela, COR_OLHO, (cx - 5, topo + 8), 4)
        pygame.draw.circle(tela, COR_OLHO, (cx + 5, topo + 8), 4)
        pygame.draw.circle(tela, COR_CONTORNO, (cx - 5, topo + 9), 2)
        pygame.draw.circle(tela, COR_CONTORNO, (cx + 5, topo + 9), 2)
        # Sobrancelhas grossas e bravas (inclinadas para o centro).
        pygame.draw.line(tela, COR_CONTORNO, (cx - 10, topo + 2), (cx - 2, topo + 5), 3)
        pygame.draw.line(tela, COR_CONTORNO, (cx + 10, topo + 2), (cx + 2, topo + 5), 3)
        # Boca aberta gritando, com dentes em cima e língua.
        pygame.draw.ellipse(tela, COR_CONTORNO, (cx - 6, topo + 13, 12, 8))
        pygame.draw.rect(tela, COR_OLHO, (cx - 4, topo + 13, 8, 2))  # dentes
        pygame.draw.ellipse(tela, COR_LINGUA, (cx - 3, topo + 18, 6, 3))  # língua
        # Baba pingando do canto da boca: sobe e desce com o tempo.
        baba = int(abs(math.sin(self.quadro * 0.15)) * 4)
        pygame.draw.line(tela, COR_BABA, (cx + 6, topo + 18), (cx + 6, topo + 21 + baba), 2)
        pygame.draw.circle(tela, COR_BABA, (cx + 6, topo + 22 + baba), 2)

        # Barriga roncando: dois tracinhos que piscam ao lado da barriga.
        if (self.quadro // 8) % 2 == 0:
            pygame.draw.line(tela, COR_CONTORNO, (cx - 20, topo + 30), (cx - 17, topo + 28), 2)
            pygame.draw.line(tela, COR_CONTORNO, (cx + 20, topo + 30), (cx + 17, topo + 28), 2)