TEMAS = {
    "financeiro": {
        "nome": "Dashboard Financeiro",
        "descricao": "Fundo escuro, acentos em verde e azul frio. Dados em destaque.",
        "preview_cores": ["#0a0f1e", "#1a2744", "#00d4aa", "#0099ff", "#ffffff"],
        "css": """
            .stApp { background-color: #0a0f1e !important; }

            [data-testid="stSidebar"] {
                background-color: #070d1a !important;
                border-right: 1px solid #1e2d4a !important;
            }
            [data-testid="stSidebar"] * { color: #8899bb !important; }

            h1, h2, h3 {
                color: #f0f4ff !important;
                font-weight: 700 !important;
                letter-spacing: -0.02em !important;
            }
            h1 { font-size: 1.8rem !important; }

            p, span, label, div { color: #8899bb !important; }

            .stButton > button {
                background: transparent !important;
                color: #00d4aa !important;
                border: 1px solid #00d4aa60 !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
                letter-spacing: 0.02em !important;
                transition: all 0.2s !important;
                box-shadow: none !important;
            }
            .stButton > button:hover {
                background: #00d4aa15 !important;
                border-color: #00d4aa !important;
                color: #00d4aa !important;
            }
            .stButton > button[kind="primary"] {
                background: #00d4aa18 !important;
                border: 1px solid #00d4aa !important;
                color: #00d4aa !important;
                font-weight: 700 !important;
            }
            .stButton > button[kind="primary"]:hover {
                background: #00d4aa30 !important;
            }

            .stSelectbox > div, .stMultiSelect > div, .stTextInput > div > div {
                background-color: #141f35 !important;
                border: 1px solid #1e2d4a !important;
                border-radius: 6px !important;
                color: #f0f4ff !important;
            }

            .stExpander {
                background-color: #141f35 !important;
                border: 1px solid #1e2d4a !important;
                border-radius: 8px !important;
            }
            .stExpander:hover { border-color: #00d4aa60 !important; }

            [data-testid="metric-container"] {
                background: #141f35 !important;
                border: 1px solid #1e2d4a !important;
                border-radius: 8px !important;
                padding: 16px !important;
                border-left: 3px solid #00d4aa !important;
            }

            .stProgress > div > div {
                background: linear-gradient(90deg, #00d4aa, #0099ff) !important;
                border-radius: 4px !important;
            }

            .stTabs [data-baseweb="tab-list"] {
                background-color: #0f1729 !important;
                border-radius: 8px !important;
                padding: 4px !important;
            }
            .stTabs [data-baseweb="tab"] {
                color: #8899bb !important;
                border-radius: 6px !important;
            }
            .stTabs [aria-selected="true"] {
                background-color: #00d4aa18 !important;
                color: #00d4aa !important;
                font-weight: 700 !important;
            }

            hr { border-color: #1e2d4a !important; }
        """,
    },

    "gestao": {
        "nome": "Gestão de Projetos",
        "descricao": "Espaçoso, tipografia forte, acentos em índigo e violeta.",
        "preview_cores": ["#0f0f23", "#1a1a3e", "#6366f1", "#a855f7", "#ffffff"],
        "css": """
            .stApp { background-color: #0f0f23 !important; }

            [data-testid="stSidebar"] {
                background-color: #0a0a1a !important;
                border-right: 1px solid #252550 !important;
            }
            [data-testid="stSidebar"] * { color: #94a3c8 !important; }

            h1, h2, h3 {
                color: #f8fafc !important;
                font-weight: 800 !important;
                letter-spacing: -0.03em !important;
                line-height: 1.2 !important;
            }
            h1 { font-size: 2rem !important; }

            p, span, label, div { color: #94a3c8 !important; }

            .stButton > button {
                background: transparent !important;
                color: #818cf8 !important;
                border: 1px solid #6366f150 !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                transition: all 0.2s !important;
                box-shadow: none !important;
            }
            .stButton > button:hover {
                background: #6366f112 !important;
                border-color: #6366f1 !important;
                color: #a5b4fc !important;
            }
            .stButton > button[kind="primary"] {
                background: #6366f115 !important;
                border: 1px solid #6366f1 !important;
                color: #a5b4fc !important;
                font-weight: 700 !important;
            }
            .stButton > button[kind="primary"]:hover {
                background: #6366f130 !important;
                border-color: #a855f7 !important;
                color: #c4b5fd !important;
            }

            .stSelectbox > div, .stMultiSelect > div, .stTextInput > div > div {
                background-color: #1a1a38 !important;
                border: 1px solid #252550 !important;
                border-radius: 8px !important;
                color: #f8fafc !important;
            }

            .stExpander {
                background-color: #1a1a38 !important;
                border: 1px solid #252550 !important;
                border-radius: 12px !important;
                margin-bottom: 8px !important;
            }
            .stExpander:hover {
                border-color: #6366f160 !important;
                box-shadow: 0 0 0 2px #6366f115 !important;
            }

            [data-testid="metric-container"] {
                background: #1a1a38 !important;
                border: 1px solid #252550 !important;
                border-radius: 12px !important;
                padding: 20px !important;
                border-top: 3px solid #6366f1 !important;
            }

            .stProgress > div > div {
                background: linear-gradient(90deg, #6366f1, #a855f7) !important;
                border-radius: 99px !important;
            }

            .stTabs [data-baseweb="tab-list"] {
                background-color: transparent !important;
                border-bottom: 2px solid #252550 !important;
                border-radius: 0 !important;
            }
            .stTabs [data-baseweb="tab"] {
                color: #94a3c8 !important;
                font-weight: 600 !important;
            }
            .stTabs [aria-selected="true"] {
                color: #818cf8 !important;
                background: transparent !important;
                font-weight: 700 !important;
            }

            hr { border-color: #252550 !important; }
        """,
    },

    "enterprise": {
        "nome": "Enterprise",
        "descricao": "Sóbrio, denso, acentos em laranja e âmbar. Foco em produtividade.",
        "preview_cores": ["#0c0c0c", "#161616", "#f97316", "#f59e0b", "#ffffff"],
        "css": """
            .stApp { background-color: #0c0c0c !important; }

            [data-testid="stSidebar"] {
                background-color: #080808 !important;
                border-right: 1px solid #262626 !important;
            }
            [data-testid="stSidebar"] * { color: #737373 !important; }

            h1, h2, h3 {
                color: #fafafa !important;
                font-weight: 600 !important;
                font-family: 'SF Mono', 'Consolas', monospace !important;
            }
            h1 {
                font-size: 1.5rem !important;
                text-transform: uppercase !important;
                letter-spacing: 0.1em !important;
            }

            p, span, label, div {
                color: #a3a3a3 !important;
                font-size: 0.875rem !important;
            }

            .stButton > button {
                background: transparent !important;
                color: #f97316 !important;
                border: 1px solid #f9731640 !important;
                border-radius: 3px !important;
                font-weight: 600 !important;
                font-family: monospace !important;
                letter-spacing: 0.05em !important;
                transition: all 0.15s !important;
                box-shadow: none !important;
            }
            .stButton > button:hover {
                background: #f9731615 !important;
                border-color: #f97316 !important;
            }
            .stButton > button[kind="primary"] {
                background: #f9731615 !important;
                border: 1px solid #f97316 !important;
                color: #fb923c !important;
                font-weight: 700 !important;
            }
            .stButton > button[kind="primary"]:hover {
                background: #f9731630 !important;
            }

            .stSelectbox > div, .stMultiSelect > div, .stTextInput > div > div {
                background-color: #161616 !important;
                border: 1px solid #262626 !important;
                border-radius: 3px !important;
                color: #fafafa !important;
                font-family: monospace !important;
            }

            .stExpander {
                background-color: #161616 !important;
                border: 1px solid #262626 !important;
                border-radius: 3px !important;
                margin-bottom: 4px !important;
            }
            .stExpander:hover { border-color: #f9731660 !important; }

            [data-testid="metric-container"] {
                background: #161616 !important;
                border: 1px solid #262626 !important;
                border-radius: 3px !important;
                padding: 12px !important;
                border-left: 2px solid #f97316 !important;
            }

            .stProgress > div > div {
                background: #f97316 !important;
                border-radius: 0 !important;
            }

            .stTabs [data-baseweb="tab-list"] {
                background-color: #111 !important;
                border: 1px solid #262626 !important;
                border-radius: 3px !important;
                padding: 2px !important;
            }
            .stTabs [data-baseweb="tab"] {
                color: #525252 !important;
                font-family: monospace !important;
                font-size: 0.8rem !important;
                letter-spacing: 0.05em !important;
            }
            .stTabs [aria-selected="true"] {
                background-color: #f9731620 !important;
                color: #f97316 !important;
                font-weight: 700 !important;
            }

            hr { border-color: #262626 !important; }
        """,
    },
}

TEMA_PADRAO = "financeiro"