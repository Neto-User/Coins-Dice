"""
ui/janela.py
============
Janela principal da aplicação.

Layout
------
┌─────────────────────────────────────────────────────────────────┐
│  CABEÇALHO                                                      │
├──────────────────┬──────────────────────────────────────────────┤
│                  │  PainelFormulas  (fórmulas em tempo real)    │
│  SIDEBAR         │  Título do gráfico                           │
│  ─────────────   │  GraficoBarras   (teórico × experimental)    │
│  1. Tipo         │  Log de amostra                              │
│  2. Quantidade   │                                              │
│  3. Faces        │                                              │
│  4. Simulações   │                                              │
│  [SIMULAR]       │                                              │
│  Tabela stats    │                                              │
│  PainelHistorico │                                              │
└──────────────────┴──────────────────────────────────────────────┘
"""

from __future__ import annotations

import threading
import tkinter as tk

import customtkinter as ctk

from core.matematica import (
    simular_dados, simular_moedas,
    prob_teorica_dados, prob_teorica_moedas,
    frequencia_experimental, desvio_absoluto_medio, classificar_precisao,
)
from ui.componentes import PainelFormulas, PainelHistorico, Rodada, SectionHeader
from ui.grafico import GraficoBarras
from ui.constantes import (
    FUNDO_APP, FUNDO_CARD,
    AZUL_ROYAL, AZUL_CEU, LARANJA, AREIA, TEXTO_DIM,
    FONTE_TITULO, FONTE_SECAO, FONTE_MONO, FONTE_MONO_LG, FONTE_DESTAQUE,
    SIDEBAR_LARGURA, JANELA_INICIAL, JANELA_MINIMA, ALTURA_CABECALHO,
    ALTURA_LOG, ALTURA_STATS,
    SLIDER_DADOS_MAX, SLIDER_MOEDAS_MAX, SLIDER_INICIAL,
)


class App(ctk.CTk):
    """
    Controlador principal — instancia widgets, reage a eventos e
    orquestra a simulação em background via threading.
    """

    def __init__(self):
        super().__init__()
        self.title("🎲  Simulador de Probabilidade — Coins & Dice")
        self.geometry(JANELA_INICIAL)
        self.minsize(*JANELA_MINIMA)
        self.configure(fg_color=FUNDO_APP)

        self._qtd_int: int = SLIDER_INICIAL
        self._num_rodada: int = 0

        # Painel principal criado ANTES da sidebar:
        # a sidebar chama _atualizar_formulas() durante sua construção
        # e precisa que self._painel_form já exista.
        self._build_cabecalho()
        self._build_corpo()

    # =========================================================================
    # LAYOUT
    # =========================================================================

    def _build_cabecalho(self) -> None:
        hdr = ctk.CTkFrame(self, fg_color=AZUL_ROYAL,
                           corner_radius=0, height=ALTURA_CABECALHO)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr,
            text="🎲  Simulador de Probabilidade  —  Coins & Dice",
            font=ctk.CTkFont(*FONTE_TITULO), text_color=AREIA,
        ).pack(side="left", padx=24, pady=14)

        ctk.CTkLabel(hdr,
            text="Probabilidade Teórica  ×  Experimental",
            font=ctk.CTkFont(size=12), text_color=TEXTO_DIM,
        ).pack(side="right", padx=24)

        ctk.CTkFrame(self, fg_color=LARANJA, height=2,
                     corner_radius=0).pack(fill="x")

    def _build_corpo(self) -> None:
        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=20, pady=14)
        self._build_painel_principal(corpo)   # direita — primeiro
        self._build_sidebar(corpo)            # esquerda — depois

    # ── Painel principal (direita) ────────────────────────────────────────────

    def _build_painel_principal(self, pai) -> None:
        main = ctk.CTkFrame(pai, fg_color="transparent")
        main.pack(side="right", fill="both", expand=True)

        self._painel_form = PainelFormulas(main)
        self._painel_form.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(main,
            text="📈  Gráfico  —  Barra AZUL = Teórico  |  Barra COLORIDA = Experimental",
            font=ctk.CTkFont(*FONTE_SECAO), text_color=LARANJA,
        ).pack(anchor="w", pady=(0, 6))

        graf_container = ctk.CTkFrame(main, fg_color=FUNDO_APP,
            corner_radius=14, border_color=AZUL_CEU, border_width=1)
        graf_container.pack(fill="both", expand=True, pady=(0, 10))
        self._grafico = GraficoBarras(graf_container)
        self._grafico.pack(fill="both", expand=True, padx=4, pady=4)

        ctk.CTkLabel(main,
            text="🔎  Amostra — últimos valores gerados pela simulação:",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXTO_DIM,
        ).pack(anchor="w")

        self._txt_log = ctk.CTkTextbox(main, height=ALTURA_LOG,
            font=ctk.CTkFont(*FONTE_MONO), fg_color=FUNDO_CARD,
            text_color=AREIA, corner_radius=10, state="disabled")
        self._txt_log.pack(fill="x", pady=(4, 0))

    # ── Sidebar (esquerda) ────────────────────────────────────────────────────

    def _build_sidebar(self, pai) -> None:
        side = ctk.CTkScrollableFrame(pai, width=SIDEBAR_LARGURA,
            fg_color=FUNDO_CARD, corner_radius=16,
            scrollbar_button_color=AZUL_CEU)
        side.pack(side="left", fill="y", padx=(0, 14))
        self._preencher_sidebar(side)

    def _preencher_sidebar(self, side) -> None:

        def sec(txt: str) -> None:
            SectionHeader(side, txt).pack(fill="x")

        def lbl(txt: str, dim: bool = False) -> None:
            ctk.CTkLabel(side, text=txt, font=ctk.CTkFont(size=11),
                text_color=TEXTO_DIM if dim else AREIA,
            ).pack(anchor="w", padx=16)

        # ── 1. Tipo ───────────────────────────────────────────────────────────
        sec("⚙  Configure o Experimento")
        lbl("1. O que você quer lançar?")

        self._var_modo = ctk.StringVar(value="🎲  Dados")
        ctk.CTkSegmentedButton(side,
            values=["🎲  Dados", "🪙  Moedas"],
            variable=self._var_modo,
            command=self._ao_mudar_modo,
            selected_color=AZUL_CEU, selected_hover_color="#376a8a",
            unselected_color=AZUL_ROYAL, fg_color=AZUL_ROYAL,
            text_color=AREIA,
            font=ctk.CTkFont(size=13, weight="bold"), height=40,
        ).pack(fill="x", padx=16, pady=(6, 16))

        # ── 2. Quantidade ─────────────────────────────────────────────────────
        self._lbl_passo2 = ctk.CTkLabel(side,
            text="2. Quantos dados?",
            font=ctk.CTkFont(size=11), text_color=AREIA)
        self._lbl_passo2.pack(anchor="w", padx=16)

        self._lbl_valor_qtd = ctk.CTkLabel(side,
            text=str(SLIDER_INICIAL),
            font=ctk.CTkFont(*FONTE_DESTAQUE), text_color=LARANJA)
        self._lbl_valor_qtd.pack(pady=(6, 0))

        self._slider_var = tk.DoubleVar(value=float(SLIDER_INICIAL))
        self._slider = ctk.CTkSlider(side,
            from_=1, to=SLIDER_DADOS_MAX,
            number_of_steps=SLIDER_DADOS_MAX - 1,
            variable=self._slider_var,
            button_color=LARANJA, button_hover_color="#c9a84c",
            progress_color=AZUL_CEU, fg_color="#0d1f35",
            command=self._ao_mover_slider)
        self._slider.pack(fill="x", padx=16, pady=(0, 2))

        linha_mm = ctk.CTkFrame(side, fg_color="transparent")
        linha_mm.pack(fill="x", padx=16, pady=(0, 14))
        ctk.CTkLabel(linha_mm, text="mín: 1",
            font=ctk.CTkFont(size=10), text_color=TEXTO_DIM).pack(side="left")
        self._lbl_max = ctk.CTkLabel(linha_mm,
            text=f"máx: {SLIDER_DADOS_MAX}",
            font=ctk.CTkFont(size=10), text_color=TEXTO_DIM)
        self._lbl_max.pack(side="right")

        # ── 3. Faces ──────────────────────────────────────────────────────────
        self._lbl_passo3 = ctk.CTkLabel(side,
            text="3. Faces por dado:",
            font=ctk.CTkFont(size=11), text_color=AREIA)
        self._lbl_passo3.pack(anchor="w", padx=16)

        self._var_faces = ctk.StringVar(value="6")
        self._seg_faces = ctk.CTkSegmentedButton(side,
            values=["4", "6", "8", "10", "12", "20"],
            variable=self._var_faces,
            command=lambda _: self._atualizar_formulas(),
            selected_color=AZUL_CEU, unselected_color=AZUL_ROYAL,
            fg_color=AZUL_ROYAL, text_color=AREIA, height=32)
        self._seg_faces.pack(fill="x", padx=16, pady=(6, 16))

        # ── 4. Simulações ─────────────────────────────────────────────────────
        lbl("4. Quantas simulações?")
        lbl("  Mais simulações → mais fiel à teoria", dim=True)

        for grupo in [(100, 500, 1_000), (5_000, 10_000, 50_000)]:
            linha = ctk.CTkFrame(side, fg_color="transparent")
            linha.pack(fill="x", padx=16, pady=2)
            for n in grupo:
                ctk.CTkButton(linha, text=f"{n:,}", width=76, height=28,
                    font=ctk.CTkFont(size=11),
                    fg_color=AZUL_ROYAL, hover_color=AZUL_CEU,
                    text_color=AREIA, corner_radius=8,
                    command=lambda v=n: self._definir_simulacoes(v),
                ).pack(side="left", padx=2)

        lbl("  Ou digite:", dim=True)
        self._var_sim = tk.StringVar(value="1000")
        ctk.CTkEntry(side, textvariable=self._var_sim,
            width=170, height=38,
            font=ctk.CTkFont(*FONTE_MONO_LG),
            fg_color=AZUL_ROYAL, border_color=AZUL_CEU,
            text_color=LARANJA, placeholder_text="ex: 2000",
        ).pack(anchor="w", padx=16, pady=(4, 16))

        # ── Botão SIMULAR ─────────────────────────────────────────────────────
        self._btn_simular = ctk.CTkButton(side,
            text="▶  SIMULAR AGORA",
            font=ctk.CTkFont(*FONTE_SECAO),
            fg_color=LARANJA, hover_color="#c9a84c",
            text_color=AZUL_ROYAL,
            height=54, corner_radius=14,
            command=self._executar_simulacao)
        self._btn_simular.pack(fill="x", padx=16, pady=(0, 8))

        self._barra_prog = ctk.CTkProgressBar(side,
            mode="indeterminate", progress_color=LARANJA,
            fg_color=AZUL_ROYAL, height=6)

        # ── Tabela de resultados ──────────────────────────────────────────────
        sec("📊  Resultados da Simulação")
        lbl("✓ desvio < 1%   |   ⚠ desvio > 5%", dim=True)

        self._txt_stats = ctk.CTkTextbox(side, height=ALTURA_STATS,
            font=ctk.CTkFont(*FONTE_MONO),
            fg_color=FUNDO_APP, text_color=AREIA,
            border_color=AZUL_CEU, border_width=1,
            corner_radius=10, state="disabled")
        self._txt_stats.pack(fill="x", padx=16, pady=(6, 4))

        # ── Histórico de rodadas ──────────────────────────────────────────────
        self._historico = PainelHistorico(side,
            on_reexibir=self._reexibir_rodada)
        self._historico.pack(fill="x", pady=(0, 16))

        self._atualizar_formulas()

    # =========================================================================
    # CALLBACKS DE INTERFACE
    # =========================================================================

    def _ao_mudar_modo(self, _=None) -> None:
        eh_dado  = self._var_modo.get().startswith("🎲")
        novo_max = SLIDER_DADOS_MAX if eh_dado else SLIDER_MOEDAS_MAX

        self._lbl_passo2.configure(
            text="2. Quantos dados?" if eh_dado else "2. Quantas moedas?")
        self._slider.configure(to=novo_max, number_of_steps=novo_max - 1)
        self._lbl_max.configure(text=f"máx: {novo_max}")
        self._seg_faces.configure(state="normal" if eh_dado else "disabled")
        self._lbl_passo3.configure(text_color=AREIA if eh_dado else TEXTO_DIM)

        if self._qtd_int > novo_max:
            self._qtd_int = novo_max
            self._slider_var.set(float(novo_max))
            self._lbl_valor_qtd.configure(text=str(novo_max))

        self._atualizar_formulas()

    def _ao_mover_slider(self, valor) -> None:
        """Arredonda DoubleVar → inteiro. Corrige bug off-by-one."""
        n = int(round(float(valor)))
        self._qtd_int = n
        self._lbl_valor_qtd.configure(text=str(n))
        self._atualizar_formulas()

    def _definir_simulacoes(self, n: int) -> None:
        self._var_sim.set(str(n))
        self._atualizar_formulas()

    def _atualizar_formulas(self) -> None:
        eh_dado = self._var_modo.get().startswith("🎲")
        faces   = int(self._var_faces.get())
        try:
            n_sim = int(self._var_sim.get())
        except ValueError:
            n_sim = 0
        self._painel_form.atualizar(eh_dado, self._qtd_int, faces, n_sim)

    # =========================================================================
    # HISTÓRICO — re-exibe uma rodada anterior no gráfico
    # =========================================================================

    def _reexibir_rodada(self, rodada: Rodada) -> None:
        """Restaura o gráfico, log e tabela de uma rodada do histórico."""
        self._grafico.desenhar(rodada.teorica, rodada.exp, rodada.eixo_x)
        self._txt_stats.configure(state="normal")
        self._txt_stats.delete("0.0", "end")
        self._txt_stats.insert("end", self._montar_tabela(
            rodada.teorica, rodada.exp, rodada.dam,
            rodada.n_sim, rodada.eh_dado, rodada.qtd, rodada.total_ea,
        ))
        self._txt_stats.configure(state="disabled")

    # =========================================================================
    # SIMULAÇÃO (thread separada para não travar a interface)
    # =========================================================================

    def _executar_simulacao(self) -> None:
        try:
            n_sim = int(self._var_sim.get())
            if n_sim < 1:
                raise ValueError
        except ValueError:
            self._mostrar_erro("Digite um número de simulações válido (mínimo: 1).")
            return

        self._btn_simular.configure(state="disabled", text="⏳  Calculando…")
        self._barra_prog.pack(fill="x", padx=16, pady=(0, 6))
        self._barra_prog.start()

        threading.Thread(target=self._rodar_em_background,
                         args=(n_sim,), daemon=True).start()

    def _rodar_em_background(self, n_sim: int) -> None:
        eh_dado = self._var_modo.get().startswith("🎲")
        qtd     = self._qtd_int

        if eh_dado:
            faces    = int(self._var_faces.get())
            res      = simular_dados(qtd, faces, n_sim)
            teorica  = prob_teorica_dados(qtd, faces)
            exp      = frequencia_experimental(res)
            eixo_x   = f"Soma  ({qtd}d{faces})"
            total_ea = faces ** qtd
            rotulo   = f"{qtd}d{faces}"
        else:
            res      = simular_moedas(qtd, n_sim)
            teorica  = prob_teorica_moedas(qtd)
            exp      = frequencia_experimental(res)
            eixo_x   = "Caras"
            total_ea = 2 ** qtd
            rotulo   = f"{qtd} moeda{'s' if qtd > 1 else ''}"

        dam = desvio_absoluto_medio(teorica, exp)

        self.after(0, lambda: self._aplicar_resultados(
            teorica, exp, res, eixo_x, rotulo, dam, n_sim, eh_dado, qtd, total_ea))

    def _aplicar_resultados(
        self, teorica, exp, res, eixo_x, rotulo,
        dam, n_sim, eh_dado, qtd, total_ea,
    ) -> None:

        self._barra_prog.stop()
        self._barra_prog.pack_forget()
        self._btn_simular.configure(state="normal", text="▶  SIMULAR AGORA")

        # Gráfico
        self._grafico.desenhar(teorica, exp, eixo_x)

        # Log
        amostra = res[-80:]
        if eh_dado:
            log_txt = "  ".join(str(v) for v in amostra)
        else:
            log_txt = "  ".join(
                "0C" if v == 0 else ("1C" if v == 1 else f"{v}C")
                for v in amostra)
        self._txt_log.configure(state="normal")
        self._txt_log.delete("0.0", "end")
        self._txt_log.insert("end", log_txt)
        self._txt_log.configure(state="disabled")

        # Tabela
        self._txt_stats.configure(state="normal")
        self._txt_stats.delete("0.0", "end")
        self._txt_stats.insert("end", self._montar_tabela(
            teorica, exp, dam, n_sim, eh_dado, qtd, total_ea))
        self._txt_stats.configure(state="disabled")

        # Histórico
        self._num_rodada += 1
        rodada = Rodada(
            numero=self._num_rodada,
            rotulo=f"{rotulo}  ·  {n_sim:,} sim.",
            n_sim=n_sim, dam=dam,
            teorica=teorica, exp=exp,
            eixo_x=eixo_x, eh_dado=eh_dado,
            qtd=qtd, total_ea=total_ea,
        )
        self._historico.adicionar(rodada)

    # ── Formatação da tabela ──────────────────────────────────────────────────

    @staticmethod
    def _montar_tabela(teorica, exp, dam, n_sim, eh_dado, qtd, total_ea) -> str:
        sep    = "─" * 38
        chaves = sorted(set(teorica) | set(exp))

        linhas = [
            "=" * 38,
            f"  Experimento  : {'Dados' if eh_dado else 'Moedas'}",
            f"  Quantidade   : {qtd}",
            f"  Simulações   : {n_sim:,}",
            f"  Esp. Amostral: {total_ea:,} resultados",
            sep,
            f"  {'Resultado':<14} {'Teórico':>8} {'Experim.':>9}",
            sep,
        ]

        for k in chaves:
            vt = teorica.get(k, 0.0) * 100
            ve = exp.get(k, 0.0)     * 100
            flag = " ✓" if abs(vt - ve) < 1.0 else (" ⚠" if abs(vt - ve) > 5.0 else "  ")
            rk   = (f"Soma {k}" if eh_dado
                    else ("0 caras" if k == 0 else ("1 cara" if k == 1 else f"{k} caras")))
            linhas.append(f"  {rk:<14} {vt:>7.2f}% {ve:>8.2f}%{flag}")

        linhas += [
            sep,
            f"  DAM          : {dam * 100:.3f}%",
            f"  Precisão     : {classificar_precisao(dam)}",
            "=" * 38,
            "",
            "  💡 DAM = Desvio Absoluto Médio",
            "  Aumente as simulações para reduzir.",
        ]
        return "\n".join(linhas)

    # ── Diálogo de erro ───────────────────────────────────────────────────────

    def _mostrar_erro(self, mensagem: str) -> None:
        win = ctk.CTkToplevel(self)
        win.title("Aviso")
        win.geometry("380x160")
        win.configure(fg_color=FUNDO_CARD)
        win.grab_set()
        ctk.CTkLabel(win, text=f"⚠  {mensagem}",
            font=ctk.CTkFont(size=13), text_color=LARANJA,
            wraplength=330).pack(pady=32)
        ctk.CTkButton(win, text="OK", width=110,
            fg_color=AZUL_CEU, command=win.destroy).pack()
