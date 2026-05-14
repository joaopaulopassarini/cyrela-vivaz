import json
from pathlib import Path
from core.template import TEMPLATE_TAREFAS

MAPA = {t["id"]: {"grupo": t["grupo"], "subgrupo": t.get("subgrupo")} for t in TEMPLATE_TAREFAS}

caminho = Path("data/projetos_cyrela.json")
with caminho.open(encoding="utf-8") as f:
    projetos = json.load(f)

for projeto in projetos:
    for tarefa in projeto["tarefas"]:
        tid = tarefa.get("id")
        if tid in MAPA:
            tarefa["grupo"] = MAPA[tid]["grupo"]
            tarefa["subgrupo"] = MAPA[tid]["subgrupo"]
            tarefa["fase"] = MAPA[tid]["grupo"]

with caminho.open("w", encoding="utf-8") as f:
    json.dump(projetos, f, ensure_ascii=False, indent=2)

print(f"Corrigido: {sum(len(p['tarefas']) for p in projetos)} tarefas em {len(projetos)} projetos.")