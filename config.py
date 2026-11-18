# Constantes do jogo. Se quiser mudar um valor, mude aqui e vale para todos os arquivos.

LARGURA = 480  # largura da janela, em pixels
ALTURA = 800   # altura da janela, em pixels
FPS = 60       # quadros por segundo (quantas vezes por segundo o jogo se atualiza)

# x do centro de cada pista (0 = esquerda, 1 = meio, 2 = direita), na altura do entregador.
# O // é a divisão que joga fora o resto: os valores ficam 80, 240 e 400.
PISTAS = [LARGURA // 6, LARGURA // 2, 5 * LARGURA // 6]

# y dos pés do entregador. É a altura em que a rua tem o tamanho "normal".
Y_CHAO = ALTURA - 120  # 120 pixels acima do fim da tela

# Cores no formato (vermelho, verde, azul), cada valor de 0 a 255
COR_FUNDO = (60, 60, 60)     # cinza-escuro: o asfalto
COR_LINHA = (230, 230, 230)  # quase branco: as linhas das pistas
COR_TEXTO = (255, 255, 255)  # branco: os textos
COR_CALCADA = (90, 120, 80)  # verde: o que fica fora da rua

# Rua em perspectiva: estreita no alto da tela (longe) e larga embaixo (perto)
LARGURA_RUA_TOPO = 160  # largura da rua em y = 0
LARGURA_RUA_BASE = 536  # largura da rua em y = ALTURA (maior que a janela: a rua "sai" pelos lados)


def largura_rua(y):
    """Largura da rua na altura y da tela."""
    # y / ALTURA vai de 0 (topo) até 1 (embaixo). A largura cresce junto, do valor do topo ao da base.
    return LARGURA_RUA_TOPO + (LARGURA_RUA_BASE - LARGURA_RUA_TOPO) * y / ALTURA


def escala(y):
    """Fator de tamanho na altura y: 1.0 na altura do entregador, menor mais longe (acima)."""
    # Compara a largura da rua em y com a largura da rua na altura do entregador.
    return largura_rua(y) / largura_rua(Y_CHAO)


def x_da_pista(pista, y):
    """x do centro de uma pista na altura y. Na altura Y_CHAO é igual a PISTAS[pista]."""
    meio = LARGURA // 2  # x do meio da tela (240)
    # PISTAS[pista] - meio é a distância da pista até o meio, na altura do entregador.
    # Multiplicar por escala(y) encolhe essa distância quando y está longe (em cima).
    return meio + (PISTAS[pista] - meio) * escala(y)