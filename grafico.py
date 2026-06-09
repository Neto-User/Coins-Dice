"""
views/grafico.py — Componente GraficoBarras.
Gráfico de barras duplas desenhado em Canvas puro do Tkinter.
"""

import tkinter as tk
from config import (
    FUNDO_APP, TEXTO_DIM, AREIA, AZUL_CEU,
    VERDE, AMARELO, VERMELHO, LARANJA
)


class GraficoBarras(tk.Canvas):
    """
    Gráfico de barras duplas desenhado diretamente no Canvas do Tkinter.

    Para cada resultado possível, exibe duas barras lado a lado:
      ▮ Barra AZUL    → probabilidade teórica (calculada matematicamente)
      ▮ Barra COLORIDA → probabilidade experimental (obtida nas simulações)

    A cor da barra experimental indica o desvio em relação à teoria:
      🟢 Verde   → desvio < 4%   (muito próximo)
      🟡 Amarelo → desvio 4–9%  (aceitável)
      🔴 Vermelho → desvio > 9%  (longe — tente mais simulações)
    """

    def __init__(self, master, **kw):
        super().__init__(master, bg=FUNDO_APP, highlightthickness=0, **kw)
        self._job = None

    def desenhar(self, teorica: dict, experimental: dict, rotulo_eixo_x: str = "Resultado"):
        """Agenda o redesenho para evitar flickering durante redimensionamento."""
        if self._job:
            self.after_cancel(self._job)
        self._job = self.after(80, lambda: self._renderizar(teorica, experimental, rotulo_eixo_x))

    def _renderizar(self, teorica, experimental, rotulo_eixo_x):
        self.delete("all")
        self.update_idletasks()
        W = self.winfo_width()
        H = self.winfo_height()

        if W < 50 or H < 50:
            self._job = self.after(100, lambda: self._renderizar(teorica, experimental, rotulo_eixo_x))
            return

        # Margens internas do gráfico
        PAD_ESQ, PAD_DIR, PAD_TOP, PAD_BOT = 70, 20, 32, 68
        area_w = W - PAD_ESQ - PAD_DIR
        area_h = H - PAD_TOP - PAD_BOT

        chaves = sorted(set(teorica) | set(experimental))
        n      = len(chaves)
        if not n:
            self.create_text(W // 2, H // 2,
                             text="Execute uma simulação para ver o gráfico",
                             fill=TEXTO_DIM, font=("Helvetica", 12))
            return

        max_val = max(
            max(teorica.values(),     default=0),
            max(experimental.values(), default=0)
        ) * 1.20 or 0.1

        # ── Grade horizontal (linhas de referência) ──
        for i in range(6):
            frac = i / 5
            y    = PAD_TOP + area_h - frac * area_h
            pct  = frac * max_val * 100
            self.create_line(PAD_ESQ, y, W - PAD_DIR, y,
                             fill="#1e3a55", dash=(4, 5))
            self.create_text(PAD_ESQ - 6, y,
                             text=f"{pct:.0f}%",
                             anchor="e", fill=TEXTO_DIM,
                             font=("Courier New", 8))

        # ── Eixos X e Y ──
        self.create_line(PAD_ESQ, PAD_TOP, PAD_ESQ, PAD_TOP + area_h,
                         fill=TEXTO_DIM, width=1)
        self.create_line(PAD_ESQ, PAD_TOP + area_h, W - PAD_DIR, PAD_TOP + area_h,
                         fill=TEXTO_DIM, width=1)

        # ── Largura das barras ──
        grupo_w = area_w / n
        barra_w = max(6, min(grupo_w * 0.30, 45))
        espaco  = barra_w * 0.20

        for i, k in enumerate(chaves):
            cx = PAD_ESQ + (i + 0.5) * grupo_w

            # Barra TEÓRICA (azul)
            vt = teorica.get(k, 0)
            ht = vt / max_val * area_h
            x0t = cx - barra_w - espaco
            x1t = cx - espaco
            yt  = PAD_TOP + area_h - ht
            self.create_rectangle(x0t, yt, x1t, PAD_TOP + area_h,
                                  fill=AZUL_CEU, outline="")
            if ht > 16:
                self.create_text((x0t + x1t) / 2, yt - 5,
                                 text=f"{vt*100:.1f}%",
                                 fill=AZUL_CEU, font=("Courier New", 7), anchor="s")

            # Barra EXPERIMENTAL (cor baseada no desvio)
            ve   = experimental.get(k, 0)
            he   = ve / max_val * area_h
            x0e  = cx + espaco
            x1e  = cx + barra_w + espaco
            ye   = PAD_TOP + area_h - he
            diff = abs(vt - ve)
            cor  = VERDE if diff < 0.04 else (AMARELO if diff < 0.09 else VERMELHO)
            self.create_rectangle(x0e, ye, x1e, PAD_TOP + area_h,
                                  fill=cor, outline="")
            if he > 16:
                self.create_text((x0e + x1e) / 2, ye - 5,
                                 text=f"{ve*100:.1f}%",
                                 fill=cor, font=("Courier New", 7), anchor="s")

            # Rótulo do eixo X
            if rotulo_eixo_x == "Caras":
                label = "0 caras" if k == 0 else ("1 cara" if k == 1 else f"{k} caras")
            else:
                label = f"Soma\n{k}"
            self.create_text(cx, PAD_TOP + area_h + 18,
                             text=label, fill=AREIA,
                             font=("Helvetica", 8), justify="center")

        # ── Legenda ──
        legenda = [
            (AZUL_CEU, "Teórico (esperado pela matemática)"),
            (VERDE,    "Experim. próximo  (desvio < 4%)"),
            (AMARELO,  "Experim. distante (desvio 4–9%)"),
            (VERMELHO, "Experim. longe    (desvio > 9%)"),
        ]
        lx = PAD_ESQ
        for cor, txt in legenda:
            self.create_rectangle(lx, H - 13, lx + 10, H - 4,
                                  fill=cor, outline="")
            self.create_text(lx + 13, H - 8, text=txt,
                             fill=cor, anchor="w", font=("Helvetica", 7))
            lx += len(txt) * 5 + 22

        # Título do eixo X
        self.create_text(W / 2, H - 1,
                         text=f"← {rotulo_eixo_x} →",
                         fill=TEXTO_DIM, font=("Helvetica", 9), anchor="s")
