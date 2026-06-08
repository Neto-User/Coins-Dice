"""
ui/componentes.py
=================
Widgets reutilizáveis da interface.

Classes
-------
SectionHeader   — título de seção com linha decorativa dourada.
PainelFormulas  — exibe as fórmulas e o espaço amostral em tempo real.
PainelHistorico — lista as últimas rodadas com DAM e botão de re-exibição.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List

import customtkinter as ctk

from ui.constantes import (
    FUNDO_APP, FUNDO_CARD, FUNDO_GRADE,
    AZUL_CEU, AZUL_ROYAL, LARANJA, AREIA, TEXTO_DIM,
    VERDE, AMARELO, VERMELHO, COR_HIST,
    FONTE_SECAO, FONTE_MONO,
    HISTORICO_MAX,
)

Distribuicao = Dict[int, float]


# ─────────────────────────────────────────────────────────────────────────────
# Estrutura de dados de uma rodada
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Rodada:
    """Snapshot imutável de uma execução de simulação."""
    numero:    int
    rotulo:    str            # ex: "2d6 · 1.000 sim."
    n_sim:     int
    dam:       float
    teorica:   Distribuicao
    exp:       Distribuicao
    eixo_x:    str
    eh_dado:   bool
    qtd:       int
    total_ea:  int


# ─────────────────────────────────────────────────────────────────────────────
# SectionHeader
# ─────────────────────────────────────────────────────────────────────────────

class SectionHeader(ctk.CTkFrame):
    """Título de seção padronizado: texto em LARANJA + linha divisória dourada."""

    def __init__(self, master, texto: str, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        ctk.CTkLabel(
            self, text=texto,
            font=ctk.CTkFont(*FONTE_SECAO),
            text_color=LARANJA,
        ).pack(anchor="w", padx=16, pady=(14, 2))
        ctk.CTkFrame(self, fg_color=LARANJA, height=1,
                     corner_radius=0).pack(fill="x", padx=16, pady=(0, 8))


# ─────────────────────────────────────────────────────────────────────────────
# PainelFormulas
# ─────────────────────────────────────────────────────────────────────────────

class PainelFormulas(ctk.CTkFrame):
    """
    Exibe em tempo real as fórmulas e o espaço amostral do experimento atual.
    Atualizado via atualizar() sempre que o usuário muda qualquer parâmetro.
    """

    def __init__(self, master, **kw):
        super().__init__(master, fg_color=FUNDO_CARD, corner_radius=12, **kw)
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(
            self,
            text="📐  Fórmulas e Espaço Amostral",
            font=ctk.CTkFont(*FONTE_SECAO),
            text_color=LARANJA,
        ).pack(anchor="w", padx=14, pady=(10, 4))
        ctk.CTkFrame(self, fg_color=LARANJA, height=1,
                     corner_radius=0).pack(fill="x", padx=14, pady=(0, 6))
        self._lbl = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont("Times New Roman", 14),
            text_color=AREIA, justify="left",
            wraplength=720, anchor="w",
        )
        self._lbl.pack(anchor="w", padx=14, pady=(0, 10), fill="x")

    def atualizar(self, modo_dado: bool, qtd: int, faces: int, n_sim: int) -> None:
        if modo_dado:
            self._lbl.configure(text=self._texto_dados(qtd, faces, n_sim))
        else:
            self._lbl.configure(text=self._texto_moedas(qtd, n_sim))

    @staticmethod
    def _texto_dados(qtd: int, faces: int, n_sim: int) -> str:
        total  = faces ** qtd
        s_min, s_max = qtd, qtd * faces
        d = "dado" if qtd == 1 else "dados"
        return (
            f"  Tipo            →  {qtd} {d} de {faces} faces\n"
            f"  Espaço amostral →  {faces}^{qtd} = {total:,} combinações  (Arranjo com repetição)\n"
            f"  Somas possíveis →  de {s_min} até {s_max}  =  {s_max - s_min + 1} resultados distintos\n"
            f"  Prob. teórica   →  P(soma = s)  =  combinações com soma s  ÷  {total:,}\n"
            f"  Simulações      →  {n_sim:,} lançamentos de {qtd} {d}"
        )

    @staticmethod
    def _texto_moedas(qtd: int, n_sim: int) -> str:
        total = 2 ** qtd
        m = "moeda" if qtd == 1 else "moedas"
        c = "cara"  if qtd == 1 else "caras"
        return (
            f"  Tipo            →  {qtd} {m} por rodada\n"
            f"  Espaço amostral →  2^{qtd} = {total:,} combinações\n"
            f"  Resultados      →  de 0 a {qtd} {c}  =  {qtd + 1} resultados distintos\n"
            f"  Prob. teórica   →  P(k caras) = C({qtd}, k) ÷ {total}  "
            f"onde C(n,k) = n! ÷ (k! × (n−k)!)\n"
            f"  Simulações      →  {n_sim:,} rodadas com {qtd} {m} cada"
        )


# ─────────────────────────────────────────────────────────────────────────────
# PainelHistorico
# ─────────────────────────────────────────────────────────────────────────────

class PainelHistorico(ctk.CTkFrame):
    """
    Exibe as últimas N rodadas executadas.

    Cada linha mostra: nº da rodada, configuração, DAM e um botão
    para re-exibir aquela rodada no gráfico principal.

    Parâmetros
    ----------
    master : widget
        Widget pai.
    on_reexibir : Callable[[Rodada], None]
        Callback chamado quando o usuário clica em "Ver" numa rodada.
    """

    def __init__(self, master, on_reexibir: Callable[[Rodada], None], **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self._on_reexibir = on_reexibir
        self._rodadas: List[Rodada] = []

        SectionHeader(self, "🕘  Histórico de Rodadas").pack(fill="x")

        self._lbl_vazio = ctk.CTkLabel(
            self,
            text="Nenhuma simulação executada ainda.",
            font=ctk.CTkFont(size=11),
            text_color=TEXTO_DIM,
        )
        self._lbl_vazio.pack(anchor="w", padx=16, pady=(0, 8))

        self._lista = ctk.CTkFrame(self, fg_color="transparent")
        self._lista.pack(fill="x", padx=12)

    # ── API pública ───────────────────────────────────────────────────────────

    def adicionar(self, rodada: Rodada) -> None:
        """Adiciona uma rodada ao histórico (mantém no máximo HISTORICO_MAX)."""
        self._rodadas.insert(0, rodada)
        if len(self._rodadas) > HISTORICO_MAX:
            self._rodadas = self._rodadas[:HISTORICO_MAX]
        self._redesenhar()

    # ── Renderização ──────────────────────────────────────────────────────────

    def _redesenhar(self) -> None:
        for w in self._lista.winfo_children():
            w.destroy()

        if not self._rodadas:
            self._lbl_vazio.pack(anchor="w", padx=16, pady=(0, 8))
            return

        self._lbl_vazio.pack_forget()

        for idx, r in enumerate(self._rodadas):
            cor  = COR_HIST[idx % len(COR_HIST)]
            dam_pct = r.dam * 100
            cor_dam = VERDE if dam_pct < 1 else (AMARELO if dam_pct < 5 else VERMELHO)

            linha = ctk.CTkFrame(
                self._lista,
                fg_color=FUNDO_CARD,
                corner_radius=8,
            )
            linha.pack(fill="x", pady=3)

            # Indicador colorido da rodada
            ctk.CTkFrame(linha, fg_color=cor, width=4,
                         corner_radius=2).pack(side="left", fill="y", padx=(6, 8), pady=6)

            # Informações
            info = ctk.CTkFrame(linha, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, pady=4)

            ctk.CTkLabel(
                info,
                text=f"#{r.numero}  {r.rotulo}",
                font=ctk.CTkFont("Helvetica", 11, "bold"),
                text_color=AREIA,
                anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=f"DAM: {dam_pct:.2f}%  ·  {r.n_sim:,} simulações",
                font=ctk.CTkFont("Helvetica", 10),
                text_color=cor_dam,
                anchor="w",
            ).pack(anchor="w")

            # Botão "Ver"
            ctk.CTkButton(
                linha,
                text="Ver",
                width=46, height=28,
                font=ctk.CTkFont("Helvetica", 11),
                fg_color=cor + "33",
                hover_color=cor + "66",
                text_color=cor,
                border_color=cor,
                border_width=1,
                corner_radius=6,
                command=lambda rd=r: self._on_reexibir(rd),
            ).pack(side="right", padx=8, pady=6)
