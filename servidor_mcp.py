"""Servidor MCP: deixa o Claude (app de desktop) consultar seus dados.

Defina a variável SAMSUNG_HEALTH_PASTA com o caminho da pasta exportada.
Instale antes: pip install mcp
"""

import os

try:  # mcp 2.x
    from mcp.server.mcpserver import MCPServer as Servidor
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as Servidor

from saude import DadosSamsung
from saude import respostas

mcp = Servidor("samsung-health")


def _dados() -> DadosSamsung:
    return DadosSamsung(os.environ["SAMSUNG_HEALTH_PASTA"])


@mcp.tool()
def passos(periodo: str = "semana") -> str:
    """Quantos passos o usuário deu. periodo: hoje, ontem, semana ou mes."""
    return respostas.passos(_dados(), periodo)


@mcp.tool()
def ultima_frequencia_cardiaca() -> str:
    """Última frequência cardíaca registrada."""
    return respostas.coracao(_dados())


@mcp.tool()
def ultima_atividade() -> str:
    """Última atividade física (exercício) registrada."""
    return respostas.atividade(_dados())


@mcp.tool()
def ultimo_sono() -> str:
    """Último registro de sono."""
    return respostas.sono(_dados())


@mcp.tool()
def resumo() -> str:
    """Resumo: passos de hoje e da semana, coração, atividade e sono."""
    return respostas.resumo(_dados())


if __name__ == "__main__":
    mcp.run()
