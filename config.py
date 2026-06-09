"""
config.py — Configurações de tema, cores e constantes globais da aplicação.
"""

import customtkinter as ctk

# ── Configuração de tema ──────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Paleta de cores ───────────────────────────────────────────────────────────
AZUL_ROYAL = "#1D3557"   # fundo do cabeçalho e detalhes
AZUL_CEU   = "#457B9D"   # barras teóricas e destaques
AREIA      = "#F1FAEE"   # texto principal claro
LARANJA    = "#E9C46A"   # títulos de seção e botão principal
VERDE      = "#2DC653"   # barra experimental próxima da teoria
AMARELO    = "#F4D35E"   # barra experimental um pouco distante
VERMELHO   = "#E63946"   # barra experimental muito distante
FUNDO_CARD = "#162840"   # fundo dos painéis laterais
FUNDO_APP  = "#0F1E30"   # fundo geral da janela
TEXTO_DIM  = "#7FA8C0"   # textos secundários / explicativos
