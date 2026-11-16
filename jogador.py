import pygame
from config import PISTAS, ALTURA, FPS

# Constantes do jogador. Ficam aqui porque o config.py é do A.
LARGURA_JOGADOR = 40
ALTURA_JOGADOR = 60
ALTURA_DESLIZANDO = 30  # altura do entregador abaixado
COR_JOGADOR = (240, 170, 40)  # laranja: o entregador
COR_PERSEGUIDOR = (200, 60, 60)  # vermelho: o cliente com fome
COR_SOMBRA = (35, 35, 35)  # sombra no chão durante o pulo
DISTANCIA_LONGE = 100  # perseguidor quase fora da tela (sem batidas)
DISTANCIA_PERTO = 10  # perseguidor colado no entregador (depois de uma batida)
TEMPO_PARA_ESQUECER = 5 * FPS  # 5 segundos sem bater zera as batidas
TEMPO_INVENCIVEL = FPS  # 1 segundo sem poder bater de novo
FORCA_PULO = 15  # velocidade para cima no início do pulo (pixels por quadro)
GRAVIDADE = 0.8  # quanto a velocidade do pulo diminui a cada quadro
TEMPO_DESLIZE = 2 * FPS // 3  # o deslize dura 2/3 de segundo


class Jogador:
    def __init__(self):
        self.pista = 1  # 0 = esquerda, 1 = meio, 2 = direita
        self.rect = pygame.Rect(0, 0, LARGURA_JOGADOR, ALTURA_JOGADOR)  # retângulo do entregador (no chão)
        self.rect.centerx = PISTAS[self.pista]  # centro do retângulo no centro da pista
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

    def esquerda(self):
        if self.pista > 0:  # só anda se não estiver na pista da esquerda
            self.pista -= 1

    def direita(self):
        if self.pista < len(PISTAS) - 1:  # só anda se não estiver na pista da direita
            self.pista += 1

    def pular(self):
        if not self.pulando:  # não dá para pular de novo no ar
            self.deslizando = False  # pular cancela o deslize
            self.pulando = True
            self.velocidade_pulo = FORCA_PULO

    def deslizar(self):
        # No ar, apertar ↓ faz ele cair rápido (como nos jogos do gênero).
        if self.pulando:
            self.velocidade_pulo = -FORCA_PULO
        # No chão, abaixa e começa a contar o tempo do deslize.
        else:
            self.deslizando = True
            self.tempo_deslize = TEMPO_DESLIZE

    def tratar_tecla(self, tecla):
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
        if self.pulando and (tipo == "cone" or tipo == "lombada" or tipo == "buraco"):
            return True
        if self.deslizando and tipo == "barreira":
            return True
        return False

    def bater(self):
        # Ainda piscando da batida anterior: ignora, senão o mesmo obstáculo
        # contaria uma batida por quadro enquanto estiver encostado.
        if self.invencivel > 0:
            return False

        # Conta a batida, traz o perseguidor para perto e zera os contadores.
        self.batidas += 1
        self.distancia_perseguidor = DISTANCIA_PERTO
        self.tempo_desde_batida = 0
        self.invencivel = TEMPO_INVENCIVEL
        return True  # avisa o main que a batida valeu (útil para tocar som)

    def perdeu(self):
        return self.batidas >= 2  # 2 batidas seguidas = game over

    def atualizar(self):
        self.rect.centerx = PISTAS[self.pista]  # leva o entregador para a pista atual

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
        self.perseguidor.centerx = self.rect.centerx
        self.perseguidor.top = self.chao + self.distancia_perseguidor

    def desenhar(self, tela):
        pygame.draw.rect(tela, COR_PERSEGUIDOR, self.perseguidor)  # cliente com fome

        # No ar, desenha uma sombra no chão para dar a ideia de altura.
        if self.pulando:
            sombra = pygame.Rect(0, 0, LARGURA_JOGADOR, 12)
            sombra.centerx = self.rect.centerx
            sombra.centery = self.chao
            pygame.draw.ellipse(tela, COR_SOMBRA, sombra)

        # Copia o retângulo e sobe a cópia pela altura do pulo, só para desenhar.
        # O self.rect fica no chão, porque é ele que o C usa na colisão.
        desenho = self.rect.copy()
        desenho.bottom = self.chao - int(self.altura_pulo)

        # Enquanto invencível, o entregador pisca: some a cada 5 quadros.
        if (self.invencivel // 5) % 2 == 0:
            pygame.draw.rect(tela, COR_JOGADOR, desenho)
