# Arquivo: mundo.py
# Autor: Henri (C)
# Uso de IA: código escrito com auxílio do Claude (Anthropic) e revisado,
# testado e entendido pelo autor. Detalhes na seção "Uso de IA" do README.
#
# O mundo: obstáculos que vêm pela rua numa pista sorteada, a colisão com o jogador
# as gorjetas (moedas) em fileiras para pegar e o capacete, que protege das batidas.
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
from config import ALTURA, FPS, Y_CHAO, Y_HORIZONTE, VELOCIDADE_RUA, x_da_pista, escala, y_da_profundidade

# Profundidade dos pés do entregador (a conta de y_da_profundidade ao contrário, para y = Y_CHAO).
D_JOGADOR = (ALTURA - Y_HORIZONTE) / (Y_CHAO - Y_HORIZONTE)  # cerca de 1.12

D_SURGIMENTO = 4.0       # onde os obstáculos nascem: logo acima do topo da tela
D_SUMIR = 0.9            # mais perto que isso já saiu por baixo da tela
ESPACO_ENTRE_FILEIRAS = 1.2  # distância (em profundidade) entre uma fileira de obstáculos e a próxima

# Medidas de cada tipo: largura em pixels (na altura do entregador) e comprimento em profundidade.
LARGURA = {"carro": 104, "cone": 34, "buraco": 96, "barreira": 120}
COMPRIMENTO = {"carro": 0.16, "cone": 0.05, "buraco": 0.1, "barreira": 0.05}
VELOCIDADE_EXTRA_CARRO = 0.0  # 0.0 = o carro anda junto com a rua. Em Obstaculo.descer a velocidade do carro é
                              # velocidade * (1 + 0.0) = velocidade. Antes era 0.5 (50% mais rápido): o carro
                              # alcançava as moedas e os cones que estavam na frente dele e passava por cima

# Cores (vermelho, verde, azul)
COR_LANTERNA = (210, 30, 30)       # lanterna traseira vermelha
COR_CROMADO = (205, 205, 210)      # para-choque cromado do Fusca
COR_PLACA_AZUL = (30, 70, 170)     # faixa azul da placa Mercosul
# Cores comuns dos carros no Brasil: prata, branco, preto, vermelho, cinza e azul.
CORES_COMUNS = [(192, 194, 198), (240, 240, 240), (35, 35, 40), (190, 40, 40), (110, 112, 118), (45, 85, 170)]
# Modelos de carro populares no Brasil, desenhados com formas simples. Cada um tem:
#   largura: fração da largura máxima (o Fusca é mais estreito, o Renegade tem a largura toda)
#   altura: altura do carro em pixels
#   cortes: onde terminam o porta-malas, o vidro de trás, o teto e o para-brisa (frações do comprimento)
#   lanterna: o formato da lanterna traseira
#   cores: cores possíveis para o modelo
MODELOS = {
    "fusca":    {"largura": 0.84, "altura": 40, "cortes": (0.24, 0.36, 0.64, 0.78), "lanterna": "redonda",
                 "cores": [(235, 220, 160), (70, 125, 175), (215, 180, 40), (150, 190, 150), (200, 60, 50)]},
    "gol":      {"largura": 0.90, "altura": 44, "cortes": (0.05, 0.21, 0.63, 0.77), "lanterna": "alta",
                 "cores": CORES_COMUNS},
    "celta":    {"largura": 0.86, "altura": 42, "cortes": (0.04, 0.20, 0.60, 0.76), "lanterna": "alta",
                 "cores": CORES_COMUNS},
    "fox":      {"largura": 0.90, "altura": 50, "cortes": (0.04, 0.22, 0.68, 0.80), "lanterna": "alta",
                 "cores": CORES_COMUNS},
    "golf":     {"largura": 0.96, "altura": 44, "cortes": (0.04, 0.21, 0.62, 0.77), "lanterna": "fina",
                 "cores": CORES_COMUNS},
    "renegade": {"largura": 1.00, "altura": 56, "cortes": (0.03, 0.19, 0.74, 0.86), "lanterna": "quadrada",
                 "cores": CORES_COMUNS + [(60, 110, 60), (235, 150, 40)]},
}
LETRAS_PLACA = "ABCDEFGHJKLMNPRSTUVWXYZ"  # letras que aparecem nas placas
_textos_placa = {}  # placas já desenhadas, para não renderizar o texto a cada quadro


def nova_placa():
    """Sorteia uma placa no padrão Mercosul: 3 letras, 1 número, 1 letra e 2 números (ex.: BRA1D23)."""
    letras = "".join(random.choice(LETRAS_PLACA) for _ in range(3))
    return letras + str(random.randint(0, 9)) + random.choice(LETRAS_PLACA) + str(random.randint(0, 99)).zfill(2)


def texto_placa(placa, largura, altura):
    """Imagem com as letras da placa no tamanho pedido. Guarda as já feitas (renderizar fonte é lento)."""
    chave = (placa, int(largura), int(altura))
    if chave not in _textos_placa:
        letras = pygame.font.Font(None, 20).render(placa, True, COR_PNEU)  # texto num tamanho fixo
        _textos_placa[chave] = pygame.transform.smoothscale(letras, (int(largura), int(altura)))  # ajusta ao tamanho
    return _textos_placa[chave]
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
COR_BARREIRA_1 = (230, 50, 40)     # listras da barreira de obra: vermelho...
COR_BARREIRA_2 = (245, 245, 245)   # ...e branco
COR_PE_BARREIRA = (70, 70, 75)
ALTURA_BARREIRA = 46  # altura da barra (pixels acima do chão): o entregador em pé bate, abaixado passa


def escurecer(cor, fator):
    """A mesma cor mais escura (fator 1.0 = igual, 0.0 = preto)."""
    return (int(cor[0] * fator), int(cor[1] * fator), int(cor[2] * fator))

# Velocidade crescente: a rua começa em VELOCIDADE_RUA e acelera até o dobro.
ACELERACAO = 1 / (80 * FPS)  # quanto o 'fator' de velocidade sobe a cada quadro. 80 * FPS = quadros em 80 segundos
                             # (80 * 60 = 4800). Somar 1/4800 por quadro dá +1 depois de 4800 quadros:
                             # o fator dobra em 80 segundos...
VELOCIDADE_MAXIMA = 2.2      # ...e para de subir em 2.2 (a rua anda 2,2 vezes mais rápido que no começo).
                             # Sai de 1 e chega em 2.2 em 1.2 * 80 = 96 segundos

# Dificuldade: 'nivel' vai de 0 (começo) a 1 (velocidade máxima). Com ele, aparecem mais obstáculos por fileira
# e tipos mais difíceis. Os tipos novos entram nestes níveis:
NIVEL_BARREIRA = 0.15  # a barreira (precisa deslizar) só aparece quando o nível passa de 0.15 (uns 15 segundos)
NIVEL_CARRO = 0.35     # o carro (precisa trocar de pista) só aparece quando o nível passa de 0.35 (uns 35 segundos)
CHANCE_DUAS_INICIAL = 0.1  # chance (de 0 a 1) de a fileira ter 2 obstáculos no começo: 10%...
CHANCE_DUAS_FINAL = 0.7    # ...e na velocidade máxima: 70%. No meio do caminho o valor fica entre os dois

# Gorjetas: fileiras de moedas numa pista livre.
MOEDAS_POR_FILEIRA = 5
ESPACO_ENTRE_MOEDAS = 0.15  # 5 moedas ocupam 0.75 de profundidade: cabem antes da próxima fileira (1.2)
CHANCE_GORJETA = 0.45       # 0.45 = 45% das fileiras de obstáculos vêm com uma fileira de moedas
TAMANHO_MOEDA = 26          # diâmetro em pixels, na altura do entregador
COR_MOEDA = (250, 200, 40)
COR_MOEDA_BORDA = (190, 130, 20)
COR_MOEDA_BRILHO = (255, 245, 180)
COR_SOMBRA_MOEDA = (35, 35, 35)

# Capacete (power-up): aparece de vez em quando numa pista livre. Pegou: 10 segundos sem levar batida.
CHANCE_CAPACETE = 0.02        # 0.02 = 2% das fileiras trazem um capacete (raro: cerca de 1 a cada 50 segundos)
TEMPO_PROTECAO = 10 * FPS     # quanto tempo a proteção dura, em quadros
COR_CAPACETE_ITEM = (40, 120, 230)
COR_VISEIRA = (170, 220, 255)
COR_BOLHA = (120, 200, 255)


class Obstaculo:
    """Um obstáculo na rua (carro, cone, buraco ou barreira), com posição em profundidade e retângulo de colisão."""
    def __init__(self, tipo, pista, d):
        """Cria o obstáculo do tipo dado na pista e profundidade dadas. Se for carro, sorteia modelo, cor e placa."""
        self.tipo = tipo      # "carro", "cone" ou "buraco"
        self.pista = pista    # 0 = esquerda, 1 = meio, 2 = direita
        self.d = d            # profundidade da ponta mais perto do jogador
        self.comprimento = COMPRIMENTO[tipo]
        self.ja_bateu = False  # cada obstáculo só pode causar uma batida
        self.modelo = "gol"   # só usados pelo carro; os outros tipos ignoram
        self.cor = (255, 255, 255)
        self.placa = ""
        if tipo == "carro":
            self.modelo = random.choice(list(MODELOS))  # sorteia o modelo: fusca, gol, celta, fox, golf ou renegade
            self.cor = random.choice(MODELOS[self.modelo]["cores"])  # e uma cor própria do modelo
            self.placa = nova_placa()  # cada carro com a sua placa
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
        """True quando o obstáculo já passou do jogador e saiu por baixo da tela."""
        return self.d + self.comprimento < D_SUMIR

    def desenhar(self, tela):
        """Desenha o obstáculo de acordo com o tipo."""
        if self.d > D_SURGIMENTO + 0.5:  # ainda acima da tela
            return
        if self.tipo == "carro":
            self.desenhar_carro(tela)
        elif self.tipo == "cone":
            self.desenhar_cone(tela)
        elif self.tipo == "barreira":
            self.desenhar_barreira(tela)
        else:
            self.desenhar_buraco(tela)

    # --- Desenhos (sprites feitos com formas do pygame, sem imagens de fora) ---

    def desenhar_carro(self, tela):
        """Carro parado na pista, visto de trás e de cima: lanternas, placa e vidro de trás perto de nós;
        teto, para-brisa e capô mais longe. O modelo (Fusca, Gol...) muda o formato, a cor e as lanternas."""
        m = MODELOS[self.modelo]
        y0 = y_da_profundidade(self.d)  # chão na traseira do carro (a ponta que está mais perto de nós)
        y1 = y_da_profundidade(self.d + self.comprimento)  # chão na frente do carro (mais longe)
        s0, s1 = escala(y0), escala(y1)  # tamanho perto e longe
        x0, x1 = x_da_pista(self.pista, y0), x_da_pista(self.pista, y1)
        meia0 = LARGURA["carro"] * m["largura"] / 2 * s0  # meia largura do carro perto (cada modelo tem a sua)
        meia1 = LARGURA["carro"] * m["largura"] / 2 * s1  # e longe
        alto0, alto1 = m["altura"] * s0, m["altura"] * s1  # altura do carro perto e longe
        cor = self.cor

        def em_cima(fracao):
            """Ponto do alto do carro a uma fração do comprimento (0 = traseira, 1 = capô): (x, y, meia largura)."""
            x = x0 + (x1 - x0) * fracao
            y = (y0 - alto0) + ((y1 - alto1) - (y0 - alto0)) * fracao
            meia = meia0 + (meia1 - meia0) * fracao
            return x, y, meia

        def faixa(f_a, f_b, cor_faixa, aperto=1.0):
            """Pinta um pedaço do alto do carro entre as frações f_a e f_b. aperto < 1 deixa mais estreito."""
            xa, ya, ma = em_cima(f_a)
            xb, yb, mb = em_cima(f_b)
            pygame.draw.polygon(tela, cor_faixa, [(xa - ma * aperto, ya), (xa + ma * aperto, ya),
                                                  (xb + mb * aperto, yb), (xb - mb * aperto, yb)])

        # Cortes do alto do carro, em frações do comprimento: fim do porta-malas, do vidro de trás,
        # do teto e do para-brisa. O resto até a frente é o capô.
        t1, t2, t3, t4 = m["cortes"]
        faixa(0, 1, cor)                                   # o alto inteiro na cor do carro
        faixa(t1, t2, COR_VIDRO, 0.82)                     # vidro de trás
        faixa(t2, t3, escurecer(cor, 0.88), 0.8)           # teto
        faixa(t3, t4, COR_VIDRO, 0.82)                     # para-brisa
        if self.modelo == "fusca":                         # tampa do motor com as grades de ventilação
            for f in (0.04, 0.09, 0.14, 0.19):
                faixa(f, f + 0.012, escurecer(cor, 0.55), 0.7)

        # Traseira: um retângulo do chão até a borda do porta-malas.
        traseira = pygame.Rect(0, 0, meia0 * 2, alto0)
        traseira.bottomleft = (x0 - meia0, y0)
        pygame.draw.rect(tela, escurecer(cor, 0.78), traseira, border_radius=max(1, int(6 * s0)))
        # Pneus aparecendo embaixo, nos cantos.
        for lado in (-1, 1):
            pneu = pygame.Rect(0, 0, 16 * s0, 12 * s0)
            pneu.midbottom = (x0 + lado * (meia0 - 8 * s0), y0)
            pygame.draw.rect(tela, COR_PNEU, pneu)
        # Para-choque (no Fusca é cromado, mais claro).
        cor_para = COR_CROMADO if self.modelo == "fusca" else COR_PARACHOQUE
        pygame.draw.rect(tela, cor_para, (x0 - meia0, y0 - 15 * s0, meia0 * 2, 7 * s0))

        # Lanternas traseiras: o formato é uma das coisas que identificam o modelo.
        estilo = m["lanterna"]
        for lado in (-1, 1):
            lx = x0 + lado * (meia0 - 11 * s0)  # centro da lanterna deste lado
            if estilo == "redonda":    # Fusca: lanterna redonda pequena
                pygame.draw.circle(tela, COR_LANTERNA, (lx, y0 - 28 * s0), max(1, 5 * s0))
            elif estilo == "fina":     # Golf: lanterna comprida e fina, no alto
                pygame.draw.rect(tela, COR_LANTERNA, (min(lx - 11 * s0, lx + 11 * s0), y0 - alto0 + 3 * s0, 22 * s0, 5 * s0))
            elif estilo == "alta":     # Gol, Celta e Fox: lanterna vertical nos cantos
                pygame.draw.rect(tela, COR_LANTERNA, (lx - 4 * s0, y0 - 40 * s0, 8 * s0, 18 * s0))
            else:                      # Renegade: lanterna quadrada
                pygame.draw.rect(tela, COR_LANTERNA, (lx - 6 * s0, y0 - 46 * s0, 12 * s0, 12 * s0))

        # Placa brasileira (padrão Mercosul): fundo branco, faixa azul em cima e letras pretas.
        placa = pygame.Rect(0, 0, 34 * s0, 14 * s0)
        placa.center = (x0, y0 - 25 * s0)
        pygame.draw.rect(tela, COR_PLACA, placa)
        pygame.draw.rect(tela, COR_PLACA_AZUL, (placa.x, placa.y, placa.width, max(1, 4 * s0)))
        pygame.draw.rect(tela, COR_PNEU, placa, 1)  # contorno fino
        if placa.width >= 26:  # só escreve as letras se a placa estiver grande o bastante para ler
            texto = texto_placa(self.placa, placa.width - 4, max(1, placa.height - 6))
            tela.blit(texto, texto.get_rect(center=(placa.centerx, placa.centery + 2 * s0)))

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

    def desenhar_barreira(self, tela):
        """Barreira de obra: uma barra listrada sobre dois pés. Só dá para passar deslizando (tecla ↓)."""
        y = y_da_profundidade(self.d + self.comprimento / 2)
        s = escala(y)
        x = x_da_pista(self.pista, y)
        meia = LARGURA["barreira"] / 2 * s
        topo = y - (ALTURA_BARREIRA + 14) * s  # parte de cima da barra
        for lado in (-1, 1):  # os dois pés
            pygame.draw.rect(tela, COR_PE_BARREIRA, (x + lado * (meia - 8 * s) - 3 * s, topo, 6 * s, y - topo))
        # Barra com 6 listras alternando vermelho e branco.
        largura_listra = 2 * meia / 6
        for i in range(6):
            cor = COR_BARREIRA_1 if i % 2 == 0 else COR_BARREIRA_2
            pygame.draw.rect(tela, cor, (x - meia + i * largura_listra, topo, largura_listra + 1, 14 * s))

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


class Gorjeta:
    """Uma moeda flutuando um pouco acima da rua. Desce junto com a rua, como o cone."""

    def __init__(self, pista, d):
        """Cria uma moeda na pista e profundidade dadas."""
        self.pista = pista
        self.d = d
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.atualizar_rect()

    def atualizar_rect(self):
        """Recalcula o retângulo da moeda (tamanho e posição) para a profundidade atual."""
        y = y_da_profundidade(self.d)
        tamanho = max(1, round(TAMANHO_MOEDA * escala(y)))
        self.rect = pygame.Rect(0, 0, tamanho, tamanho)
        self.rect.bottom = round(y)  # a pegada no chão, para comparar com o rect do jogador
        self.rect.centerx = round(x_da_pista(self.pista, y))

    def descer(self, velocidade):
        """Move a moeda na direção do jogador, junto com a rua."""
        self.d -= velocidade
        self.atualizar_rect()

    def saiu_da_tela(self):
        """True quando a moeda já saiu por baixo da tela."""
        return self.d < D_SUMIR

    def desenhar(self, tela):
        """Desenha a moeda flutuando, com sombra no chão."""
        if self.d > D_SURGIMENTO + 0.5:
            return
        y = y_da_profundidade(self.d)
        s = escala(y)
        x = x_da_pista(self.pista, y)
        raio = TAMANHO_MOEDA / 2 * s
        centro = (x, y - 22 * s)  # a moeda flutua 22 pixels acima do chão
        sombra = pygame.Rect(0, 0, raio * 1.6, raio * 0.5)
        sombra.center = (x, y)
        pygame.draw.ellipse(tela, COR_SOMBRA_MOEDA, sombra)
        pygame.draw.circle(tela, COR_MOEDA_BORDA, centro, raio)
        pygame.draw.circle(tela, COR_MOEDA, centro, raio * 0.78)
        pygame.draw.circle(tela, COR_MOEDA_BRILHO, (centro[0] - raio * 0.3, centro[1] - raio * 0.3), max(1, raio * 0.2))


class Capacete:
    """O power-up: um capacete azul flutuando na rua. Desce junto com a rua, como a moeda."""

    def __init__(self, pista, d):
        """Cria um capacete (power-up) na pista e profundidade dadas."""
        self.pista = pista
        self.d = d
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.atualizar_rect()

    def atualizar_rect(self):
        """Recalcula o retângulo do capacete para a profundidade atual."""
        y = y_da_profundidade(self.d)
        tamanho = max(1, round(34 * escala(y)))
        self.rect = pygame.Rect(0, 0, tamanho, tamanho)
        self.rect.bottom = round(y)
        self.rect.centerx = round(x_da_pista(self.pista, y))

    def descer(self, velocidade):
        """Move o capacete na direção do jogador, junto com a rua."""
        self.d -= velocidade
        self.atualizar_rect()

    def saiu_da_tela(self):
        """True quando o capacete já saiu por baixo da tela."""
        return self.d < D_SUMIR

    def desenhar(self, tela):
        """Desenha o capacete azul flutuando, com sombra no chão."""
        if self.d > D_SURGIMENTO + 0.5:
            return
        y = y_da_profundidade(self.d)
        s = escala(y)
        x = x_da_pista(self.pista, y)
        cy = y - 26 * s  # flutua acima do chão
        sombra = pygame.Rect(0, 0, 30 * s, 8 * s)
        sombra.center = (x, y)
        pygame.draw.ellipse(tela, COR_SOMBRA_MOEDA, sombra)
        casco = pygame.Rect(0, 0, 34 * s, 30 * s)
        casco.center = (x, cy)
        pygame.draw.ellipse(tela, COR_CAPACETE_ITEM, casco)  # o casco
        pygame.draw.rect(tela, COR_CAPACETE_ITEM, (x - 17 * s, cy, 34 * s, 8 * s))  # a aba de baixo
        pygame.draw.rect(tela, COR_VISEIRA, (x - 11 * s, cy - 2 * s, 22 * s, 8 * s), border_radius=max(1, int(3 * s)))


class Mundo:
    """A rua: guarda os obstáculos, moedas e capacetes, controla a velocidade e a dificuldade e detecta colisões."""
    def __init__(self):
        """Começa uma rua vazia, na velocidade inicial e sem proteção."""
        self.obstaculos = []  # obstáculos na rua agora
        self.gorjetas = []  # moedas na rua agora
        self.moedas_pegas = 0  # quantas moedas o jogador pegou na partida
        self.capacetes = []  # capacetes (power-up) na rua agora
        self.protecao = 0  # quadros que faltam de proteção do capacete (0 = sem proteção)
        self.velocidade = VELOCIDADE_RUA  # quanto a rua anda por quadro (cresce com o tempo)
        self.fator = 1.0  # quantas vezes mais rápido que no começo
        self.proxima_fileira = D_SURGIMENTO  # profundidade em que nasce a próxima fileira

    def nivel(self):
        """Dificuldade de 0 (começo) a 1 (velocidade máxima)."""
        # self.fator vai de 1 a VELOCIDADE_MAXIMA (2.2). Subtrair 1 e dividir pela distância total (2.2 - 1)
        # transforma esse intervalo em 0 a 1. Exemplos: fator 1.0 -> 0; fator 1.6 -> 0.5; fator 2.2 -> 1.
        return (self.fator - 1) / (VELOCIDADE_MAXIMA - 1)

    def criar_fileira(self):
        """Sorteia 1 ou 2 pistas com obstáculo. Sempre sobra pelo menos uma pista sem carro."""
        nivel = self.nivel()  # dificuldade de agora, de 0 a 1 (variável local: só existe dentro desta função)
        # Quanto mais difícil, maior a chance de 2 obstáculos na mesma fileira.
        # Interpolação linear: começa em CHANCE_DUAS_INICIAL e anda até CHANCE_DUAS_FINAL conforme o nível.
        # Nível 0 -> 0.1; nível 0.5 -> 0.1 + 0.6 * 0.5 = 0.4; nível 1 -> 0.1 + 0.6 = 0.7
        chance_duas = CHANCE_DUAS_INICIAL + (CHANCE_DUAS_FINAL - CHANCE_DUAS_INICIAL) * nivel
        # random.random() sorteia um decimal entre 0 e 1. Se for menor que chance_duas, são 2 obstáculos; senão, 1.
        # (com chance_duas = 0.4, o sorteio cai abaixo de 0.4 em 40% das vezes)
        quantos = 2 if random.random() < chance_duas else 1
        pistas = random.sample([0, 1, 2], quantos)  # sample: sorteia sem repetir
        # Os tipos mais difíceis só entram depois de um tempo de jogo.
        tipos = ["cone", "buraco"]  # começa só com os fáceis: dá para passar pulando
        if nivel >= NIVEL_BARREIRA:  # já passou do nível da barreira?
            tipos.append("barreira")  # append coloca um item no fim da lista: agora a barreira pode ser sorteada
        if nivel >= NIVEL_CARRO:  # já passou do nível do carro?
            tipos.append("carro")  # agora o carro também pode ser sorteado
        for pista in pistas:
            tipo = random.choice(tipos)  # sorteia um tipo só entre os que já estão liberados
            self.obstaculos.append(Obstaculo(tipo, pista, D_SURGIMENTO))

        # Às vezes, uma fileira de moedas numa pista que ficou livre.
        livres = [p for p in [0, 1, 2] if p not in pistas]
        if random.random() < CHANCE_GORJETA:
            pista = random.choice(livres)
            livres.remove(pista)  # essa pista agora tem moedas
            for i in range(MOEDAS_POR_FILEIRA):
                self.gorjetas.append(Gorjeta(pista, D_SURGIMENTO + i * ESPACO_ENTRE_MOEDAS))

        # Raramente, um capacete numa pista que ainda está livre (sem obstáculo e sem moedas).
        if livres and random.random() < CHANCE_CAPACETE:
            self.capacetes.append(Capacete(random.choice(livres), D_SURGIMENTO))

    def atualizar(self):
        # Acelera um pouquinho a cada quadro, até o limite. min() devolve o menor dos dois.
        """Avança um quadro: acelera, cria novas fileiras, move tudo na direção do jogador e remove o que saiu da tela."""
        self.fator = min(self.fator + ACELERACAO, VELOCIDADE_MAXIMA)
        self.velocidade = VELOCIDADE_RUA * self.fator

        # Cada fileira nasce lá longe; a "linha" da próxima fileira anda junto com a rua.
        self.proxima_fileira -= self.velocidade
        if self.proxima_fileira <= D_SURGIMENTO:
            self.criar_fileira()
            self.proxima_fileira += ESPACO_ENTRE_FILEIRAS

        for obstaculo in self.obstaculos:
            obstaculo.descer(self.velocidade)
        # Fica só com os que ainda aparecem na tela.
        self.obstaculos = [o for o in self.obstaculos if not o.saiu_da_tela()]

        for gorjeta in self.gorjetas:
            gorjeta.descer(self.velocidade)
        self.gorjetas = [g for g in self.gorjetas if not g.saiu_da_tela()]

        for capacete in self.capacetes:
            capacete.descer(self.velocidade)
        self.capacetes = [c for c in self.capacetes if not c.saiu_da_tela()]
        if self.protecao > 0:
            self.protecao -= 1  # a proteção vai acabando

    def pegar_gorjetas(self, jogador):
        """Tira da rua as moedas que encostaram no jogador. Devolve quantas ele pegou neste quadro."""
        pegas = [g for g in self.gorjetas if g.rect.colliderect(jogador.rect)]
        self.gorjetas = [g for g in self.gorjetas if g not in pegas]
        self.moedas_pegas += len(pegas)
        return len(pegas)

    def colisao(self, jogador):
        """Devolve True se o jogador levou uma batida neste quadro."""
        for obstaculo in self.obstaculos:
            if obstaculo.ja_bateu or not obstaculo.rect.colliderect(jogador.rect):
                continue
            if jogador.desvia(obstaculo.tipo):  # pulou o cone ou o buraco
                continue
            if self.protecao > 0:  # de capacete: atravessa sem contar batida
                obstaculo.ja_bateu = True
                continue
            obstaculo.ja_bateu = True  # este obstáculo não bate de novo
            if jogador.bater():  # False se o jogador ainda estiver piscando da batida anterior
                return True
        return False

    def pegar_capacete(self, jogador):
        """Se o jogador encostou num capacete, liga a proteção e devolve True."""
        for capacete in self.capacetes:
            if capacete.rect.colliderect(jogador.rect):
                self.capacetes.remove(capacete)
                self.protecao = TEMPO_PROTECAO
                return True
        return False

    def desenhar_protecao(self, tela, jogador):
        """Bolha azul em volta do entregador enquanto o capacete protege. Pisca nos últimos 2 segundos."""
        if self.protecao <= 0:
            return
        if self.protecao < 2 * FPS and (self.protecao // 6) % 2 == 0:
            return  # piscando: avisa que vai acabar
        centro = (jogador.rect.centerx, jogador.chao - int(jogador.altura_pulo) - 30)
        bolha = pygame.Surface((96, 96), pygame.SRCALPHA)  # folha transparente para a bolha
        pygame.draw.circle(bolha, COR_BOLHA + (60,), (48, 48), 46)  # miolo bem transparente
        pygame.draw.circle(bolha, COR_BOLHA + (200,), (48, 48), 46, 3)  # contorno
        tela.blit(bolha, bolha.get_rect(center=centro))

    def desenhar(self, tela, na_frente):
        """Desenha obstáculos, moedas e capacetes do mais longe para o mais perto.
        na_frente=False: os que estão atrás do jogador (chamar antes de desenhar o jogador).
        na_frente=True: os que já passaram por ele (chamar depois, para ficarem por cima)."""
        for coisa in sorted(self.obstaculos + self.gorjetas + self.capacetes, key=lambda o: -o.d):
            if (coisa.d < D_JOGADOR) == na_frente:
                coisa.desenhar(tela)