"""
CircoLando — Configuração Central
Sistema de automação: Gemini + RSS → Hugo → GitHub Pages
"""
import os
from pathlib import Path

# ─── API Keys ─────────────────────────────────────────────
GEMINI_API_KEY = "AIzaSyDTp9dwGe9h_s_vXwZ_jViXF8Dp4Pwv-8c"

# ─── GitHub Pages Deploy ───────────────────────────────────
# Seu usuário e nome do repositório no GitHub
# Seu blog ficará em: https://GITHUB_USER.github.io/GITHUB_REPO/
GITHUB_USER = "ttpap"
GITHUB_REPO = "EcoBuzios-Blog"    # ← Nome do repositório que você criar

# ─── Gmail (aprovação por e-mail) ─────────────────────────
GMAIL_USER = "antonpap@gmail.com"
GMAIL_APP_PASSWORD = ""       # Senha de app do Gmail (não a senha pessoal)

# ─── Caminhos ─────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent.parent          # raiz do projeto Hugo
POSTS_DIR    = BASE_DIR / "content" / "posts"        # onde os .md são salvos
IMAGES_DIR   = BASE_DIR / "static" / "images"        # imagens dos posts
FILA_DIR     = Path(__file__).parent / "fila"        # arquivos temporários

FILA_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

# ─── RSS Feeds ────────────────────────────────────────────
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=circo+social+brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "https://news.google.com/rss/search?q=circo+social+arte+educacao&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "https://news.google.com/rss/search?q=circo+transformacao+social+brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "https://news.google.com/rss/search?q=arte+circense+comunidade&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "https://news.google.com/rss/search?q=malabarismo+acrobacia+social&hl=pt-BR&gl=BR&ceid=BR:pt-419",
]

# ─── Filtros de conteúdo ──────────────────────────────────
TERMOS_POSITIVOS = [
    "circo", "circense", "social", "arte", "comunidade", "transformação",
    "malabarismo", "acrobacia", "palhaço", "trapézio", "educação", "cultura",
    "periferia", "jovens", "inclusão", "projeto", "oficina", "espetáculo",
    "lona", "picadeiro", "equilibrismo", "contorcionismo",
]

TERMOS_NEGATIVOS = [
    "apostas", "cassino", "crime", "violência", "briga", "morreu", "morte",
    "acidente grave", "pornografia", "drogas ilegais",
]

MIN_SCORE_POSITIVO = 2

# ─── Geração ──────────────────────────────────────────────
POSTS_POR_DIA     = 3
MODELO_GEMINI     = "gemini-1.5-flash"

# Categorias válidas para o blog
CATEGORIAS = ["Social", "Cultura", "Educação", "Espetáculo", "Comunidade", "Arte"]

# ─── Arquivos de estado ───────────────────────────────────
ARQUIVO_COLETADOS   = FILA_DIR / "coletados.json"
ARQUIVO_FILTRADOS   = FILA_DIR / "filtrados.json"
ARQUIVO_GERADOS     = FILA_DIR / "gerados.json"
ARQUIVO_PUBLICADOS  = FILA_DIR / "publicados.json"
ARQUIVO_IDS_VISTOS  = FILA_DIR / "ids_vistos.txt"
