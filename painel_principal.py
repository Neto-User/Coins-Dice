"""
views/painel_principal.py — Componente PainelPrincipal.
Contém: Painel de Fórmulas, Gráfico de Barras e Log de resultados.
"""

import customtkinter as ctk
from config import FUNDO_APP, FUNDO_CARD, AZUL_CEU, LARANJA, TEXTO_DIM, AREIA
from views.grafico import GraficoBarras
from views.painel_formulas import PainelFormulas


class PainelPrincipal(ctk.CTkFrame):
    """
    Área direita da janela com três seções empilhadas:
      1. Painel de Fórmulas  — espaço amostral e fórmulas usadas
      2. Gráfico de Barras   — compara teórico vs experimental
      3. Log de Resultados   — últimos valores gerados
    """

    def __init__(self, master, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self._build()

    def _build(self):
        # 1. Painel de fórmulas
        self._painel_form = PainelFormulas(self)
        self._painel_form.pack(fill="x", pady=(0, 10))

        # 2. Título do gráfico
        ctk.CTkLabel(self,
                     text="📈  Gráfico  —  Barra AZUL = Teórico   |   Barra COLORIDA = Experimental",
                     font=ctk.CTkFont("Georgia", 12, "bold"),
                     text_color=LARANJA
                     ).pack(anchor="w", pady=(0, 6))

        # 3. Gráfico de barras
        graf_container = ctk.CTkFrame(self, fg_color=FUNDO_APP,
                                       corner_radius=14,
                                       border_color=AZUL_CEU, border_width=1)
        graf_container.pack(fill="both", expand=True, pady=(0, 10))

        self._grafico = GraficoBarras(graf_container)
        self._grafico.pack(fill="both", expand=True, padx=4, pady=4)

        # 4. Log de amostra
        ctk.CTkLabel(self,
                     text="🔎  Amostra — últimos valores gerados pela simulação:",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXTO_DIM
                     ).pack(anchor="w")

        self._txt_log = ctk.CTkTextbox(self, height=50,
                                        font=ctk.CTkFont("Courier New", 11),
                                        fg_color=FUNDO_CARD,
                                        text_color=AREIA,
                                        corner_radius=10,
                                        state="disabled")
        self._txt_log.pack(fill="x", pady=(4, 0))

    # ── API pública ───────────────────────────────────────────────────────────

    def atualizar_formulas(self, modo_dado: bool, qtd: int, faces: int, n_sim: int):
        self._painel_form.atualizar(modo_dado, qtd, faces, n_sim)

    def desenhar_grafico(self, teorica: dict, experimental: dict, rotulo: str):
        self._grafico.desenhar(teorica, experimental, rotulo)

    def exibir_log(self, res: list, eh_dado: bool):
        amostra = res[-80:]
        if eh_dado:
            log_txt = "  ".join(str(v) for v in amostra)
        else:
            log_txt = "  ".join(
                ("0C" if v == 0 else ("1C" if v == 1 else f"{v}C"))
                for v in amostra
            )
        self._txt_log.configure(state="normal")
        self._txt_log.delete("0.0", "end")
        self._txt_log.insert("end", log_txt)
        self._txt_log.configure(state="disabled")
