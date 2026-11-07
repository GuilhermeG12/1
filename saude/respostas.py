"""Respostas em português, usadas pelo terminal e pelo servidor MCP."""

from __future__ import annotations

from datetime import date, timedelta

from .leitor import DadosSamsung


def _fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def passos(dados: DadosSamsung, periodo: str = "semana", hoje: date | None = None) -> str:
    hoje = hoje or date.today()
    if periodo == "hoje":
        inicio, nome = hoje, "hoje"
    elif periodo == "ontem":
        inicio = hoje = hoje - timedelta(days=1)
        nome = "ontem"
    elif periodo == "mes":
        inicio, nome = hoje.replace(day=1), "este mês"
    else:
        inicio, nome = hoje - timedelta(days=hoje.weekday()), "esta semana"
    total = dados.passos_periodo(inicio, hoje)
    texto = f"Você deu {_fmt(total)} passos {nome}."
    if periodo in ("semana", "mes"):
        dias = (hoje - inicio).days + 1
        texto += f" Média de {_fmt(total // dias)} por dia."
    dias = dados.passos_por_dia()
    if dias:
        ultimo = max(dias)
        if ultimo < inicio:
            texto += f" (Atenção: o último dado exportado é de {ultimo:%d/%m/%Y}.)"
    return texto


def coracao(dados: DadosSamsung) -> str:
    r = dados.ultima_frequencia()
    if not r:
        return "Não encontrei registros de frequência cardíaca."
    return f"Sua última frequência cardíaca foi {r['bpm']} bpm, em {r['quando']:%d/%m/%Y às %H:%M}."


def atividade(dados: DadosSamsung) -> str:
    a = dados.ultima_atividade()
    if not a:
        return "Não encontrei atividades registradas."
    texto = f"Sua última atividade foi {a['tipo']}, em {a['quando']:%d/%m/%Y às %H:%M}, por {a['minutos']} min"
    if a["distancia_km"]:
        texto += f", {a['distancia_km']} km"
    if a["calorias"]:
        texto += f", {a['calorias']} kcal"
    return texto + "."


def sono(dados: DadosSamsung) -> str:
    s = dados.ultimo_sono()
    if not s:
        return "Não encontrei registros de sono."
    if s["horas"] is None:
        return f"Seu último sono começou em {s['inicio']:%d/%m/%Y às %H:%M}."
    return f"Você dormiu {s['horas']} h na última noite registrada ({s['inicio']:%d/%m %H:%M} até {s['fim']:%H:%M})."


def resumo(dados: DadosSamsung, hoje: date | None = None) -> str:
    return "\n".join([
        passos(dados, "hoje", hoje),
        passos(dados, "semana", hoje),
        coracao(dados),
        atividade(dados),
        sono(dados),
    ])
