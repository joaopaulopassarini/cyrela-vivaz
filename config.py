import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"
DATA_PATH = "data/projetos_cyrela.json"

STATUS_OPTIONS = [
    "Não iniciado",
    "Em andamento",
    "Protocolado",
    "Aguardando resposta",
    "Concluído",
    "Bloqueado",
    "Não aplicável",
]

# Grupos principais (nível 1)
GRUPOS = [
    "Passagem Terrenos-Negócios",
    "Levantamentos Iniciais",
    "Desenvolvimento de Projeto",
    "Aprovações Legais",
    "Preparativos Lançamento",
]

# Subgrupos (nível 2) e a qual grupo pertencem
SUBGRUPOS = {
    "Estudos Ambientais": "Levantamentos Iniciais",
    "Jurídico": "Levantamentos Iniciais",
    "Aprovações Municipais": "Aprovações Legais",
    "Aprovações Estaduais": "Aprovações Legais",
    "Registro e Cartório": "Preparativos Lançamento",
    "Comercialização": "Preparativos Lançamento",
}

# Mantém FASES como alias para compatibilidade com views existentes
FASES = GRUPOS

COR_STATUS = {
    "Não iniciado": "#adb5bd",
    "Em andamento": "#339af0",
    "Protocolado": "#f59f00",
    "Aguardando resposta": "#f76707",
    "Concluído": "#40c057",
    "Bloqueado": "#fa5252",
    "Não aplicável": "#dee2e6",
}

COR_GRUPO = {
    "Passagem Terrenos-Negócios": "#74c0fc",
    "Levantamentos Iniciais": "#4dabf7",
    "Desenvolvimento de Projeto": "#69db7c",
    "Aprovações Legais": "#ffa94d",
    "Preparativos Lançamento": "#da77f2",
}

COR_SUBGRUPO = {
    "Estudos Ambientais": "#63e6be",
    "Jurídico": "#a9e34b",
    "Aprovações Municipais": "#ffec99",
    "Aprovações Estaduais": "#ffd8a8",
    "Registro e Cartório": "#eebefa",
    "Comercialização": "#d0bfff",
}

# Alias para compatibilidade
COR_FASE = COR_GRUPO