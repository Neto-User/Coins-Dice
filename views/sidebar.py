"""
views/sidebar.py — Componente Sidebar.
Painel de configuração com 4 passos guiados + botão SIMULAR + tabela de resultados.
"""

import tkinter as tk
import customtkinter as ctk
from config import (
    FUNDO_CARD, FUNDO_APP, AZUL_ROYAL, AZUL_CEU,
    AREIA, LARANJA, TEXTO_DIM
)


class Sidebar(ctk.CTkScrollableFrame):
    """
    Painel de configuração com 4 passos guiados:
      Passo 1 — Tipo de experimento (Dados ou Moedas)
      Passo 2 — Quantidade (slider com valor em destaque)
      Passo 3 — Faces por dado (somente para dados)
      Passo 4 — Número de simulações
      + Botão SIMULAR e tabela de resultados
    """

    def __init__(self, master, on_simular, on_config_change, **kw):
        super().__init__(
            master,
            width=312,
            fg_color=FUNDO_CARD,
            corner_radius=16,
            scrollbar_button_color=AZUL_CEU,
            **kw
        )
        self._on_simular       = on_simular
        self._on_config_change = on_config_change

        # Estado interno do slider (inteiro garantido)
        self._qtd_int = 2

        self._build()

    # ── Helpers visuais ──────────────────────────────────────────────────────

    def _titulo_secao(self, txt):
        ctk.CTkLabel(self, text=txt,
                     font=ctk.CTkFont("Georgia", 12, "bold"),
                     text_color=LARANJA
                     ).pack(anchor="w", padx=16, pady=(14, 2))
        ctk.CTkFrame(self, fg_color=LARANJA, height=1,
                     corner_radius=0).pack(fill="x", padx=16, pady=(0, 8))

    def _add_label(self, txt, dim=False):
        ctk.CTkLabel(self, text=txt,
                     font=ctk.CTkFont(size=11),
                     text_color=TEXTO_DIM if dim else AREIA
                     ).pack(anchor="w", padx=16)

    # ── Construção ───────────────────────────────────────────────────────────

    def _build(self):
        self._titulo_secao("⚙  Configure o Experimento")

        # ── PASSO 1 — Tipo ──
        self._add_label("Passo 1 — O que você quer lançar?")
        self._add_label("  Dados: gera somas aleatórias por lançamento", dim=True)
        self._add_label("  Moedas: conta quantas caras saem por rodada", dim=True)

        self._var_modo = ctk.StringVar(value="🎲  Dados")
        ctk.CTkSegmentedButton(
            self,
            values=["🎲  Dados", "🪙  Moedas"],
            variable=self._var_modo,
            command=self._ao_mudar_modo,
            selected_color=AZUL_CEU,
            selected_hover_color="#376a8a",
            unselected_color=AZUL_ROYAL,
            fg_color=AZUL_ROYAL,
            text_color=AREIA,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40
        ).pack(fill="x", padx=16, pady=(6, 16))

        # ── PASSO 2 — Quantidade ──
        self._lbl_passo2 = ctk.CTkLabel(self,
                                         text="Passo 2 — Quantos dados? (arraste o slider)",
                                         font=ctk.CTkFont(size=11), text_color=AREIA)
        self._lbl_passo2.pack(anchor="w", padx=16)
        self._add_label("  O valor selecionado aparece em destaque abaixo", dim=True)

        self._lbl_valor_qtd = ctk.CTkLabel(self, text="2",
                                            font=ctk.CTkFont("Courier New", 46, "bold"),
                                            text_color=LARANJA)
        self._lbl_valor_qtd.pack(pady=(6, 0))

        self._slider_var = tk.DoubleVar(value=2.0)
        self._slider = ctk.CTkSlider(
            self, from_=1, to=6, number_of_steps=5,
            variable=self._slider_var,
            button_color=LARANJA,
            button_hover_color="#c9a84c",
            progress_color=AZUL_CEU,
            fg_color="#0d1f35",
            command=self._ao_mover_slider
        )
        self._slider.pack(fill="x", padx=16, pady=(0, 2))

        linha_min_max = ctk.CTkFrame(self, fg_color="transparent")
        linha_min_max.pack(fill="x", padx=16, pady=(0, 14))
        ctk.CTkLabel(linha_min_max, text="mín: 1",
                     font=ctk.CTkFont(size=10), text_color=TEXTO_DIM).pack(side="left")
        self._lbl_max = ctk.CTkLabel(linha_min_max, text="máx: 6",
                                      font=ctk.CTkFont(size=10), text_color=TEXTO_DIM)
        self._lbl_max.pack(side="right")

        # ── PASSO 3 — Faces ──
        self._lbl_passo3 = ctk.CTkLabel(self,
                                         text="Passo 3 — Quantas faces tem cada dado?",
                                         font=ctk.CTkFont(size=11), text_color=AREIA)
        self._lbl_passo3.pack(anchor="w", padx=16)
        self._add_label("  d4=4 faces  d6=6 faces  d8=8 faces  d20=20 faces", dim=True)
        self._add_label("  Ignore este passo se usar moedas", dim=True)

        self._var_faces = ctk.StringVar(value="6")
        self._seg_faces = ctk.CTkSegmentedButton(
            self,
            values=["4", "6", "8", "10", "12", "20"],
            variable=self._var_faces,
            command=lambda _: self._on_config_change(),
            selected_color=AZUL_CEU,
            unselected_color=AZUL_ROYAL,
            fg_color=AZUL_ROYAL,
            text_color=AREIA,
            height=32
        )
        self._seg_faces.pack(fill="x", padx=16, pady=(6, 16))

        # ── PASSO 4 — Simulações ──
        self._add_label("Passo 4 — Quantas simulações executar?")
        self._add_label("  Mais simulações = resultado mais fiel à teoria", dim=True)
        self._add_label("  Recomendado: pelo menos 1.000", dim=True)

        for grupo in [(100, 500, 1000), (5000, 10000, 50000)]:
            linha = ctk.CTkFrame(self, fg_color="transparent")
            linha.pack(fill="x", padx=16, pady=2)
            for n in grupo:
                ctk.CTkButton(
                    linha, text=f"{n:,}", width=76, height=28,
                    font=ctk.CTkFont(size=11),
                    fg_color=AZUL_ROYAL, hover_color=AZUL_CEU,
                    text_color=AREIA, corner_radius=8,
                    command=lambda v=n: self._definir_simulacoes(v)
                ).pack(side="left", padx=2)

        self._add_label("  Ou digite um valor personalizado:", dim=True)
        self._var_sim = tk.StringVar(value="1000")
        ctk.CTkEntry(self,
                     textvariable=self._var_sim,
                     width=170, height=38,
                     font=ctk.CTkFont("Courier New", 16, "bold"),
                     fg_color=AZUL_ROYAL, border_color=AZUL_CEU,
                     text_color=LARANJA,
                     placeholder_text="ex: 2000"
                     ).pack(anchor="w", padx=16, pady=(4, 16))

        # ── Botão principal ──
        self._btn_simular = ctk.CTkButton(
            self,
            text="▶  SIMULAR AGORA",
            font=ctk.CTkFont("Georgia", 15, "bold"),
            fg_color=LARANJA, hover_color="#c9a84c",
            text_color=AZUL_ROYAL,
            height=54, corner_radius=14,
            command=self._on_simular
        )
        self._btn_simular.pack(fill="x", padx=16, pady=(0, 8))

        # Barra de progresso (aparece só durante a simulação)
        self._barra_prog = ctk.CTkProgressBar(self, mode="indeterminate",
                                               progress_color=LARANJA,
                                               fg_color=AZUL_ROYAL, height=6)

        # ── Seção de resultados ──
        self._titulo_secao("📊  Resultados da Simulação")
        self._add_label("Teórico = calculado pela fórmula matemática", dim=True)
        self._add_label("Experim. = obtido nas simulações aleatórias", dim=True)
        self._add_label("✓ desvio < 1%  |  ⚠ desvio > 5%", dim=True)

        self._txt_stats = ctk.CTkTextbox(
            self, height=260,
            font=ctk.CTkFont("Courier New", 11),
            fg_color=FUNDO_APP,
            text_color=AREIA,
            border_color=AZUL_CEU, border_width=1,
            corner_radius=10,
            state="disabled"
        )
        self._txt_stats.pack(fill="x", padx=16, pady=(6, 16))

    # ── Callbacks de interface ────────────────────────────────────────────────

    def _ao_mudar_modo(self, _=None):
        """Chamado quando o usuário troca entre Dados e Moedas."""
        eh_dado = self._var_modo.get().startswith("🎲")

        if eh_dado:
            self._lbl_passo2.configure(text="Passo 2 — Quantos dados? (arraste o slider)")
            self._slider.configure(to=6, number_of_steps=5)
            self._lbl_max.configure(text="máx: 6")
            maximo = 6
        else:
            self._lbl_passo2.configure(text="Passo 2 — Quantas moedas? (arraste o slider)")
            self._slider.configure(to=8, number_of_steps=7)
            self._lbl_max.configure(text="máx: 8")
            maximo = 8

        self._seg_faces.configure(state="normal" if eh_dado else "disabled")
        self._lbl_passo3.configure(text_color=AREIA if eh_dado else TEXTO_DIM)

        if self._qtd_int > maximo:
            self._qtd_int = maximo
            self._slider_var.set(float(maximo))
            self._lbl_valor_qtd.configure(text=str(maximo))

        self._on_config_change()

    def _ao_mover_slider(self, valor):
        """Arredonda o valor float para inteiro e notifica a mudança."""
        inteiro = int(round(float(valor)))
        self._qtd_int = inteiro
        self._lbl_valor_qtd.configure(text=str(inteiro))
        self._on_config_change()

    def _definir_simulacoes(self, n: int):
        self._var_sim.set(str(n))
        self._on_config_change()

    # ── API pública (leitura de estado) ──────────────────────────────────────

    def get_modo_dado(self) -> bool:
        return self._var_modo.get().startswith("🎲")

    def get_qtd(self) -> int:
        return self._qtd_int

    def get_faces(self) -> int:
        return int(self._var_faces.get())

    def get_n_simulacoes(self) -> int:
        try:
            return int(self._var_sim.get())
        except ValueError:
            return 0

    # ── API pública (controle visual) ────────────────────────────────────────

    def set_simulando(self, ativo: bool):
        if ativo:
            self._btn_simular.configure(state="disabled", text="⏳  Calculando…")
            self._barra_prog.pack(fill="x", padx=16, pady=(0, 6))
            self._barra_prog.start()
        else:
            self._barra_prog.stop()
            self._barra_prog.pack_forget()
            self._btn_simular.configure(state="normal", text="▶  SIMULAR AGORA")

    def exibir_stats(self, linhas: list):
        self._txt_stats.configure(state="normal")
        self._txt_stats.delete("0.0", "end")
        self._txt_stats.insert("end", "\n".join(linhas))
        self._txt_stats.configure(state="disabled")
