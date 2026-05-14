import json
import uuid
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any

from config import DATA_PATH
from core.template import TEMPLATE_TAREFAS
from core.datas import calcular_datas


def _caminho() -> Path:
    p = Path(DATA_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def carregar_projetos() -> list[dict[str, Any]]:
    caminho = _caminho()
    if not caminho.exists():
        return []
    with caminho.open("r", encoding="utf-8") as f:
        return json.load(f)


def salvar_projetos(projetos: list[dict[str, Any]]) -> None:
    with _caminho().open("w", encoding="utf-8") as f:
        json.dump(projetos, f, ensure_ascii=False, indent=2)


def criar_projeto(
    nome: str,
    analista: str,
    data_inicio: date,
    flags: list[str],
    endereco: str = "",
    numero_unidades: int = 0,
) -> dict[str, Any]:
    tarefas_base = deepcopy(TEMPLATE_TAREFAS)
    tarefas_processadas = []

    for t in tarefas_base:
        cond = t.get("condicional")
        t["status"] = "Não iniciado" if (cond is None or cond in flags) else "Não aplicável"
        t["duracao_real"] = None
        t["observacao"] = ""
        t["numero_processo"] = ""
        t["data_inicio_manual"] = None
        t["data_fim_manual"] = None
        tarefas_processadas.append(t)

    tarefas_com_datas = calcular_datas(tarefas_processadas, data_inicio)

    return {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "analista": analista,
        "endereco": endereco,
        "numero_unidades": numero_unidades,
        "data_inicio": data_inicio.isoformat(),
        "flags": flags,
        "tarefas": tarefas_com_datas,
        "criado_em": date.today().isoformat(),
    }


def atualizar_tarefa(
    projetos: list[dict],
    projeto_id: str,
    tarefa_id: str,
    campos: dict[str, Any],
) -> list[dict]:
    for projeto in projetos:
        if projeto["id"] != projeto_id:
            continue
        for tarefa in projeto["tarefas"]:
            if tarefa["id"] != tarefa_id:
                continue
            for chave, valor in campos.items():
                tarefa[chave] = valor
            if "data_inicio_manual" in campos:
                projeto["tarefas"] = calcular_datas(
                    projeto["tarefas"],
                    date.fromisoformat(projeto["data_inicio"]),
                )
            break
        break
    return projetos


def progresso_projeto(projeto: dict) -> float:
    tarefas = [t for t in projeto["tarefas"] if t["status"] != "Não aplicável"]
    if not tarefas:
        return 0.0
    concluidas = sum(1 for t in tarefas if t["status"] == "Concluído")
    return round(concluidas / len(tarefas) * 100, 1)