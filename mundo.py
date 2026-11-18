# Arquivo: mundo.py
# Autor: Henri (C)
# Uso de IA: código escrito com auxílio do Claude (Anthropic) e revisado,
# testado e entendido pelo autor. Detalhes na seção "Uso de IA" do README.
#
# O mundo: obstáculos que vêm pela rua numa pista sorteada e a colisão com o jogador.
#
# Cada obstáculo vive na mesma "profundidade" d que o cenario.py usa:
# d grande = longe (alto da tela), d pequeno = perto (embaixo). A cada quadro o d
# diminui, então o obstáculo desce pela tela e cresce, junto com a rua.
#
# Contrato com o resto do grupo (combinado no plano):
#   - todo obstáculo tem um rect (a "pegada" dele no chão, em pixels da tela)
#     e um método descer(velocidade);
#   - o jogador tem um rect e o método desvia(tipo), que diz se ele passa sem bater.

import random
import pygame
from config import ALTURA, Y_CHAO, Y_HORIZONTE, VELOCIDADE_RUA, x_da_pista, escala, y_da_profundidade

# Profundidade dos pés do entregador (a conta de y_da_profundidade ao contrário, para y = Y_CHAO).
D_JOGADOR = (ALTURA - Y_HORIZONTE) / (Y_CHAO - Y_HORIZONTE)  # cerca de 1.12

D_SURGIMENTO = 4.0       # onde os obstáculos nascem: logo acima do topo da tela
D_SUMIR = 0.9            # mais perto que isso já saiu por baixo da tela
ESPACO_ENTRE_FILEIRAS = 1.2  # distância (em profundidade) entre uma fileira de obstáculos e a próxima

# Medidas de cada tipo: largura em pixels (na altura do entregador) e comprimento em profundidade.
LARGURA = {"carro": 104, "cone": 34, "buraco": 96}
COMPRIMENTO = {"carro": 0.3, "cone": 0.05, "buraco": 0.1}
VELOCIDADE_EXTRA_CARRO = 0.5  # o carro vem na contramão: anda 50% mais rápido que a rua

# Cores (vermelho, verde, azul)
CORES_CARRO = [(200, 40, 40), (40, 90, 190), (235, 235, 235), (40, 40, 45), (230, 180, 30), (60, 150, 80)]
COR_VIDRO = (40, 60, 90)
COR_PNEU = (20, 20, 20)
COR_FAROL = (255, 240, 150)
COR_PARACHOQUE = (90, 90, 95)
COR_PLACA = (240, 240, 240)
COR_CONE = (250, 120, 20)
COR_FAIXA_CONE = (250, 250, 250)
COR_BASE_CONE = (30, 30, 30)
COR_BURACO = (25, 25, 25)
COR_BURACO_FUNDO = (10, 10, 10)
COR_BORDA_BURACO = (95, 90, 85)


def escurecer(cor, fator):
    """A mesma cor mais escura (fator 1.0 = igual, 0.0 = preto)."""
    return (int(cor[0] * fator), int(cor[1] * fator), int(cor[2] * fator))


class Obstaculo:
    def __init__(self, tipo, pista, d):
        self.tipo = tipo      # "carro", "cone" ou "buraco"
        self.pista = pista    # 0 = esquerda, 1 = meio, 2 = direita
        self.d = d            # profundidade da ponta mais perto do jogador
        self.comprimento = COMPRIMENTO[tipo]
        self.ja_bateu = False  # cada obstáculo só pode causar uma batida
        self.cor = random.choice(CORES_CARRO)  # só usada pelo carro
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.atualizar_rect()

    def atualizar_rect(self):
        """O rect é a pegada do obstáculo no chão: da ponta de perto (embaixo) até a de longe (em cima)."""
        y_perto = y_da_profundidade(self.d)
        y_longe = y_da_profundidade(self.d + self.comprimento)
        largura = LARGURA[self.tipo] * escala(y_perto)  # mais longe = mais estreito
        self.rect = pygame.Rect(0, 0, round(largura), max(1, round(y_perto - y_longe)))
        self.rect.bottom = round(y_perto)
        self.rect.centerx = round(x_da_pista(self.pista, y_perto))

    def descer(self, velocidade):
        """Anda na direção do jogador. Cone e buraco ficam parados na rua; o carro vem mais rápido."""
        if self.tipo == "carro":
            velocidade = velocidade * (1 + VELOCIDADE_EXTRA_CARRO)
        self.d -= velocidade
        self.atualizar_rect()

    def saiu_da_tela(self):
        return self.d + self.comprimento < D_SUMIR

    def desenhar(self, tela):
        if self.d > D_SURGIMENTO + 0.5:  # ainda acima da tela
            return
        if self.tipo == "carro":
            self.desenhar_carro(tela)
        elif self.tipo == "cone":
            self.desenhar_cone(tela)
        else:
            self.desenhar_buraco(tela)

    # --- Desenhos (sprites feitos com formas do pygame, sem imagens de fora) ---

    def desenhar_carro(self, tela):
        """Carro na contramão, visto de cima e de frente: teto em perspectiva e a frente com faróis."""
        y0 = y_da_profundidade(self.d)  # chão na frente do carro
        y1 = y_da_profundidade(self.d + self.comprimento)  # chão na traseira
        s0, s1 = escala(y0), escala(y1)  # tamanho na frente e atrás
        x0, x1 = x_da_pista(self.pista, y0), x_da_pista(self.pista, y1)
        meia0, meia1 = LARGURA["carro"] / 2 * s0, LARGURA["carro"] / 2 * s1  # meia largura
        alto0, alto1 = 46 * s0, 46 * s1  # altura do carro

        def em_cima(fracao):
            """Ponto de cima do carro a uma fração do comprimento (0 = frente, 1 = traseira): (x, y, meia largura)."""
            x = x0 + (x1 - x0) * fracao
            y = (y0 - alto0) + ((y1 - alto1) - (y0 - alto0)) * fracao
            meia = meia0 + (meia1 - meia0) * fracao
            return x, y, meia

        def faixa(f_a, f_b, cor, aperto=1.0):
            """Pinta um pedaço do teto entre as frações f_a e f_b. aperto < 1 deixa mais estreito."""
            xa, ya, ma = em_cima(f_a)
            xb, yb, mb = em_cima(f_b)
            pygame.draw.polygon(tela, cor, [(xa - ma * aperto, ya), (xa + ma * aperto, ya),
                                            (xb + mb * aperto, yb), (xb - mb * aperto, yb)])

        faixa(0, 1, self.cor)                           # teto inteiro (capô, cabine e porta-malas)
        faixa(0.28, 0.42, COR_VIDRO, 0.85)              # para-brisa
        faixa(0.42, 0.78, escurecer(self.cor, 0.85), 0.8)  # teto da cabine
        faixa(0.78, 0.86, COR_VIDRO, 0.8)               # vidro de trás

        # Frente: um retângulo do chão até o capô.
        frente = pygame.Rect(0, 0, meia0 * 2, alto0)
        frente.bottomleft = (x0 - meia0, y0)
        pygame.draw.rect(tela, escurecer(self.cor, 0.75), frente, border_radius=max(1, int(6 * s0)))
        # Pneus aparecendo embaixo, nos cantos.
        for lado in (-1, 1):
            pneu = pygame.Rect(0, 0, 16 * s0, 12 * s0)
            pneu.midbottom = (x0 + lado * (meia0 - 10 * s0), y0)
            pygame.draw.rect(tela, COR_PNEU, pneu)
        # Para-choque, faróis e placa.
        pygame.draw.rect(tela, COR_PARACHOQUE, (x0 - meia0, y0 - 16 * s0, meia0 * 2, 7 * s0))
        for lado in (-1, 1):
            pygame.draw.circle(tela, COR_FAROL, (x0 + lado * (meia0 - 14 * s0), y0 - 30 * s0), max(1, 7 * s0))
        placa = pygame.Rect(0, 0, 26 * s0, 9 * s0)
        placa.center = (x0, y0 - 24 * s0)
        pygame.draw.rect(tela, COR_PLACA, placa)

    def desenhar_cone(self, tela):
        """Cone de trânsito laranja com faixa branca e base preta."""
        y = y_da_profundidade(self.d + self.comprimento / 2)  # meio da pegada no chão
        s = escala(y)
        x = x_da_pista(self.pista, y)
        pygame.draw.rect(tela, COR_BASE_CONE, (x - 18 * s, y - 6 * s, 36 * s, 6 * s))  # base quadrada
        pygame.draw.polygon(tela, COR_CONE, [(x - 13 * s, y - 6 * s), (x + 13 * s, y - 6 * s), (x, y - 48 * s)])
        # Faixa branca: um trapézio no meio do cone.
        pygame.draw.polygon(tela, COR_FAIXA_CONE, [(x - 8.5 * s, y - 21 * s), (x + 8.5 * s, y - 21 * s),
                                                   (x + 6 * s, y - 29 * s), (x - 6 * s, y - 29 * s)])

    def desenhar_buraco(self, tela):
        """Buraco no asfalto: uma elipse escura deitada no chão, com borda de asfalto quebrado."""
        y_perto = y_da_profundidade(self.d)
        y_longe = y_da_profundidade(self.d + self.comprimento)
        s = escala(y_perto)
        x = x_da_pista(self.pista, (y_perto + y_longe) / 2)
        largura = LARGURA["buraco"] * s
        borda = pygame.Rect(0, 0, largura, y_perto - y_longe)
        borda.midbottom = (x, y_perto)
        pygame.draw.ellipse(tela, COR_BORDA_BURACO, borda)
        pygame.draw.ellipse(tela, COR_BURACO, borda.inflate(-8 * s, -borda.height * 0.2))
        pygame.draw.ellipse(tela, COR_BURACO_FUNDO, borda.inflate(-30 * s, -borda.height * 0.5))


class Mundo:
    def __init__(self):
        self.obstaculos = []  # obstáculos na rua agora
        self.velocidade = VELOCIDADE_RUA  # quanto a rua anda por quadro
        self.proxima_fileira = D_SURGIMENTO  # profundidade em que nasce a próxima fileira

    def criar_fileira(self):
        """Sorteia 1 ou 2 pistas com obstáculo. Sempre sobra pelo menos uma pista sem carro."""
        quantos = random.choice([1, 1, 2])  # 1 obstáculo é mais comum que 2
        pistas = random.sample([0, 1, 2], quantos)  # sample: sorteia sem repetir
        for pista in pistas:
            tipo = random.choice(["carro", "cone", "buraco"])
            self.obstaculos.append(Obstaculo(tipo, pista, D_SURGIMENTO))

    def atualizar(self):
        # Cada fileira nasce lá longe; a "linha" da próxima fileira anda junto com a rua.
        self.proxima_fileira -= self.velocidade
        if self.proxima_fileira <= D_SURGIMENTO:
            self.criar_fileira()
            self.proxima_fileira += ESPACO_ENTRE_FILEIRAS

        for obstaculo in self.obstaculos:
            obstaculo.descer(self.velocidade)
        # Fica só com os que ainda aparecem na tela.
        self.obstaculos = [o for o in self.obstaculos if not o.saiu_da_tela()]

    def colisao(self, jogador):
        """Devolve True se o jogador levou uma batida neste quadro."""
        for obstaculo in self.obstaculos:
            if obstaculo.ja_bateu or not obstaculo.rect.colliderect(jogador.rect):
                continue
            if jogador.desvia(obstaculo.tipo):  # pulou o cone ou o buraco
                continue
            obstaculo.ja_bateu = True  # este obstáculo não bate de novo
            if jogador.bater():  # False se o jogador ainda estiver piscando da batida anterior
                return True
        return False

    def desenhar(self, tela, na_frente):
        """Desenha os obstáculos do mais longe para o mais perto.
        na_frente=False: os que estão atrás do jogador (chamar antes de desenhar o jogador).
        na_frente=True: os que já passaram por ele (chamar depois, para ficarem por cima)."""
        for obstaculo in sorted(self.obstaculos, key=lambda o: -o.d):
            if (obstaculo.d < D_JOGADOR) == na_frente:
                obstaculo.desenhar(tela)
