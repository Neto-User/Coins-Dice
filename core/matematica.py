"""
core/matematica.py
==================
Toda a lógica matemática do simulador, sem nenhuma dependência de interface.

Conceitos cobertos
------------------
- Análise Combinatória   : arranjo com repetição (dados) e combinação simples C(n,k) (moedas).
- Probabilidade Elementar: P(evento) = casos favoráveis / espaço amostral.
- Simulação de Monte Carlo: amostras aleatórias para estimar probabilidades.
- Desvio Absoluto Médio  : métrica de convergência entre teoria e experimento.
"""

from __future__ import annotations

import math
import random
from collections import Counter
from itertools import product as _product
from typing import Dict, List

Distribuicao = Dict[int, float]   # {resultado: probabilidade}


# ─────────────────────────────────────────────────────────────────────────────
# ESPAÇO AMOSTRAL
# ─────────────────────────────────────────────────────────────────────────────

def espaco_amostral_dados(n_dados: int, n_faces: int) -> List[tuple]:
    """
    Gera todos os resultados possíveis ao lançar n_dados dados de n_faces lados.

    Método: Arranjo com Repetição → Total = n_faces ^ n_dados
    Exemplo: 2d6 → 6² = 36 tuplas, de (1,1) a (6,6).
    """
    return list(_product(range(1, n_faces + 1), repeat=n_dados))


# ─────────────────────────────────────────────────────────────────────────────
# PROBABILIDADE TEÓRICA
# ─────────────────────────────────────────────────────────────────────────────

def prob_teorica_dados(n_dados: int, n_faces: int) -> Distribuicao:
    """
    P(soma = s) = |combinações cuja soma é s| / n_faces^n_dados

    Exemplo com 2d6: P(7) = 6/36 ≈ 16.7%
    """
    espaco   = espaco_amostral_dados(n_dados, n_faces)
    total    = len(espaco)
    contagem = Counter(sum(c) for c in espaco)
    return {s: contagem[s] / total for s in sorted(contagem)}


def prob_teorica_moedas(n_moedas: int) -> Distribuicao:
    """
    P(k caras) = C(n, k) / 2^n,  onde C(n,k) = n! / (k! × (n−k)!)

    Exemplo com 3 moedas: P(0C)=12.5%, P(1C)=37.5%, P(2C)=37.5%, P(3C)=12.5%
    """
    total = 2 ** n_moedas
    return {k: math.comb(n_moedas, k) / total for k in range(n_moedas + 1)}


# ─────────────────────────────────────────────────────────────────────────────
# SIMULAÇÃO (Monte Carlo)
# ─────────────────────────────────────────────────────────────────────────────

def simular_dados(n_dados: int, n_faces: int, n_simulacoes: int) -> List[int]:
    """Retorna lista com a soma de cada lançamento."""
    return [
        sum(random.randint(1, n_faces) for _ in range(n_dados))
        for _ in range(n_simulacoes)
    ]


def simular_moedas(n_moedas: int, n_simulacoes: int) -> List[int]:
    """
    Retorna lista com o nº de caras de cada rodada.
    n_moedas controla o range() interno — corrige o bug off-by-one.
    """
    return [
        sum(1 for _ in range(n_moedas) if random.random() < 0.5)
        for _ in range(n_simulacoes)
    ]


# ─────────────────────────────────────────────────────────────────────────────
# FREQUÊNCIA EXPERIMENTAL
# ─────────────────────────────────────────────────────────────────────────────

def frequencia_experimental(resultados: List[int]) -> Distribuicao:
    """
    P_exp(x) = ocorrências de x / total de simulações.
    Converge para P_teórica conforme n aumenta (Lei dos Grandes Números).
    """
    total    = len(resultados)
    contagem = Counter(resultados)
    return {k: contagem[k] / total for k in sorted(contagem)}


# ─────────────────────────────────────────────────────────────────────────────
# MÉTRICAS DE CONVERGÊNCIA
# ─────────────────────────────────────────────────────────────────────────────

def desvio_absoluto_medio(teorica: Distribuicao, experimental: Distribuicao) -> float:
    """
    DAM = Σ |P_teo(k) − P_exp(k)| / nº de resultados distintos

    DAM ≈ 0% → fiel à teoria.  DAM > 5% → aumente as simulações.
    """
    chaves  = set(teorica) | set(experimental)
    desvios = [abs(teorica.get(k, 0.0) - experimental.get(k, 0.0)) for k in chaves]
    return sum(desvios) / len(desvios) if desvios else 0.0


def classificar_precisao(dam: float) -> str:
    """Rótulo legível para o DAM."""
    if dam < 0.01:
        return "Alta  ✓  (DAM < 1%)"
    if dam < 0.05:
        return "Média    (DAM 1–5%)"
    return "Baixa ⚠  (DAM > 5%)"
