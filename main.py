"""
╔══════════════════════════════════════════════════════════════╗
║         Simulador de Probabilidade — Dados & Moedas          ║
║                                                              ║
║  Estrutura do projeto:                                       ║
║    main.py              ← ponto de entrada (este arquivo)    ║
║    core/                                                     ║
║      matematica.py      ← toda a lógica matemática           ║
║    ui/                                                       ║
║      constantes.py      ← paleta de cores e fontes           ║
║      componentes.py     ← widgets reutilizáveis              ║
║      grafico.py         ← gráfico de barras (Canvas)         ║
║      janela.py          ← janela principal (App)             ║
║                                                              ║
║  Requisito:  pip install customtkinter                       ║
║  Execução:   python main.py                                  ║
╚══════════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
from ui.janela import App


def main() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
