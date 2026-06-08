# Coins-Dice

# 🎲 Simulador de Probabilidade — Dados & Moedas

Simulador didático que compara a **probabilidade teórica** (calculada matematicamente)
com a **probabilidade experimental** (obtida por simulação de Monte Carlo).

---

## Requisito

```bash
pip install customtkinter
```

## Como executar

```bash
python main.py
```

---

## Estrutura do projeto

```
simulador_prob/
│
├── main.py                  # Ponto de entrada — inicializa o tema e abre a janela
│
├── core/
│   ├── __init__.py
│   └── matematica.py        # Toda a lógica matemática (sem dependência de UI)
│       ├── espaco_amostral_dados()
│       ├── prob_teorica_dados()
│       ├── prob_teorica_moedas()
│       ├── simular_dados()
│       ├── simular_moedas()
│       ├── frequencia_experimental()
│       ├── desvio_absoluto_medio()
│       └── classificar_precisao()
│
└── ui/
    ├── __init__.py
    ├── constantes.py        # Paleta de cores, fontes e dimensões
    ├── componentes.py       # Widgets reutilizáveis (PainelFormulas, SectionHeader)
    ├── grafico.py           # GraficoBarras — Canvas com barras duplas
    └── janela.py            # App — janela principal e orquestração
```

---

## Conceitos matemáticos abordados

| Conceito | Onde é usado |
|---|---|
| **Arranjo com Repetição** | `espaco_amostral_dados` — `faces^n` combinações |
| **Combinação Simples C(n,k)** | `prob_teorica_moedas` — `n! / (k!(n-k)!)` |
| **Probabilidade Elementar** | `prob_teorica_dados` — favoráveis / total |
| **Simulação de Monte Carlo** | `simular_dados` / `simular_moedas` |
| **Frequência Relativa** | `frequencia_experimental` — ocorrências / total |
| **Desvio Absoluto Médio** | `desvio_absoluto_medio` — convergência teoria × experimento |

---

## Como o gráfico funciona

Cada resultado possível gera **duas barras lado a lado**:

- **Barra azul** → probabilidade teórica (o que a matemática prevê)
- **Barra colorida** → probabilidade experimental (o que a simulação obteve)

A cor da barra experimental indica o desvio:

| Cor | Desvio | Significado |
|---|---|---|
| 🟢 Verde | < 4 % | Muito próximo da teoria |
| 🟡 Amarelo | 4 – 9 % | Aceitável |
| 🔴 Vermelho | > 9 % | Aumente as simulações |

---

## Dica pedagógica

> Quanto maior o número de simulações, mais a frequência experimental
> converge para a probabilidade teórica — isso é a **Lei dos Grandes Números**.
> Experimente 100 vs 50.000 simulações e observe a diferença no gráfico.
