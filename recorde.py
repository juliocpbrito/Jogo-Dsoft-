import os  # os: usado para checar se um arquivo existe

ARQUIVO = "recorde.txt"  # nome do arquivo onde o recorde fica guardado


def carregar():
    """Lê o recorde salvo. Se o arquivo não existir ou estiver vazio, devolve 0."""
    if not os.path.exists(ARQUIVO):  # primeira vez jogando: ainda não há arquivo
        return 0
    with open(ARQUIVO, "r") as arquivo:  # "r" = abrir para leitura; o with fecha o arquivo sozinho
        texto = arquivo.read().strip()  # lê tudo e tira espaços e quebras de linha das pontas
    if texto == "":  # arquivo existe mas está vazio
        return 0
    return int(texto)  # converte o texto para número inteiro


def salvar(valor):
    """Grava o recorde no arquivo."""
    with open(ARQUIVO, "w") as arquivo:  # "w" = abrir para escrita (apaga o que havia antes)
        arquivo.write(str(valor))  # arquivo só guarda texto, então converte o número com str()