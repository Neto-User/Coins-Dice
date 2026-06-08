"""
ui/grafico.py
=============
Widget de gráfico de barras duplas — teórico × experimental.

Barra AZUL     → probabilidade teórica  (calculada matematicamente)
Barra COLORIDA → probabilidade experimental (obtida nas simulações)

Cor da barra experimental:
  Verde    → desvio < 4%
  Amarelo  → desvio 4–9%
  Vermelho → desvio > 9%
"""

from __future__ import annotations

import tkinter as tk
from typing import Dict

from ui.constantes import (
    FUNDO_APP, FUNDO_GRADE,
    AZUL_CEU, AREIA, TEXTO_DIM,
    VERDE, AMARELO, VERMELHO,
    FONTE_GRAFICO, FONTE_GRAFICO_X, FONTE_GRAFICO_Y,
)

Distribuicao = Dict[int, float]

_PAD = dict(esq=70, dir=20, top=32, bot=68)

_LEGENDA = [
    (AZUL_CEU, "Teórico"),
    (VERDE,    "Experim. próximo  (< 4%)"),
    (AMARELO,  "Experim. distante (4–9%)"),
    (VERMELHO, "Experim. longe    (> 9%)"),
]


class GraficoBarras(tk.Canvas):
    """
    Canvas com gráfico de barras duplas (teórico × experimental).

    Uso:
        g = GraficoBarras(parent)
        g.pack(fill="both", expand=True)
        g.desenhar(teorica, experimental, rotulo_eixo_x="Soma (2d6)")
    """

    def __init__(self, master, **kw):
        super().__init__(master, bg=FUNDO_APP, highlightthickness=0, **kw)
        self._job: str | None = None

    # ── API pública ───────────────────────────────────────────────────────────

    def desenhar(
        self,
        teorica: Distribuicao,
        experimental: Distribuicao,
        rotulo_eixo_x: str = "Resultado",
    ) -> None:
        """Agenda redesenho com debounce de 80 ms (evita flickering)."""
        if self._job:
            self.after_cancel(self._job)
        self._job = self.after(80, lambda: self._renderizar(teorica, experimental, rotulo_eixo_x))

    # ── Renderização ──────────────────────────────────────────────────────────

    def _renderizar(self, teorica, experimental, rotulo_eixo_x) -> None:
        self.delete("all")
        self.update_idletasks()
        W, H = self.winfo_width(), self.winfo_height()

        if W < 50 or H < 50:
            self._job = self.after(100, lambda: self._renderizar(teorica, experimental, rotulo_eixo_x))
            return

        chaves = sorted(set(teorica) | set(experimental))
        if not chaves:
            self.create_text(W // 2, H // 2,
                text="Execute uma simulação para ver o gráfico",
                fill=TEXTO_DIM, font=("Helvetica", 12))
            return

        PL, PR, PT, PB = _PAD["esq"], _PAD["dir"], _PAD["top"], _PAD["bot"]
        aw, ah = W - PL - PR, H - PT - PB
        max_val = max(max(teorica.values(), default=0.0),
                      max(experimental.values(), default=0.0)) * 1.20 or 0.1

        self._grade(W, PL, PR, PT, ah, max_val)
        self._eixos(W, PL, PR, PT, ah)
        self._barras(chaves, teorica, experimental, PL, PT, ah, aw, max_val, rotulo_eixo_x)
        self._legenda(PL, H)
        self._titulo_x(W, H, rotulo_eixo_x)

    def _grade(self, W, PL, PR, PT, ah, max_val) -> None:
        for i in range(6):
            f = i / 5
            y = PT + ah - f * ah
            self.create_line(PL, y, W - PR, y, fill=FUNDO_GRADE, dash=(4, 5))
            self.create_text(PL - 6, y, text=f"{f * max_val * 100:.0f}%",
                anchor="e", fill=TEXTO_DIM, font=FONTE_GRAFICO)

    def _eixos(self, W, PL, PR, PT, ah) -> None:
        self.create_line(PL, PT, PL, PT + ah, fill=TEXTO_DIM, width=1)
        self.create_line(PL, PT + ah, W - PR, PT + ah, fill=TEXTO_DIM, width=1)

    def _barras(self, chaves, teorica, experimental, PL, PT, ah, aw, max_val, rotulo_eixo_x) -> None:
        n       = len(chaves)
        grupo_w = aw / n
        barra_w = max(6.0, min(grupo_w * 0.30, 45.0))
        espaco  = barra_w * 0.20

        for i, k in enumerate(chaves):
            cx = PL + (i + 0.5) * grupo_w

            # Barra teórica
            vt = teorica.get(k, 0.0)
            ht = vt / max_val * ah
            x0t, x1t = cx - barra_w - espaco, cx - espaco
            yt = PT + ah - ht
            self.create_rectangle(x0t, yt, x1t, PT + ah, fill=AZUL_CEU, outline="")
            if ht > 16:
                self.create_text((x0t + x1t) / 2, yt - 5,
                    text=f"{vt * 100:.1f}%", fill=AZUL_CEU,
                    font=FONTE_GRAFICO, anchor="s")

            # Barra experimental
            ve   = experimental.get(k, 0.0)
            he   = ve / max_val * ah
            x0e, x1e = cx + espaco, cx + barra_w + espaco
            ye   = PT + ah - he
            diff = abs(vt - ve)
            cor  = VERDE if diff < 0.04 else (AMARELO if diff < 0.09 else VERMELHO)
            self.create_rectangle(x0e, ye, x1e, PT + ah, fill=cor, outline="")
            if he > 16:
                self.create_text((x0e + x1e) / 2, ye - 5,
                    text=f"{ve * 100:.1f}%", fill=cor,
                    font=FONTE_GRAFICO, anchor="s")

            # Rótulo X
            if rotulo_eixo_x == "Caras":
                label = "0 caras" if k == 0 else ("1 cara" if k == 1 else f"{k} caras")
            else:
                label = f"Soma\n{k}"
            self.create_text(cx, PT + ah + 18, text=label,
                fill=AREIA, font=FONTE_GRAFICO_X, justify="center")

    def _legenda(self, PL, H) -> None:
        lx = PL
        for cor, txt in _LEGENDA:
            self.create_rectangle(lx, H - 13, lx + 10, H - 4, fill=cor, outline="")
            self.create_text(lx + 13, H - 8, text=txt, fill=cor,
                anchor="w", font=("Helvetica", 7))
            lx += len(txt) * 5 + 22

    def _titulo_x(self, W, H, rotulo) -> None:
        self.create_text(W / 2, H - 1, text=f"← {rotulo} →",
            fill=TEXTO_DIM, font=FONTE_GRAFICO_Y, anchor="s")
