"""
views/painel_formulas.py — Componente PainelFormulas.
Exibe em tempo real as fórmulas e o espaço amostral do experimento configurado.
"""

import customtkinter as ctk
from config import FUNDO_CARD, LARANJA, AREIA, TEXTO_DIM


class PainelFormulas(ctk.CTkFrame):
    """
    Exibe em tempo real as fórmulas e o espaço amostral do experimento configurado.
    Atualiza sempre que o usuário muda o tipo, quantidade ou número de simulações.
    """

    def __init__(self, master, **kw):
        super().__init__(master, fg_color=FUNDO_CARD, corner_radius=12, **kw)

        ctk.CTkLabel(self,
                     text="📐  Fórmulas e Espaço Amostral do Experimento",
                     font=ctk.CTkFont("Georgia", 12, "bold"),
                     text_color=LARANJA
                     ).pack(anchor="w", padx=14, pady=(10, 4))

        ctk.CTkFrame(self, fg_color=LARANJA, height=1,
                     corner_radius=0).pack(fill="x", padx=14, pady=(0, 6))

        self._lbl = ctk.CTkLabel(self, text="",
                                  font=ctk.CTkFont("Courier New", 11),
                                  text_color=AREIA, justify="left",
                                  wraplength=720, anchor="w")
        self._lbl.pack(anchor="w", padx=14, pady=(0, 10), fill="x")

    def atualizar(self, modo_dado: bool, qtd: int, faces: int, n_sim: int):
        """Recalcula e exibe as fórmulas com os valores atuais da configuração."""
        if modo_dado:
            total_ea = faces ** qtd
            soma_min = qtd
            soma_max = qtd * faces
            n_dist   = soma_max - soma_min + 1
            txt = (
                f"  Tipo            →  {qtd} dado{'s' if qtd > 1 else ''} de {faces} faces\n"
                f"  Espaço amostral →  {faces}^{qtd} = {total_ea:,} combinações  "
                f"(Arranjo com repetição: faces^dados)\n"
                f"  Somas possíveis →  de {soma_min} até {soma_max}  "
                f"= {n_dist} resultados distintos\n"
                f"  Prob. teórica   →  P(soma = s)  =  combinações que geram s  ÷  {total_ea:,}\n"
                f"  Simulações      →  {n_sim:,} lançamentos de "
                f"{qtd} dado{'s' if qtd > 1 else ''}"
            )
        else:
            total_ea = 2 ** qtd
            txt = (
                f"  Tipo            →  {qtd} moeda{'s' if qtd > 1 else ''} por rodada\n"
                f"  Espaço amostral →  2^{qtd} = {total_ea:,} combinações possíveis "
                f"(cara ou coroa para cada moeda)\n"
                f"  Resultados      →  de 0 a {qtd} cara{'s' if qtd > 1 else ''}  "
                f"= {qtd + 1} resultados distintos\n"
                f"  Prob. teórica   →  P(k caras) = C({qtd}, k) ÷ {total_ea}  "
                f"onde C(n,k) = n! ÷ (k! × (n−k)!)\n"
                f"  Simulações      →  {n_sim:,} rodadas, cada uma com "
                f"EXATAMENTE {qtd} moeda{'s' if qtd > 1 else ''} lançada{'s' if qtd > 1 else ''}"
            )
        self._lbl.configure(text=txt)
