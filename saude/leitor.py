"""Lê a pasta exportada do Samsung Health ("Baixar dados pessoais").

Só usa a biblioteca padrão do Python. Os arquivos da Samsung são CSV com:
  linha 1: metadados (ex.: "com.samsung.shealth.tracker.heart_rate,6315005,3")
  linha 2: nomes das colunas (às vezes com prefixo "com.samsung.health.xxx.")
  resto:   os registros
"""

from __future__ import annotations

import csv
import io
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# Códigos de exercício mais comuns do Samsung Health.
TIPOS_EXERCICIO = {
    0: "Exercício personalizado",
    1001: "Caminhada",
    1002: "Corrida",
    3001: "Beisebol",
    4003: "Futebol",
    6001: "Musculação",
    9002: "Yoga",
    10007: "Pilates",
    11007: "Ciclismo",
    13001: "Trilha",
    14001: "Natação",
    15002: "Esteira",
    15003: "Bicicleta ergométrica",
    15004: "Elíptico",
    15005: "Remo",
}


@dataclass
class Registro:
    quando: datetime  # horário local
    dados: dict


def _ler_csv(caminho: Path) -> list[dict]:
    texto = caminho.read_text(encoding="utf-8-sig", errors="replace")
    linhas = texto.splitlines()
    if len(linhas) >= 2:
        primeira = next(csv.reader([linhas[0]]))
        segunda = next(csv.reader([linhas[1]]))
        if len(primeira) <= 3 and len(segunda) > 3:
            linhas = linhas[1:]  # pula a linha de metadados
    leitor = csv.reader(io.StringIO("\n".join(linhas)))
    try:
        cabecalho = [c.strip().split(".")[-1] for c in next(leitor)]
    except StopIteration:
        return []
    registros = []
    for linha in leitor:
        if not any(v.strip() for v in linha):
            continue
        registros.append({c: v.strip() for c, v in zip(cabecalho, linha) if c})
    return registros


def _fuso(texto: str | None) -> timezone:
    m = re.fullmatch(r"UTC([+-])(\d{2}):?(\d{2})", (texto or "").strip())
    if not m:
        return timezone.utc
    minutos = int(m.group(2)) * 60 + int(m.group(3))
    return timezone(timedelta(minutes=minutos if m.group(1) == "+" else -minutos))


def _data_hora(valor: str | None, offset: str | None = None) -> datetime | None:
    """Converte o horário (salvo em UTC) para o horário local do registro."""
    if not valor:
        return None
    valor = valor.strip()
    try:
        if valor.isdigit():  # milissegundos desde 1970
            dt = datetime.fromtimestamp(int(valor) / 1000, tz=timezone.utc)
        else:
            dt = datetime.fromisoformat(valor.replace("Z", "")[:23]).replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return dt.astimezone(_fuso(offset)).replace(tzinfo=None)


def _numero(valor: str | None) -> float | None:
    try:
        return float(valor) if valor not in (None, "") else None
    except ValueError:
        return None


class DadosSamsung:
    def __init__(self, pasta: str | Path):
        self.pasta = Path(pasta).expanduser()
        if not self.pasta.is_dir():
            raise FileNotFoundError(f"Pasta não encontrada: {self.pasta}")

    def _arquivos(self, nome: str) -> list[Path]:
        return sorted(
            p for p in self.pasta.rglob("*.csv")
            if p.name.startswith(nome + ".") or p.name == nome + ".csv"
        )

    def _registros(self, nome: str, campo_tempo: str = "start_time") -> list[Registro]:
        saida = []
        for arq in self._arquivos(nome):
            for r in _ler_csv(arq):
                quando = _data_hora(r.get(campo_tempo), r.get("time_offset"))
                if quando:
                    saida.append(Registro(quando, r))
        return sorted(saida, key=lambda r: r.quando)

    # ---------- Passos ----------
    def passos_por_dia(self) -> dict[date, int]:
        # 1) resumo diário (source_type -2 = soma de todos os aparelhos)
        dias: dict[date, int] = {}
        for arq in self._arquivos("com.samsung.shealth.step_daily_trend"):
            linhas = _ler_csv(arq)
            tem_total = any(r.get("source_type") == "-2" for r in linhas)
            for r in linhas:
                if tem_total and r.get("source_type") != "-2":
                    continue
                dt = _data_hora(r.get("day_time"))  # meia-noite em UTC = o dia
                n = _numero(r.get("count"))
                if dt and n is not None:
                    dias[dt.date()] = max(dias.get(dt.date(), 0), int(n))
        if dias:
            return dict(sorted(dias.items()))
        # 2) resumo do pedômetro
        for arq in self._arquivos("com.samsung.shealth.tracker.pedometer_day_summary"):
            for r in _ler_csv(arq):
                dt = _data_hora(r.get("day_time"))
                n = _numero(r.get("step_count"))
                if dt and n is not None:
                    dias[dt.date()] = max(dias.get(dt.date(), 0), int(n))
        if dias:
            return dict(sorted(dias.items()))
        # 3) registros soltos de passos
        soma: dict[date, int] = defaultdict(int)
        for reg in self._registros("com.samsung.health.step_count"):
            n = _numero(reg.dados.get("count"))
            if n is not None:
                soma[reg.quando.date()] += int(n)
        return dict(sorted(soma.items()))

    def passos_periodo(self, inicio: date, fim: date) -> int:
        return sum(n for d, n in self.passos_por_dia().items() if inicio <= d <= fim)

    # ---------- Coração ----------
    def frequencias_cardiacas(self) -> list[Registro]:
        return [
            r for r in self._registros("com.samsung.shealth.tracker.heart_rate")
            if _numero(r.dados.get("heart_rate"))
        ]

    def ultima_frequencia(self) -> dict | None:
        regs = self.frequencias_cardiacas()
        if not regs:
            return None
        r = regs[-1]
        return {"quando": r.quando, "bpm": int(_numero(r.dados["heart_rate"]))}

    # ---------- Exercícios ----------
    def atividades(self) -> list[dict]:
        saida = []
        for r in self._registros("com.samsung.shealth.exercise"):
            d = r.dados
            codigo = int(_numero(d.get("exercise_type")) or 0)
            duracao_ms = _numero(d.get("duration")) or 0
            saida.append({
                "quando": r.quando,
                "tipo": d.get("custom_type") or TIPOS_EXERCICIO.get(codigo, f"Exercício {codigo}"),
                "minutos": round(duracao_ms / 60000),
                "distancia_km": round((_numero(d.get("distance")) or 0) / 1000, 2),
                "calorias": round(_numero(d.get("calorie")) or 0),
            })
        return saida

    def ultima_atividade(self) -> dict | None:
        lista = self.atividades()
        return lista[-1] if lista else None

    # ---------- Sono ----------
    def ultimo_sono(self) -> dict | None:
        regs = self._registros("com.samsung.shealth.sleep")
        if not regs:
            return None
        r = regs[-1]
        fim = _data_hora(r.dados.get("end_time"), r.dados.get("time_offset"))
        horas = round((fim - r.quando).total_seconds() / 3600, 1) if fim else None
        return {"inicio": r.quando, "fim": fim, "horas": horas}
