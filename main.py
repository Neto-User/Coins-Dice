"""
╔══════════════════════════════════════════════════════════════╗
║   🎲 Simulador de Probabilidade — Dados & Moedas             ║
║   Requer: pip install customtkinter                          ║
║   Rodar:  python main.py                                     ║
╚══════════════════════════════════════════════════════════════╝
"""

import threading
import customtkinter as ctk

from config import FUNDO_APP, FUNDO_CARD, AZUL_ROYAL, AZUL_CEU, AREIA, LARANJA, TEXTO_DIM
from math_engine import (
    executar_simulacao_dados,
    executar_simulacao_moedas,
    calcular_probabilidade_teorica_dados,
    calcular_probabilidade_teorica_moedas,
    calcular_frequencia_experimental,
    calcular_desvio_absoluto_medio,
)
from views.sidebar import Sidebar
from views.painel_principal import PainelPrincipal


class App(ctk.CTk):
    """
    Janela principal do simulador.

    Organização:
      ┌─────────────────────────────────────────────────────────┐
      │  CABEÇALHO                                              │
      ├───────────────┬─────────────────────────────────────────┤
      │               │  Painel de Fórmulas                     │
      │   SIDEBAR     │  Gráfico (Teórico vs Experimental)      │
      │ (Configuração │  Log dos últimos resultados             │
      │  + Resultados)│                                         │
      └───────────────┴─────────────────────────────────────────┘
    """

    def __init__(self):
        super().__init__()
        self.title("🎲  Simulador de Probabilidade — Dados & Moedas")
        self.geometry("1180x820")
        self.minsize(980, 680)
        self.configure(fg_color=FUNDO_APP)

        self._build_cabecalho()
        self._build_corpo()

    # ── CABEÇALHO ─────────────────────────────────────────────────────────────

    def _build_cabecalho(self):
        hdr = ctk.CTkFrame(self, fg_color=AZUL_ROYAL, corner_radius=0, height=70)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr,
                     text="🎲  Simulador de Probabilidade  —  Dados & Moedas",
                     font=ctk.CTkFont("Georgia", 22, "bold"),
                     text_color=AREIA
                     ).pack(side="left", padx=24, pady=14)

        ctk.CTkLabel(hdr,
                     text="Probabilidade Teórica  ×  Experimental",
                     font=ctk.CTkFont(size=12),
                     text_color=TEXTO_DIM
                     ).pack(side="right", padx=24)

        ctk.CTkFrame(self, fg_color=LARANJA, height=2,
                     corner_radius=0).pack(fill="x")

    # ── CORPO ─────────────────────────────────────────────────────────────────

    def _build_corpo(self):
        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=20, pady=14)

        # Painel principal criado antes da sidebar para evitar referências nulas
        self._painel = PainelPrincipal(corpo)
        self._painel.pack(side="right", fill="both", expand=True)

        self._sidebar = Sidebar(
            corpo,
            on_simular=self._executar_simulacao,
            on_config_change=self._atualizar_formulas,
        )
        self._sidebar.pack(side="left", fill="y", padx=(0, 14))

        # Primeira renderização das fórmulas
        self._atualizar_formulas()

    # ── CALLBACKS ─────────────────────────────────────────────────────────────

    def _atualizar_formulas(self):
        """Repassa o estado atual da sidebar para o painel de fórmulas."""
        self._painel.atualizar_formulas(
            self._sidebar.get_modo_dado(),
            self._sidebar.get_qtd(),
            self._sidebar.get_faces(),
            self._sidebar.get_n_simulacoes(),
        )

    def _executar_simulacao(self):
        """Valida os inputs e inicia a simulação em background."""
        n_sim = self._sidebar.get_n_simulacoes()
        if n_sim < 1:
            self._mostrar_erro("Digite um número de simulações válido (mínimo: 1).")
            return

        self._sidebar.set_simulando(True)

        threading.Thread(
            target=self._rodar_em_background,
            args=(n_sim,),
            daemon=True
        ).start()

    def _rodar_em_background(self, n_sim: int):
        """Executa os cálculos em thread separada e agenda atualização da UI."""
        eh_dado = self._sidebar.get_modo_dado()
        qtd     = self._sidebar.get_qtd()

        if eh_dado:
            faces    = self._sidebar.get_faces()
            res      = executar_simulacao_dados(qtd, faces, n_sim)
            teorica  = calcular_probabilidade_teorica_dados(qtd, faces)
            exp      = calcular_frequencia_experimental(res)
            rotulo   = f"Soma  ({qtd}d{faces})"
            total_ea = faces ** qtd
        else:
            res      = executar_simulacao_moedas(qtd, n_sim)
            teorica  = calcular_probabilidade_teorica_moedas(qtd)
            exp      = calcular_frequencia_experimental(res)
            rotulo   = "Caras"
            total_ea = 2 ** qtd

        dam = calcular_desvio_absoluto_medio(teorica, exp)

        self.after(0, lambda: self._aplicar_resultados(
            teorica, exp, res, rotulo, dam, n_sim, eh_dado, qtd, total_ea
        ))

    def _aplicar_resultados(self, teorica, exp, res, rotulo,
                             dam, n_sim, eh_dado, qtd, total_ea):
        """Atualiza gráfico, log e tabela de estatísticas com os resultados."""
        self._sidebar.set_simulando(False)

        self._painel.desenhar_grafico(teorica, exp, rotulo)
        self._painel.exibir_log(res, eh_dado)

        # Monta a tabela de estatísticas
        chaves = sorted(set(teorica) | set(exp))
        linhas = [
            f"{'='*38}",
            f"  Experimento  : {'Dados' if eh_dado else 'Moedas'}",
            f"  Quantidade   : {qtd}",
            f"  Simulações   : {n_sim:,}",
            f"  Esp.Amostral : {total_ea:,} resultados",
            f"{'─'*38}",
            f"  {'Resultado':<14} {'Teórico':>8} {'Experim.':>9}",
            f"{'─'*38}",
        ]

        for k in chaves:
            vt = teorica.get(k, 0) * 100
            ve = exp.get(k, 0) * 100
            proximo = abs(vt - ve) < 1.0
            longe   = abs(vt - ve) > 5.0
            flag = " ✓" if proximo else (" ⚠" if longe else "  ")

            if not eh_dado:
                rotulo_k = "0 caras" if k == 0 else ("1 cara" if k == 1 else f"{k} caras")
            else:
                rotulo_k = f"Soma {k}"
            linhas.append(f"  {rotulo_k:<14} {vt:>7.2f}% {ve:>8.2f}%{flag}")

        precisao_str = (
            "Alta ✓  (< 1%)" if dam < 0.01 else
            ("Média   (1–5%)" if dam < 0.05 else "Baixa ⚠ (> 5%)")
        )
        linhas += [
            f"{'─'*38}",
            f"  DAM          : {dam*100:.3f}%",
            f"  Precisão     : {precisao_str}",
            f"{'='*38}",
            f"",
            f"  💡 DAM = Desvio Absoluto Médio",
            f"  Quanto menor, mais fiel à teoria.",
            f"  Aumente as simulações para reduzir.",
        ]

        self._sidebar.exibir_stats(linhas)

    # ── Diálogo de erro ───────────────────────────────────────────────────────

    def _mostrar_erro(self, mensagem: str):
        win = ctk.CTkToplevel(self)
        win.title("Aviso")
        win.geometry("380x160")
        win.configure(fg_color=FUNDO_CARD)
        win.grab_set()
        ctk.CTkLabel(win, text="⚠  " + mensagem,
                     font=ctk.CTkFont(size=13),
                     text_color=LARANJA, wraplength=330
                     ).pack(pady=32)
        ctk.CTkButton(win, text="OK", width=110,
                      fg_color=AZUL_CEU, command=win.destroy).pack()


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
