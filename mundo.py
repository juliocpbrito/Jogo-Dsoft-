# Arquivo: mundo.py
# Autor: Henri (C)
# Uso de IA: código escrito com auxílio do Claude (Anthropic) e revisado,
# testado e entendido pelo autor. Detalhes na seção "Uso de IA" do README.
#
# O mundo: obstáculos que vêm pela rua numa pista sorteada.
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

# Cor provisória de cada tipo, até os desenhos ficarem prontos.
COR_TIPO = {"carro": (200, 40, 40), "cone": (250, 120, 20), "buraco": (20, 20, 20)}


class Obstaculo:
    def __init__(self, tipo, pista, d):
        self.tipo = tipo      # "carro", "cone" ou "buraco"
        self.pista = pista    # 0 = esquerda, 1 = meio, 2 = direita
        self.d = d            # profundidade da ponta mais perto do jogador
        self.comprimento = COMPRIMENTO[tipo]
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
        # Provisório: um retângulo na pegada do obstáculo. Os desenhos vêm depois.
        pygame.draw.rect(tela, COR_TIPO[self.tipo], self.rect)


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

    def desenhar(self, tela, na_frente):
        """Desenha os obstáculos do mais longe para o mais perto.
        na_frente=False: os que estão atrás do jogador (chamar antes de desenhar o jogador).
        na_frente=True: os que já passaram por ele (chamar depois, para ficarem por cima)."""
        for obstaculo in sorted(self.obstaculos, key=lambda o: -o.d):
            if (obstaculo.d < D_JOGADOR) == na_frente:
                obstaculo.desenhar(tela)
