# Arquivo: cenario.py
# Autor: Julio (A)
# Uso de IA: código escrito com auxílio do Claude (Anthropic) e revisado,
# testado e entendido pelo autor. Detalhes na seção "Uso de IA" do README.
#
# Desenha o cenário: uma rua de comunidade (favela) brasileira vista de cima e de trás,
# com casas de tijolo e de cores fortes, lajes, caixas d'água azuis, varais,
# postes com emaranhado de fios, calçada estreita e faixa de pedestres.
# Tudo "anda" com a variável deslocamento.
#
# A ideia da perspectiva: cada ponto do mundo tem uma profundidade d (1 = borda
# de baixo da tela, maior = mais longe). Tudo na tela fica dividido por d:
#   - a posição lateral:  x = MEIO + lado * distancia / d
#   - a altura na tela:   y = y_da_profundidade(d) - altura / d
# Quanto mais longe, mais perto do centro e menor.

import pygame
from config import LARGURA, ALTURA, COR_FUNDO, COR_LINHA, LARGURA_RUA_TOPO, LARGURA_RUA_BASE, y_da_profundidade

MEIO = LARGURA // 2                # x do meio da tela
META_RUA = LARGURA_RUA_BASE / 2    # meia largura da rua em d = 1 (268 pixels)
LARGURA_CALCADA = 60               # calçada estreita, em d = 1
DIST_PAREDE = META_RUA + LARGURA_CALCADA  # distância do meio até a parede das casas em d = 1
PROFUNDIDADE_BLOCO = 600           # quanto o telhado das casas se estende para dentro do quarteirão
PERIODO = 0.6                      # tamanho de uma laje da calçada, de um meio-fio ou de um traço
LARGURA_CASA = 0.3                 # largura de cada casa, em profundidade
LIMITE_PROFUNDIDADE = 4.0          # além disso já está acima da tela
PROFUNDIDADE_MINIMA = 0.4          # mais perto que isso está fora da tela (e evita dividir por zero)

# Cores (vermelho, verde, azul)
COR_CALCADA = (185, 180, 170)         # concreto
COR_CALCADA_ESCURA = (170, 165, 155)  # faixas alternadas: dão sensação de movimento
COR_MEIO_FIO_1 = (225, 222, 215)      # meio-fio de concreto, pintado de branco...
COR_MEIO_FIO_2 = (140, 138, 132)      # ...e já gasto
COR_VIDRO = (60, 85, 120)
COR_TIJOLO = (176, 92, 62)            # tijolo aparente
COR_JUNTA = (120, 62, 42)             # linhas entre os tijolos
COR_LAJE = (172, 168, 158)            # teto de concreto
COR_TELHA = (190, 105, 70)            # telhado de telha
COR_FIBRO = (140, 146, 150)           # telhado de fibrocimento
COR_CAIXA = (50, 120, 205)            # caixa d'água azul
COR_TAMPA_CAIXA = (150, 190, 240)
COR_FERRO = (60, 60, 60)              # ferros de espera (vergalhões) no alto das lajes
COR_TOLDO_1 = (200, 50, 50)
COR_TOLDO_2 = (245, 245, 245)
COR_POSTE = (90, 90, 95)
COR_FIO = (25, 25, 25)
COR_TRANSFORMADOR = (110, 120, 130)
# Cores das casas pintadas (tons fortes comuns nas comunidades brasileiras)
CORES_CASAS = [(60, 170, 170), (240, 200, 60), (235, 120, 150), (140, 200, 90),
               (80, 140, 210), (240, 150, 60), (230, 225, 215), (190, 120, 200)]
CORES_ROUPAS = [(230, 60, 80), (250, 210, 50), (60, 160, 230), (255, 255, 255), (90, 200, 120)]


def escurecer(cor, fator=0.8):
    """Devolve a mesma cor mais escura. fator 1.0 = igual, 0.0 = preto."""
    return (int(cor[0] * fator), int(cor[1] * fator), int(cor[2] * fator))


def sorteio(indice, k, n):
    """Um 'sorteio' sempre igual para a mesma casa: devolve um número de 0 a n-1.
    k diferencia os sorteios da mesma casa (um para a cor, outro para o telhado...)."""
    return ((indice * 7919 + k * 104729 + 13) * 2654435761) % 1000003 % n


def ponto(lado, d, lateral, altura):
    """Ponto do mundo na tela. lado: -1 esquerda, 1 direita.
    lateral = distância do meio da rua; altura = altura do chão (os dois em pixels de d = 1)."""
    x = MEIO + lado * lateral / d
    y = y_da_profundidade(d) - altura / d
    return (x, y)


def quadro_parede(tela, cor, lado, d1, d2, h1, h2):
    """Desenha um retângulo na parede da frente da casa: de profundidade d1 a d2 e de altura h1 a h2."""
    if d1 < PROFUNDIDADE_MINIMA:  # perto demais, está fora da tela
        return
    pontos = [ponto(lado, d1, DIST_PAREDE, h1), ponto(lado, d2, DIST_PAREDE, h1),
              ponto(lado, d2, DIST_PAREDE, h2), ponto(lado, d1, DIST_PAREDE, h2)]
    pygame.draw.polygon(tela, cor, pontos)


def desenhar_calcada(tela, deslocamento):
    """Chão de concreto, com lajes alternando de cor e descendo com o tempo."""
    tela.fill(COR_CALCADA)
    n = int(deslocamento // PERIODO)  # primeira laje que ainda aparece
    while n * PERIODO - deslocamento < LIMITE_PROFUNDIDADE:
        d_perto = max(n * PERIODO - deslocamento, 0.5)
        d_longe = (n + 1) * PERIODO - deslocamento
        if n % 2 == 0 and d_longe > d_perto:  # só as lajes pares são mais escuras
            y_baixo = int(y_da_profundidade(d_perto))
            y_cima = int(y_da_profundidade(d_longe))
            pygame.draw.rect(tela, COR_CALCADA_ESCURA, (0, y_cima, LARGURA, y_baixo - y_cima + 1))
        n += 1


def desenhar_casa(tela, lado, indice, d0):
    """Uma casa ao lado da rua. 'indice' decide cor, altura e detalhes (sempre os mesmos para a mesma casa)."""
    d_a = max(d0, PROFUNDIDADE_MINIMA)  # começo da casa (lado de perto)
    d_b = d0 + LARGURA_CASA             # fim da casa (lado de longe)
    altura = 140 + sorteio(indice, 1, 300)  # casas de alturas bem diferentes: de 140 a 439
    tijolo = sorteio(indice, 2, 3) == 0     # uma a cada 3 sem pintura: tijolo aparente
    cor = COR_TIJOLO if tijolo else CORES_CASAS[sorteio(indice, 3, len(CORES_CASAS))]

    def d_em(fracao):
        return d0 + LARGURA_CASA * fracao  # profundidade a uma fração da casa (0 = começo, 1 = fim)

    # Frente da casa vista de lado (a parede que dá para a rua).
    quadro_parede(tela, cor, lado, d_a, d_b, 0, altura)

    # Parede dos fundos (de frente para a câmera): aparece acima da casa vizinha, mais escura.
    pygame.draw.polygon(tela, escurecer(cor, 0.7), [ponto(lado, d_a, DIST_PAREDE, 0),
                                                    ponto(lado, d_a, DIST_PAREDE + PROFUNDIDADE_BLOCO, 0),
                                                    ponto(lado, d_a, DIST_PAREDE + PROFUNDIDADE_BLOCO, altura),
                                                    ponto(lado, d_a, DIST_PAREDE, altura)])

    # Teto visto de cima: laje, telha ou fibrocimento.
    tipo_teto = sorteio(indice, 4, 4)
    cor_teto = COR_TELHA if tipo_teto == 2 else (COR_FIBRO if tipo_teto == 3 else COR_LAJE)
    teto = [ponto(lado, d_a, DIST_PAREDE, altura),
            ponto(lado, d_b, DIST_PAREDE, altura),
            ponto(lado, d_b, DIST_PAREDE + PROFUNDIDADE_BLOCO, altura),
            ponto(lado, d_a, DIST_PAREDE + PROFUNDIDADE_BLOCO, altura)]
    pygame.draw.polygon(tela, cor_teto, teto)
    pygame.draw.polygon(tela, escurecer(cor_teto, 0.7), teto, 1)  # contorno de 1 pixel: separa um teto do outro

    # Tijolo aparente: linhas horizontais a cada 12 pixels.
    if tijolo and d0 >= PROFUNDIDADE_MINIMA:
        for h in range(12, altura, 12):
            pygame.draw.line(tela, COR_JUNTA, ponto(lado, d_a, DIST_PAREDE, h), ponto(lado, d_b, DIST_PAREDE, h), 1)

    # Laje: faixa de concreto no topo da parede.
    quadro_parede(tela, COR_LAJE, lado, d_a, d_b, altura - 12, altura)

    # Mural colorido em algumas casas pintadas: três listras.
    if not tijolo and sorteio(indice, 5, 6) == 0:
        for i, cor_listra in enumerate([(235, 90, 140), (250, 215, 60), (60, 190, 190)]):
            quadro_parede(tela, cor_listra, lado, d_em(0.05), d_em(0.95), 60 + i * 22, 82 + i * 22)

    # Térreo: bar com toldo listrado, ou portão de metal.
    if sorteio(indice, 6, 5) == 0:
        quadro_parede(tela, COR_VIDRO, lado, d_em(0.12), d_em(0.88), 15, 90)  # vitrine do bar
        for i in range(6):  # toldo: 6 listras vermelhas e brancas
            cor_listra = COR_TOLDO_1 if i % 2 == 0 else COR_TOLDO_2
            quadro_parede(tela, cor_listra, lado, d_em(0.08 + i * 0.14), d_em(0.08 + (i + 1) * 0.14), 95, 120)
    else:
        cor_portao = CORES_CASAS[sorteio(indice, 7, len(CORES_CASAS))]
        quadro_parede(tela, escurecer(cor_portao, 0.6), lado, d_em(0.12), d_em(0.45), 0, 85)  # portão de metal
        quadro_parede(tela, COR_VIDRO, lado, d_em(0.6), d_em(0.85), 30, 75)                    # janelinha

    # Andares de cima: uma janela pequena por andar.
    andar = 1
    while 130 * andar + 80 < altura - 12:
        base = 130 * andar
        quadro_parede(tela, COR_VIDRO, lado, d_em(0.2), d_em(0.45), base + 25, base + 80)
        quadro_parede(tela, COR_VIDRO, lado, d_em(0.62), d_em(0.8), base + 35, base + 75)
        andar += 1

    # Varal com roupas penduradas.
    if altura > 230 and sorteio(indice, 8, 3) == 0:
        h_varal = 130 + 55  # altura do fio
        pygame.draw.line(tela, COR_FIO, ponto(lado, d_em(0.05), DIST_PAREDE, h_varal),
                         ponto(lado, d_em(0.95), DIST_PAREDE, h_varal), 1)
        for i in range(4):
            cor_roupa = CORES_ROUPAS[(indice + i) % len(CORES_ROUPAS)]
            quadro_parede(tela, cor_roupa, lado, d_em(0.12 + i * 0.2), d_em(0.22 + i * 0.2), h_varal - 28, h_varal)

    # Em cima da laje: caixa d'água azul ou ferros de espera (de uma construção que vai crescer).
    d_c = d_em(0.5)
    if d_c >= PROFUNDIDADE_MINIMA:
        if sorteio(indice, 9, 2) == 0:
            x, y = ponto(lado, d_c, DIST_PAREDE + 90, altura)  # base da caixa, em cima do teto
            largura = 40 / d_c
            alto = 46 / d_c
            pygame.draw.rect(tela, COR_CAIXA, (x - largura / 2, y - alto, largura, alto))
            pygame.draw.ellipse(tela, COR_TAMPA_CAIXA, (x - largura / 2, y - alto - largura * 0.2, largura, largura * 0.4))
        else:
            for fracao in (0.15, 0.5, 0.85):
                x, y = ponto(lado, d_em(fracao), DIST_PAREDE + 15, altura)
                pygame.draw.line(tela, COR_FERRO, (x, y), (x, y - 45 / d_em(fracao)), 1)


def desenhar_casas(tela, deslocamento):
    """Casas dos dois lados, descendo com o tempo. As mais longe são desenhadas primeiro,
    para as mais perto ficarem por cima delas."""
    primeiro = int(deslocamento // LARGURA_CASA)  # primeira casa que ainda aparece
    ultimo = primeiro
    while ultimo * LARGURA_CASA - deslocamento < LIMITE_PROFUNDIDADE:
        ultimo += 1
    for n in range(ultimo, primeiro - 1, -1):  # de trás para frente
        d0 = n * LARGURA_CASA - deslocamento
        if d0 + LARGURA_CASA > PROFUNDIDADE_MINIMA:
            for lado in (-1, 1):
                desenhar_casa(tela, lado, n * 2 + (1 if lado > 0 else 0), d0)


def desenhar_asfalto(tela, deslocamento):
    """Rua de asfalto, meio-fio, traços das pistas e faixa de pedestres."""
    topo = LARGURA_RUA_TOPO // 2
    base = LARGURA_RUA_BASE // 2
    pygame.draw.polygon(tela, COR_FUNDO, [(MEIO - topo, 0), (MEIO + topo, 0),
                                          (MEIO + base, ALTURA), (MEIO - base, ALTURA)])

    n = int(deslocamento // PERIODO)
    while n * PERIODO - deslocamento < LIMITE_PROFUNDIDADE:
        d_perto = max(n * PERIODO - deslocamento, 0.5)
        d_longe = (n + 1) * PERIODO - deslocamento
        if d_longe > d_perto:
            y_baixo = y_da_profundidade(d_perto)
            y_cima = y_da_profundidade(d_longe)

            # Meio-fio: faixa ao longo de cada borda, alternando branco e cinza.
            cor = COR_MEIO_FIO_1 if n % 2 == 0 else COR_MEIO_FIO_2
            for lado in (-1, 1):
                borda_baixo = MEIO + lado * META_RUA / d_perto
                borda_cima = MEIO + lado * META_RUA / d_longe
                esp_baixo = 19 / d_perto  # espessura do meio-fio: diminui com a distância
                esp_cima = 19 / d_longe
                pygame.draw.polygon(tela, cor, [(borda_cima, y_cima), (borda_cima - lado * esp_cima, y_cima),
                                                (borda_baixo - lado * esp_baixo, y_baixo), (borda_baixo, y_baixo)])

            # Traços brancos entre as pistas: ocupam só a metade de cada período.
            d_fim = min(d_perto + PERIODO / 2, d_longe)
            y_t_cima = y_da_profundidade(d_fim)
            for lado in (-1, 1):
                x_baixo = MEIO + lado * (META_RUA / 3) / d_perto  # as linhas ficam a 1/3 do meio
                x_cima = MEIO + lado * (META_RUA / 3) / d_fim
                e_baixo = 2.2 / d_perto  # meia espessura do traço
                e_cima = 2.2 / d_fim
                pygame.draw.polygon(tela, COR_LINHA, [(x_cima - e_cima, y_t_cima), (x_cima + e_cima, y_t_cima),
                                                      (x_baixo + e_baixo, y_baixo), (x_baixo - e_baixo, y_baixo)])

            # Faixa de pedestres a cada 12 períodos.
            if n % 12 == 0:
                d_f = d_perto + 0.22  # a faixa ocupa um pedaço pequeno de profundidade
                y_f = y_da_profundidade(d_f)
                for i in range(0, 9, 2):  # 5 listras (as pares de 9 divisões da rua)
                    x0 = -1 + 2 * i / 9
                    x1 = -1 + 2 * (i + 1) / 9
                    pygame.draw.polygon(tela, COR_LINHA, [(MEIO + x0 * META_RUA / d_f, y_f), (MEIO + x1 * META_RUA / d_f, y_f),
                                                          (MEIO + x1 * META_RUA / d_perto, y_baixo),
                                                          (MEIO + x0 * META_RUA / d_perto, y_baixo)])
        n += 1


def topo_poste(lado, d, extra=0):
    """(x, y) do topo de um poste na calçada, à profundidade d. 'extra' desce o ponto (para fios mais baixos)."""
    x = MEIO + lado * (META_RUA + 24) / d
    y = y_da_profundidade(d) - (250 - extra) / d
    return (x, y)


def fio(tela, a, b, frouxo):
    """Um fio entre os pontos a e b, caído no meio (dois segmentos)."""
    meio_x = (a[0] + b[0]) / 2
    meio_y = (a[1] + b[1]) / 2 + frouxo
    pygame.draw.line(tela, COR_FIO, a, (meio_x, meio_y), 1)
    pygame.draw.line(tela, COR_FIO, (meio_x, meio_y), b, 1)


def desenhar_postes(tela, deslocamento):
    """Postes com emaranhado de fios (os 'gatos'), um a cada 2 períodos, em cada lado da rua."""
    passo = PERIODO * 2  # distância entre postes
    primeiro = int(deslocamento // passo)
    ultimo = primeiro
    while ultimo * passo - deslocamento < LIMITE_PROFUNDIDADE:
        ultimo += 1
    for k in range(ultimo, primeiro - 1, -1):  # dos mais longe para os mais perto
        d = k * passo - deslocamento
        if d < PROFUNDIDADE_MINIMA:
            continue
        for lado in (-1, 1):
            x, y_topo = topo_poste(lado, d)
            y_base = y_da_profundidade(d)
            grossura = max(1, int(7 / d))
            pygame.draw.line(tela, COR_POSTE, (x, y_base), (x, y_topo), grossura)  # o poste
            pygame.draw.line(tela, COR_POSTE, (x - 14 / d, y_topo + 8 / d), (x + 14 / d, y_topo + 8 / d), grossura)  # travessa
            if k % 3 == 0:  # alguns postes têm transformador
                pygame.draw.rect(tela, COR_TRANSFORMADOR, (x + 4 / d, y_topo + 14 / d, 14 / d, 22 / d))
            # Fios até o próximo poste (mais longe): três fios em alturas diferentes.
            d_prox = d + passo
            for extra, frouxo in ((0, 6), (12, 9), (26, 12)):
                fio(tela, topo_poste(lado, d, extra), topo_poste(lado, d_prox, extra), frouxo / d)
        # Fio atravessando a rua, de um poste ao outro, bem frouxo.
        fio(tela, topo_poste(-1, d, 10), topo_poste(1, d, 10), 14 / d)


def desenhar(tela, deslocamento):
    """Desenha o cenário inteiro. 'deslocamento' cresce com o tempo: quanto maior, mais a rua já andou."""
    desenhar_calcada(tela, deslocamento)   # 1) chão de concreto
    desenhar_casas(tela, deslocamento)     # 2) casas, lajes e caixas d'água
    desenhar_asfalto(tela, deslocamento)   # 3) rua, meio-fio, traços e faixa de pedestres
    desenhar_postes(tela, deslocamento)    # 4) postes e fios por cima de tudo