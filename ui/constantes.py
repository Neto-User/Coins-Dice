"""
ui/constantes.py
================
Paleta de cores, fontes e dimensões usadas em toda a interface.
Uma única alteração aqui reflete em todo o app.
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# PALETA DE CORES
# ─────────────────────────────────────────────────────────────────────────────

FUNDO_APP   = "#0F1E30"   # fundo geral da janela
FUNDO_CARD  = "#162840"   # fundo dos painéis / cartões
FUNDO_GRADE = "#1E3A55"   # linhas de grade do gráfico

AZUL_ROYAL  = "#1D3557"   # cabeçalho e bordas de destaque
AZUL_CEU    = "#457B9D"   # barras teóricas, botões secundários
LARANJA     = "#E9C46A"   # títulos de seção, botão principal, destaques

AREIA       = "#F1FAEE"   # texto principal sobre fundo escuro
TEXTO_DIM   = "#7FA8C0"   # texto secundário / dicas

# Barras experimentais — classificadas pelo desvio em relação à teoria
VERDE       = "#2DC653"   # desvio < 4%
AMARELO     = "#F4D35E"   # desvio 4–9%
VERMELHO    = "#E63946"   # desvio > 9%

# Histórico de rodadas
COR_HIST = ["#457B9D", "#E9C46A", "#2DC653", "#E63946", "#A78BFA"]

# ─────────────────────────────────────────────────────────────────────────────
# FONTES
# ─────────────────────────────────────────────────────────────────────────────

FONTE_TITULO    = ("Georgia",     26, "bold")
FONTE_SECAO     = ("Georgia",     12, "bold")
FONTE_MONO      = ("Courier New", 11)
FONTE_MONO_LG   = ("Courier New", 16, "bold")
FONTE_DESTAQUE  = ("Courier New", 46, "bold")
FONTE_GRAFICO   = ("Courier New",  7)
FONTE_GRAFICO_X = ("Helvetica",    8)
FONTE_GRAFICO_Y = ("Helvetica",    9)

# ─────────────────────────────────────────────────────────────────────────────
# DIMENSÕES
# ─────────────────────────────────────────────────────────────────────────────

SIDEBAR_LARGURA  = 312
JANELA_INICIAL   = "1180x820"
JANELA_MINIMA    = (980, 680)
ALTURA_CABECALHO = 70
ALTURA_LOG       = 50
ALTURA_STATS     = 220
HISTORICO_MAX    = 5     # máximo de rodadas guardadas no histórico

# ─────────────────────────────────────────────────────────────────────────────
# LIMITES DO SLIDER
# ─────────────────────────────────────────────────────────────────────────────

SLIDER_DADOS_MAX  = 6
SLIDER_MOEDAS_MAX = 8
SLIDER_INICIAL    = 2
