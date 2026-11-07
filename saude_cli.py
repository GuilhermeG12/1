"""Pergunte sobre seus dados do Samsung Health pelo terminal.

Exemplos:
  python saude_cli.py PASTA passos semana
  python saude_cli.py PASTA passos hoje
  python saude_cli.py PASTA coracao
  python saude_cli.py PASTA atividade
  python saude_cli.py PASTA sono
  python saude_cli.py PASTA resumo
"""

import sys

from saude import DadosSamsung
from saude import respostas


def main(args: list[str]) -> int:
    if len(args) < 2:
        print(__doc__)
        return 1
    dados = DadosSamsung(args[0])
    comando = args[1].lower()
    if comando == "passos":
        print(respostas.passos(dados, args[2] if len(args) > 2 else "semana"))
    elif comando in ("coracao", "coração", "frequencia"):
        print(respostas.coracao(dados))
    elif comando == "atividade":
        print(respostas.atividade(dados))
    elif comando == "sono":
        print(respostas.sono(dados))
    elif comando == "resumo":
        print(respostas.resumo(dados))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
