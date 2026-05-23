TEMAS = {
    "vivaz": {
        "nome": "Vivaz",
        "descricao": "Dark editorial. Âmbar sobre preto. Tipografia técnica.",
        "preview_cores": ["#0a0a0a", "#111111", "#c8902a", "#e8a83a", "#f0ede8"],
        "css": """
            @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;500&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

            .stApp {
                background-color: #0a0a0a !important;
                font-family: 'IBM Plex Mono', monospace !important;
            }

            [data-testid="stSidebar"] {
                background-color: #0d0d0d !important;
                border-right: 1px solid #1e1e1e !important;
            }
            [data-testid="stSidebar"] * {
                color: #5a5550 !important;
                font-family: 'IBM Plex Mono', monospace !important;
                font-size: 0.8rem !important;
                letter-spacing: 0.04em !important;
            }
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
                color: #5a5550 !important;
            }
            [data-testid="stSidebar"] .stRadio label[data-checked="true"] {
                color: #c8902a !important;
                background: #1a1208 !important;
                border-left: 2px solid #c8902a !important;
            }
            [data-testid="stSidebar"] .stRadio label:hover {
                background: #141414 !important;
                color: #a09a90 !important;
            }
            [data-testid="stSidebar"] hr {
                border-color: #1e1e1e !important;
                margin: 8px 0 !important;
            }

            h1 {
                font-family: 'Bebas Neue', sans-serif !important;
                font-size: 2rem !important;
                letter-spacing: 0.1em !important;
                color: #f0ede8 !important;
                font-weight: 400 !important;
                line-height: 1 !important;
                margin-bottom: 0.5rem !important;
            }
            h2 {
                font-family: 'Bebas Neue', sans-serif !important;
                font-size: 1.3rem !important;
                letter-spacing: 0.1em !important;
                color: #f0ede8 !important;
                font-weight: 400 !important;
            }
            h3 {
                font-family: 'IBM Plex Mono', monospace !important;
                font-size: 0.85rem !important;
                letter-spacing: 0.15em !important;
                text-transform: uppercase !important;
                color: #c8902a !important;
                font-weight: 500 !important;
            }

            [data-testid="stMarkdownContainer"] p,
            [data-testid="stMarkdownContainer"] li,
            [data-testid="stMarkdownContainer"] span {
                color: #a09a90 !important;
                font-family: 'IBM Plex Mono', monospace !important;
                font-size: 0.82rem !important;
                line-height: 1.6 !important;
            }
            [data-testid="stMarkdownContainer"] strong,
            [data-testid="stMarkdownContainer"] b {
                color: #f0ede8 !important;
            }

            .stButton > button {
                background: transparent !important;
                color: #c8902a !important;
                border: 1px solid #6b4d1640 !important;
                border-radius: 2px !important;
                font-family: 'IBM Plex Mono', monospace !important;
                font-size: 0.78rem !important;
                letter-spacing: 0.1em !important;
                text-transform: uppercase !important;
                font-weight: 500 !important;
                transition: all 0.15s !important;
                box-shadow: none !important;
                padding: 6px 16px !important;
            }
            .stButton > button:hover {
                background: #1a1208 !important;
                border-color: #c8902a !important;
                color: #e8a83a !important;
            }
            .stButton > button[kind="primary"] {
                background: #1a1208 !important;
                border: 1px solid #c8902a !important;
                color: #e8a83a !important;
                font-weight: 700 !important;
            }
            .stButton > button[kind="primary"]:hover {
                background: #261a0a !important;
                border-color: #e8a83a !important;
            }

            .stSelectbox > div > div,
            .stMultiSelect > div > div,
            .stTextInput > div > div,
            .stTextArea > div > div,
            .stDateInput > div > div {
                background-color: #111111 !important;
                border: 1px solid #222222 !important;
                border-radius: 2px !important;
                color: #f0ede8 !important;
                font-family: 'IBM Plex Mono', monospace !important;
                font-size: 0.82rem !important;
            }
            .stSelectbox > div > div:focus-within,
            .stTextInput > div > div:focus-within,
            .stTextArea > div > div:focus-within {
                border-color: #c8902a !important;
                box-shadow: 0 0 0 1px #c8902a30 !important;
            }
            .stSelectbox label,
            .stTextInput label,
            .stTextArea label,
            .stDateInput label,
            .stCheckbox label,
            .stRadio label {
                color: #5a5550 !important;
                font-size: 0.75rem !important;
                letter-spacing: 0.1em !important;
                text-transform: uppercase !important;
                font-family: 'IBM Plex Mono', monospace !important;
            }

            [data-testid="metric-container"] {
                background: #111111 !important;
                border: 1px solid #1e1e1e !important;
                border-radius: 2px !important;
                padding: 16px !important;
                border-left: 2px solid #c8902a !important;
            }
            [data-testid="stMetricValue"] {
                font-family: 'Bebas Neue', sans-serif !important;
                font-size: 2.2rem !important;
                letter-spacing: 0.05em !important;
                color: #f0ede8 !important;
                font-weight: 400 !important;
            }
            [data-testid="stMetricLabel"] {
                font-size: 0.7rem !important;
                letter-spacing: 0.2em !important;
                text-transform: uppercase !important;
                color: #5a5550 !important;
                font-family: 'IBM Plex Mono', monospace !important;
            }
            [data-testid="stMetricDelta"] {
                font-size: 0.75rem !important;
                font-family: 'IBM Plex Mono', monospace !important;
            }

            .stExpander {
                background-color: #111111 !important;
                border: 1px solid #1e1e1e !important;
                border-radius: 2px !important;
                margin-bottom: 4px !important;
            }
            .stExpander:hover {
                border-color: #c8902a60 !important;
            }
            .stExpander details summary {
                font-family: 'IBM Plex Mono', monospace !important;
                font-size: 0.82rem !important;
                color: #a09a90 !important;
                letter-spacing: 0.04em !important;
                background: transparent !important;
            }
            .stExpander details summary:hover {
                color: #f0ede8 !important;
            }
            .stExpander details summary p {
                color: #a09a90 !important;
                font-family: 'IBM Plex Mono', monospace !important;
                font-size: 0.82rem !important;
            }

            .stProgress > div > div {
                background: #c8902a !important;
                border-radius: 0 !important;
                height: 3px !important;
            }
            .stProgress > div {
                background: #1e1e1e !important;
                border-radius: 0 !important;
                height: 3px !important;
            }

            .stTabs [data-baseweb="tab-list"] {
                background-color: transparent !important;
                border-bottom: 1px solid #1e1e1e !important;
                border-radius: 0 !important;
                gap: 0 !important;
            }
            .stTabs [data-baseweb="tab"] {
                color: #5a5550 !important;
                font-family: 'IBM Plex Mono', monospace !important;
                font-size: 0.75rem !important;
                letter-spacing: 0.12em !important;
                text-transform: uppercase !important;
                border-radius: 0 !important;
                padding: 8px 16px !important;
                border-bottom: 2px solid transparent !important;
            }
            .stTabs [aria-selected="true"] {
                color: #c8902a !important;
                background: transparent !important;
                border-bottom: 2px solid #c8902a !important;
                font-weight: 500 !important;
            }
            .stTabs [data-baseweb="tab"]:hover {
                color: #a09a90 !important;
                background: #111111 !important;
            }

            [data-testid="stAlert"] {
                border-radius: 2px !important;
                font-family: 'IBM Plex Mono', monospace !important;
                font-size: 0.8rem !important;
            }

            hr {
                border-color: #1e1e1e !important;
                margin: 16px 0 !important;
            }

            .stCaption, [data-testid="stCaptionContainer"] {
                color: #3a3530 !important;
                font-size: 0.72rem !important;
                letter-spacing: 0.05em !important;
                font-family: 'IBM Plex Mono', monospace !important;
            }

            .stDownloadButton > button {
                background: transparent !important;
                color: #c8902a !important;
                border: 1px solid #c8902a40 !important;
                border-radius: 2px !important;
                font-family: 'IBM Plex Mono', monospace !important;
                font-size: 0.78rem !important;
                letter-spacing: 0.1em !important;
            }
            .stDownloadButton > button:hover {
                background: #1a1208 !important;
                border-color: #c8902a !important;
            }

            ::-webkit-scrollbar { width: 4px; height: 4px; }
            ::-webkit-scrollbar-track { background: #0a0a0a; }
            ::-webkit-scrollbar-thumb { background: #1e1e1e; border-radius: 2px; }
            ::-webkit-scrollbar-thumb:hover { background: #c8902a40; }
        """,
    },
}

TEMA_PADRAO = "vivaz"