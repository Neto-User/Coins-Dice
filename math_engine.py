"""
math_engine.py — Funções matemáticas e de simulação.
Separadas da interface para facilitar testes e reutilização.
"""

import random
import math
from collections import Counter
from itertools import product as iter_product


# ══════════════════════════════════════════════════════════════════════════════
# ESPAÇO AMOSTRAL
# ══════════════════════════════════════════════════════════════════════════════

def calcular_espaco_amostral_dados(n_dados: int, n_faces: int) -> list:
    """
    Gera todos os resultados possíveis ao lançar n_dados dados de n_faces lados.

    Usa Arranjo com Repetição (Análise Combinatória):
        Total de resultados = n_faces ^ n_dados
    Exemplo: 2 dados de 6 faces → 6² = 36 combinações.

    Retorna uma lista de tuplas, onde cada tupla é um resultado possível.
    Ex: [(1,1), (1,2), ..., (6,6)]
    """
    return list(iter_product(range(1, n_faces + 1), repeat=n_dados))


# ══════════════════════════════════════════════════════════════════════════════
# PROBABILIDADE TEÓRICA
# ══════════════════════════════════════════════════════════════════════════════

def calcular_probabilidade_teorica_dados(n_dados: int, n_faces: int) -> dict:
    """
    Calcula a probabilidade TEÓRICA de cada soma possível ao lançar os dados.

    Fórmula (Probabilidade Elementar):
        P(soma = s) = nº de combinações que resultam em s  /  total de combinações

    Exemplo com 2d6:
        P(soma=7) = 6/36 ≈ 16.7%  (as 6 combinações: 1+6, 2+5, 3+4, 4+3, 5+2, 6+1)

    Retorna um dicionário {soma: probabilidade}.
    """
    espaco = calcular_espaco_amostral_dados(n_dados, n_faces)
    total  = len(espaco)                          # = n_faces ^ n_dados
    contagem = Counter(sum(combo) for combo in espaco)
    return {soma: contagem[soma] / total for soma in sorted(contagem)}


def calcular_probabilidade_teorica_moedas(n_moedas: int) -> dict:
    """
    Calcula a probabilidade TEÓRICA de obter exatamente k caras em n_moedas lançamentos.

    Fórmula (Análise Combinatória + Probabilidade):
        P(k caras) = C(n, k) / 2^n
        onde C(n, k) = n! / (k! × (n-k)!)  ← Combinação simples

    Exemplo com 3 moedas:
        P(0 caras) = C(3,0)/8 = 1/8 = 12.5%
        P(1 cara)  = C(3,1)/8 = 3/8 = 37.5%
        P(2 caras) = C(3,2)/8 = 3/8 = 37.5%
        P(3 caras) = C(3,3)/8 = 1/8 = 12.5%

    Retorna um dicionário {nº de caras: probabilidade}.
    """
    total = 2 ** n_moedas
    return {k: math.comb(n_moedas, k) / total for k in range(n_moedas + 1)}


# ══════════════════════════════════════════════════════════════════════════════
# SIMULAÇÕES
# ══════════════════════════════════════════════════════════════════════════════

def executar_simulacao_dados(n_dados: int, n_faces: int, n_simulacoes: int) -> list:
    """
    Simula n_simulacoes lançamentos de n_dados dados de n_faces lados.

    Cada lançamento gera uma soma aleatória entre n_dados e n_dados*n_faces.
    Retorna uma lista com a soma de cada lançamento.
    """
    return [
        sum(random.randint(1, n_faces) for _ in range(n_dados))
        for _ in range(n_simulacoes)
    ]


def executar_simulacao_moedas(n_moedas: int, n_simulacoes: int) -> list:
    """
    Simula n_simulacoes rodadas, cada uma lançando EXATAMENTE n_moedas moedas.

    Cada moeda tem 50% de chance de cara.
    Retorna uma lista com o nº de caras obtidas em cada rodada.

    CORREÇÃO APLICADA: o parâmetro n_moedas controla o range() interno,
    garantindo que 1 moeda = 1 lançamento por rodada (não 2).
    """
    resultados = []
    for _ in range(n_simulacoes):
        caras = sum(1 for _ in range(n_moedas) if random.random() < 0.5)
        resultados.append(caras)
    return resultados


# ══════════════════════════════════════════════════════════════════════════════
# ANÁLISE DOS RESULTADOS
# ══════════════════════════════════════════════════════════════════════════════

def calcular_frequencia_experimental(resultados: list) -> dict:
    """
    Converte os resultados brutos em probabilidade experimental (frequência relativa).

    Fórmula:
        P_experimental(x) = nº de vezes que x apareceu / total de simulações

    Quanto maior o número de simulações, mais próxima da probabilidade teórica.
    """
    total    = len(resultados)
    contagem = Counter(resultados)
    return {k: contagem[k] / total for k in sorted(contagem)}


def calcular_desvio_absoluto_medio(teorica: dict, experimental: dict) -> float:
    """
    Mede o quanto o resultado experimental desviou da teoria, em média.

    Fórmula:
        DAM = Σ |P_teórico(k) - P_experimental(k)| / nº de resultados

    DAM próximo de 0% → simulação muito fiel à teoria.
    DAM alto → poucas simulações ou variação aleatória grande.
    """
    chaves = set(teorica) | set(experimental)
    desvios = [abs(teorica.get(k, 0) - experimental.get(k, 0)) for k in chaves]
    return sum(desvios) / len(desvios) if desvios else 0.0
