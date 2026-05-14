from datetime import date, timedelta
from typing import Any


def calcular_datas(tarefas: list[dict[str, Any]], data_inicio: date) -> list[dict[str, Any]]:
    mapa: dict[str, dict] = {t["id"]: t for t in tarefas}
    cache_fim: dict[str, date] = {}

    def fim_de(tarefa_id: str) -> date:
        if tarefa_id in cache_fim:
            return cache_fim[tarefa_id]
        tarefa = mapa.get(tarefa_id)
        if not tarefa:
            return data_inicio
        deps = [d for d in tarefa.get("dependencias", []) if d in mapa]
        inicio = max(fim_de(d) for d in deps) if deps else data_inicio
        fim = inicio + timedelta(days=tarefa["duracao_dias"])
        cache_fim[tarefa_id] = fim
        return fim

    resultado = []
    for t in tarefas:
        deps = [d for d in t.get("dependencias", []) if d in mapa]
        inicio_t = max(fim_de(d) for d in deps) if deps else data_inicio
        fim_t = inicio_t + timedelta(days=t["duracao_dias"])
        cache_fim[t["id"]] = fim_t

        entrada = dict(t)
        if t.get("data_inicio_manual"):
            try:
                inicio_t = date.fromisoformat(t["data_inicio_manual"])
                fim_t = inicio_t + timedelta(days=t["duracao_dias"])
            except ValueError:
                pass

        entrada["data_inicio_calc"] = inicio_t.isoformat()
        entrada["data_fim_calc"] = fim_t.isoformat()
        resultado.append(entrada)

    return resultado