import customtkinter as ctk
import tkinter as tk
import random
import math
import threading
from collections import Counter
from itertools import product as iter_product

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


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 1 — MATEMÁTICA
# Todas as funções matemáticas ficam aqui, separadas da interface.
# ══════════════════════════════════════════════════════════════════════════════

def calcular_espaco_amostral_dados(n_dados: int, n_faces: int) -> list:
    """
    Gera todos os resultados possíveis ao lançar n_dados dados de n_faces lados.

    Usa Arranjo com Repetição (Análise Combinatória):
        Total de resultados = n_faces ^ n_dados
    Exemplo: 2 dados de 6 faces → 6² = 36 combinações.

    Retorna uma lista de tuplas, onde cada tupla é um resultado possível.
    Ex: [(1,1), (1,2), ..., (6,6)]
    """
    return list(iter_product(range(1, n_faces + 1), repeat=n_dados))


def calcular_probabilidade_teorica_dados(n_dados: int, n_faces: int) -> dict:
    """
    Calcula a probabilidade TEÓRICA de cada soma possível ao lançar os dados.

    Fórmula (Probabilidade Elementar):
        P(soma = s) = nº de combinações que resultam em s  /  total de combinações

    Exemplo com 2d6:
        P(soma=7) = 6/36 ≈ 16.7%  (as 6 combinações: 1+6, 2+5, 3+4, 4+3, 5+2, 6+1)

    Retorna um dicionário {soma: probabilidade}.
    """
    espaco = calcular_espaco_amostral_dados(n_dados, n_faces)
    total  = len(espaco)                          # = n_faces ^ n_dados
    contagem = Counter(sum(combo) for combo in espaco)
    return {soma: contagem[soma] / total for soma in sorted(contagem)}


def calcular_probabilidade_teorica_moedas(n_moedas: int) -> dict:
    """
    Calcula a probabilidade TEÓRICA de obter exatamente k caras em n_moedas lançamentos.

    Fórmula (Análise Combinatória + Probabilidade):
        P(k caras) = C(n, k) / 2^n
        onde C(n, k) = n! / (k! × (n-k)!)  ← Combinação simples

    Exemplo com 3 moedas:
        P(0 caras) = C(3,0)/8 = 1/8 = 12.5%
        P(1 cara)  = C(3,1)/8 = 3/8 = 37.5%
        P(2 caras) = C(3,2)/8 = 3/8 = 37.5%
        P(3 caras) = C(3,3)/8 = 1/8 = 12.5%

    Retorna um dicionário {nº de caras: probabilidade}.
    """
    total = 2 ** n_moedas
    return {k: math.comb(n_moedas, k) / total for k in range(n_moedas + 1)}


def executar_simulacao_dados(n_dados: int, n_faces: int, n_simulacoes: int) -> list:
    """
    Simula n_simulacoes lançamentos de n_dados dados de n_faces lados.

    Cada lançamento gera uma soma aleatória entre n_dados e n_dados*n_faces.
    Retorna uma lista com a soma de cada lançamento.
    """
    return [
        sum(random.randint(1, n_faces) for _ in range(n_dados))
        for _ in range(n_simulacoes)
    ]


def executar_simulacao_moedas(n_moedas: int, n_simulacoes: int) -> list:
    """
    Simula n_simulacoes rodadas, cada uma lançando EXATAMENTE n_moedas moedas.

    Cada moeda tem 50% de chance de cara.
    Retorna uma lista com o nº de caras obtidas em cada rodada.

    CORREÇÃO APLICADA: o parâmetro n_moedas controla o range() interno,
    garantindo que 1 moeda = 1 lançamento por rodada (não 2).
    """
    resultados = []
    for _ in range(n_simulacoes):
        caras = sum(1 for _ in range(n_moedas) if random.random() < 0.5)
        resultados.append(caras)
    return resultados


def calcular_frequencia_experimental(resultados: list) -> dict:
    """
    Converte os resultados brutos em probabilidade experimental (frequência relativa).

    Fórmula:
        P_experimental(x) = nº de vezes que x apareceu / total de simulações

    Quanto maior o número de simulações, mais próxima da probabilidade teórica.
    """
    total    = len(resultados)
    contagem = Counter(resultados)
    return {k: contagem[k] / total for k in sorted(contagem)}


def calcular_desvio_absoluto_medio(teorica: dict, experimental: dict) -> float:
    """
    Mede o quanto o resultado experimental desviou da teoria, em média.

    Fórmula:
        DAM = Σ |P_teórico(k) - P_experimental(k)| / nº de resultados

    DAM próximo de 0% → simulação muito fiel à teoria.
    DAM alto → poucas simulações ou variação aleatória grande.
    """
    chaves = set(teorica) | set(experimental)
    desvios = [abs(teorica.get(k, 0) - experimental.get(k, 0)) for k in chaves]
    return sum(desvios) / len(desvios) if desvios else 0.0


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 2 — GRÁFICO DE BARRAS (Canvas puro dentro de um CTkFrame)
# ══════════════════════════════════════════════════════════════════════════════

class GraficoBarras(tk.Canvas):


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


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 3 — PAINEL DE FÓRMULAS (exibe os cálculos em linguagem clara)
# ══════════════════════════════════════════════════════════════════════════════

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
                                  font=ctk.CTkFont("Times new roman", 14),
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


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 4 — APLICAÇÃO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

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
        self.title("🎲  Simulador de Probabilidade — Coins & Dice")
        self.geometry("1180x820")
        self.minsize(980, 680)
        self.configure(fg_color=FUNDO_APP)

        # Estado interno do slider (inteiro garantido)
        self._qtd_int = 2

        # Constrói primeiro o painel principal (que contém _painel_form)
        # e só depois a sidebar (que chama _atualizar_formulas)
        self._build_cabecalho()
        self._build_corpo()      # cria sidebar + painel principal na ordem certa

    # ── CABEÇALHO ────────────────────────────────────────────────────────────

    def _build_cabecalho(self):
        hdr = ctk.CTkFrame(self, fg_color=AZUL_ROYAL, corner_radius=0, height=70)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr,
                     text="🎲  Simulador de Probabilidade  —  Coins & Dice",
                     font=ctk.CTkFont("Georgia", 26, "bold"),
                     text_color=AREIA
                     ).pack(side="left", padx=24, pady=14)

        ctk.CTkLabel(hdr,
                     text="Probabilidade Teórica  ×  Experimental",
                     font=ctk.CTkFont(size=12),
                     text_color=TEXTO_DIM
                     ).pack(side="right", padx=24)

        # Linha decorativa dourada
        ctk.CTkFrame(self, fg_color=LARANJA, height=2,
                     corner_radius=0).pack(fill="x")

    # ── CORPO (sidebar + painel principal) ───────────────────────────────────

    def _build_corpo(self):
        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.pack(fill="both", expand=True, padx=20, pady=14)

        # IMPORTANTE: painel principal criado ANTES da sidebar
        # para que _painel_form exista quando _atualizar_formulas for chamado
        self._build_painel_principal(corpo)
        self._build_sidebar(corpo)

    # ── PAINEL PRINCIPAL (direita) ────────────────────────────────────────────

    def _build_painel_principal(self, pai):
        """
        Contém três áreas empilhadas:
          1. Painel de Fórmulas  — mostra o espaço amostral e as fórmulas usadas
          2. Gráfico de Barras   — compara teórico vs experimental visualmente
          3. Log de Resultados   — exibe os últimos valores gerados
        """
        main = ctk.CTkFrame(pai, fg_color="transparent")
        main.pack(side="right", fill="both", expand=True)

        # 1. Painel de fórmulas
        self._painel_form = PainelFormulas(main)
        self._painel_form.pack(fill="x", pady=(0, 10))

        # 2. Título do gráfico
        ctk.CTkLabel(main,
                     text="📈  Gráfico ",
                     font=ctk.CTkFont("Georgia", 12, "bold"),
                     text_color=LARANJA
                     ).pack(anchor="w", pady=(0, 6))

        # 3. Gráfico de barras
        graf_container = ctk.CTkFrame(main, fg_color=FUNDO_APP,
                                       corner_radius=14,
                                       border_color=AZUL_CEU, border_width=1)
        graf_container.pack(fill="both", expand=True, pady=(0, 10))

        self._grafico = GraficoBarras(graf_container)
        self._grafico.pack(fill="both", expand=True, padx=4, pady=4)

        # 4. Log de amostra
        ctk.CTkLabel(main,
                     text="🔎  Amostra — últimos valores gerados pela simulação:",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXTO_DIM
                     ).pack(anchor="w")

        self._txt_log = ctk.CTkTextbox(main, height=50,
                                        font=ctk.CTkFont("Courier New", 11),
                                        fg_color=FUNDO_CARD,
                                        text_color=AREIA,
                                        corner_radius=10,
                                        state="disabled")
        self._txt_log.pack(fill="x", pady=(4, 0))

    # ── SIDEBAR (esquerda) ────────────────────────────────────────────────────

    def _build_sidebar(self, pai):
        """
        Painel de configuração com 4 passos guiados:
          Passo 1 — Tipo de experimento (Dados ou Moedas)
          Passo 2 — Quantidade (slider com valor em destaque)
          Passo 3 — Faces por dado (somente para dados)
          Passo 4 — Número de simulações
          + Botão SIMULAR e tabela de resultados
        """
        side = ctk.CTkScrollableFrame(pai, width=312, fg_color=FUNDO_CARD,
                                      corner_radius=16,
                                      scrollbar_button_color=AZUL_CEU)
        side.pack(side="left", fill="y", padx=(0, 14))

        # ── helpers locais ──
        def titulo_secao(txt):
            ctk.CTkLabel(side, text=txt,
                         font=ctk.CTkFont("Georgia", 12, "bold"),
                         text_color=LARANJA
                         ).pack(anchor="w", padx=16, pady=(14, 2))
            ctk.CTkFrame(side, fg_color=LARANJA, height=1,
                         corner_radius=0).pack(fill="x", padx=16, pady=(0, 8))

        def label(txt, dim=False):
            ctk.CTkLabel(side, text=txt,
                         font=ctk.CTkFont(size=11),
                         text_color=TEXTO_DIM if dim else AREIA
                         ).pack(anchor="w", padx=16)

        # ════════════════════════════════════
        titulo_secao("⚙  Configure o Experimento")

        # ── PASSO 1 — Tipo ──
        label("Passo 1 — O que você quer lançar?")
        self._var_modo = ctk.StringVar(value="🎲  Dados")
        ctk.CTkSegmentedButton(
            side,
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
        self._lbl_passo2 = ctk.CTkLabel(side,
                                         text="Passo 2 — Quantos dados? ",
                                         font=ctk.CTkFont(size=11), text_color=AREIA)
        self._lbl_passo2.pack(anchor="w", padx=16)


        # Número em destaque (mostra o valor exato do slider)
        self._lbl_valor_qtd = ctk.CTkLabel(side, text="2",
                                            font=ctk.CTkFont("Courier New", 46, "bold"),
                                            text_color=LARANJA)
        self._lbl_valor_qtd.pack(pady=(6, 0))

        # Slider — usa DoubleVar; arredondamos manualmente no callback
        self._slider_var = tk.DoubleVar(value=2.0)
        self._slider = ctk.CTkSlider(
            side, from_=1, to=6, number_of_steps=5,
            variable=self._slider_var,
            button_color=LARANJA,
            button_hover_color="#c9a84c",
            progress_color=AZUL_CEU,
            fg_color="#0d1f35",
            command=self._ao_mover_slider
        )
        self._slider.pack(fill="x", padx=16, pady=(0, 2))

        # Rótulos mín/máx do slider
        linha_min_max = ctk.CTkFrame(side, fg_color="transparent")
        linha_min_max.pack(fill="x", padx=16, pady=(0, 14))
        ctk.CTkLabel(linha_min_max, text="mín: 1",
                     font=ctk.CTkFont(size=10), text_color=TEXTO_DIM).pack(side="left")
        self._lbl_max = ctk.CTkLabel(linha_min_max, text="máx: 6",
                                      font=ctk.CTkFont(size=10), text_color=TEXTO_DIM)
        self._lbl_max.pack(side="right")

        # ── PASSO 3 — Faces (somente dados) ──
        self._lbl_passo3 = ctk.CTkLabel(side,
                                         text="Passo 3 — Quantas faces tem cada dado?",
                                         font=ctk.CTkFont(size=11), text_color=AREIA)
        self._lbl_passo3.pack(anchor="w", padx=16)


        self._var_faces = ctk.StringVar(value="6")
        self._seg_faces = ctk.CTkSegmentedButton(
            side,
            values=["4", "6", "8", "10", "12", "20"],
            variable=self._var_faces,
            command=lambda _: self._atualizar_formulas(),
            selected_color=AZUL_CEU,
            unselected_color=AZUL_ROYAL,
            fg_color=AZUL_ROYAL,
            text_color=AREIA,
            height=32
        )
        self._seg_faces.pack(fill="x", padx=16, pady=(6, 16))

        # ── PASSO 4 — Simulações ──
        label("Passo 4 — Quantas simulações executar?")


        # Botões de atalho rápido
        for grupo in [(100, 500, 1000), (5000, 10000, 50000)]:
            linha = ctk.CTkFrame(side, fg_color="transparent")
            linha.pack(fill="x", padx=16, pady=2)
            for n in grupo:
                ctk.CTkButton(
                    linha, text=f"{n:,}", width=76, height=28,
                    font=ctk.CTkFont(size=11),
                    fg_color=AZUL_ROYAL, hover_color=AZUL_CEU,
                    text_color=AREIA, corner_radius=8,
                    command=lambda v=n: self._definir_simulacoes(v)
                ).pack(side="left", padx=2)

        label(" Digite um valor personalizado:", dim=True)
        self._var_sim = tk.StringVar(value="1000")
        ctk.CTkEntry(side,
                     textvariable=self._var_sim,
                     width=170, height=38,
                     font=ctk.CTkFont("Courier New", 16, "bold"),
                     fg_color=AZUL_ROYAL, border_color=AZUL_CEU,
                     text_color=LARANJA,
                     placeholder_text="ex: 2000"
                     ).pack(anchor="w", padx=16, pady=(4, 16))

        # ── Botão principal ──
        self._btn_simular = ctk.CTkButton(
            side,
            text="▶  SIMULAR AGORA",
            font=ctk.CTkFont("Georgia", 15, "bold"),
            fg_color=LARANJA, hover_color="#c9a84c",
            text_color=AZUL_ROYAL,
            height=54, corner_radius=14,
            command=self._executar_simulacao
        )
        self._btn_simular.pack(fill="x", padx=16, pady=(0, 8))

        # Barra de progresso (aparece só durante a simulação)
        self._barra_prog = ctk.CTkProgressBar(side, mode="indeterminate",
                                               progress_color=LARANJA,
                                               fg_color=AZUL_ROYAL, height=6)

        # ── Seção de resultados ──
        titulo_secao("📊  Resultados da Simulação")
        label("Teórico = calculado pela fórmula matemática", dim=True)
        label("Experim. = obtido nas simulações aleatórias", dim=True)
        label("✓ desvio < 1%  |  ⚠ desvio > 5%", dim=True)

        self._txt_stats = ctk.CTkTextbox(
            side, height=260,
            font=ctk.CTkFont("Courier New", 11),
            fg_color=FUNDO_APP,
            text_color=AREIA,
            border_color=AZUL_CEU, border_width=1,
            corner_radius=10,
            state="disabled"
        )
        self._txt_stats.pack(fill="x", padx=16, pady=(6, 16))

        # Primeira atualização das fórmulas (agora _painel_form já existe)
        self._atualizar_formulas()

    # ══════════════════════════════════════════════════════════════════════════
    # CALLBACKS DE INTERFACE
    # ══════════════════════════════════════════════════════════════════════════

    def _ao_mudar_modo(self, _=None):
        """
        Chamado quando o usuário troca entre Dados e Moedas.
        Ajusta o slider, habilita/desabilita o seletor de faces e atualiza as fórmulas.
        """
        eh_dado = self._var_modo.get().startswith("🎲")

        if eh_dado:
            self._lbl_passo2.configure(text="Passo 2 — Quantos dados? ")
            self._slider.configure(to=6, number_of_steps=5)
            self._lbl_max.configure(text="máx: 6")
            maximo = 6
        else:
            self._lbl_passo2.configure(text="Passo 2 — Quantas moedas? ")
            self._slider.configure(to=8, number_of_steps=7)
            self._lbl_max.configure(text="máx: 8")
            maximo = 8

        # Habilita/desabilita o seletor de faces
        self._seg_faces.configure(state="normal" if eh_dado else "disabled")
        self._lbl_passo3.configure(text_color=AREIA if eh_dado else TEXTO_DIM)

        # Corrige valor caso exceda o novo máximo
        if self._qtd_int > maximo:
            self._qtd_int = maximo
            self._slider_var.set(float(maximo))
            self._lbl_valor_qtd.configure(text=str(maximo))

        self._atualizar_formulas()

    def _ao_mover_slider(self, valor):
        """
        Callback do slider: arredonda o valor float para inteiro e atualiza a interface.
        Isso CORRIGE o bug onde 1 moeda era interpretado como 2.
        """
        inteiro = int(round(float(valor)))     # arredondamento explícito
        self._qtd_int = inteiro                # guarda o inteiro
        self._lbl_valor_qtd.configure(text=str(inteiro))
        self._atualizar_formulas()

    def _definir_simulacoes(self, n: int):
        """Define o número de simulações pelo botão de atalho."""
        self._var_sim.set(str(n))
        self._atualizar_formulas()

    def _atualizar_formulas(self):
        """
        Atualiza o painel de fórmulas com os valores atuais.
        Chamado toda vez que qualquer configuração muda.
        """
        eh_dado = self._var_modo.get().startswith("🎲")
        faces   = int(self._var_faces.get())
        try:
            n_sim = int(self._var_sim.get())
        except ValueError:
            n_sim = 0
        # Usa self._qtd_int (inteiro garantido) — nunca o valor bruto do slider
        self._painel_form.atualizar(eh_dado, self._qtd_int, faces, n_sim)

    # ══════════════════════════════════════════════════════════════════════════
    # SIMULAÇÃO (executa em thread separada para não travar a interface)
    # ══════════════════════════════════════════════════════════════════════════

    def _executar_simulacao(self):
        """Valida os inputs e inicia a simulação em background."""
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

        threading.Thread(
            target=self._rodar_em_background,
            args=(n_sim,),
            daemon=True
        ).start()

    def _rodar_em_background(self, n_sim: int):
        """
        Executa os cálculos em uma thread separada.
        Ao terminar, agenda a atualização da interface na thread principal.
        """
        eh_dado = self._var_modo.get().startswith("🎲")
        qtd     = self._qtd_int    # inteiro garantido — SEM arredondamento duplo

        if eh_dado:
            faces    = int(self._var_faces.get())
            res      = executar_simulacao_dados(qtd, faces, n_sim)
            teorica  = calcular_probabilidade_teorica_dados(qtd, faces)
            exp      = calcular_frequencia_experimental(res)
            rotulo   = f"Soma  ({qtd}d{faces})"
            total_ea = faces ** qtd
        else:
            res      = executar_simulacao_moedas(qtd, n_sim)   # qtd exato
            teorica  = calcular_probabilidade_teorica_moedas(qtd)
            exp      = calcular_frequencia_experimental(res)
            rotulo   = "Caras"
            total_ea = 2 ** qtd

        dam = calcular_desvio_absoluto_medio(teorica, exp)

        # Agenda atualização na thread principal (obrigatório no Tkinter)
        self.after(0, lambda: self._aplicar_resultados(
            teorica, exp, res, rotulo, dam, n_sim, eh_dado, qtd, total_ea
        ))

    def _aplicar_resultados(self, teorica, exp, res, rotulo,
                             dam, n_sim, eh_dado, qtd, total_ea):
        """Atualiza gráfico, log e tabela de estatísticas com os resultados."""

        # Para a barra de progresso
        self._barra_prog.stop()
        self._barra_prog.pack_forget()
        self._btn_simular.configure(state="normal", text="▶  SIMULAR AGORA")

        # Atualiza o gráfico
        self._grafico.desenhar(teorica, exp, rotulo)

        # Atualiza o log de amostra
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
            # Lógica booleana: classifica o desvio
            proximo = abs(vt - ve) < 1.0    # booleano: desvio aceitável?
            longe   = abs(vt - ve) > 5.0    # booleano: desvio alto?
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

        self._txt_stats.configure(state="normal")
        self._txt_stats.delete("0.0", "end")
        self._txt_stats.insert("end", "\n".join(linhas))
        self._txt_stats.configure(state="disabled")

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
