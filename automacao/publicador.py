"""
publicador.py — Salva posts como .md no Hugo e faz deploy no Netlify
"""
import json
import re
import subprocess
import urllib.request
import urllib.parse
import io
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
from config import (
    GEMINI_API_KEY, ARQUIVO_GERADOS, ARQUIVO_PUBLICADOS,
    POSTS_DIR, IMAGES_DIR, NETLIFY_TOKEN, NETLIFY_SITE_ID, BASE_DIR
)

genai.configure(api_key=GEMINI_API_KEY)


# ────────────────────────────────────────
# GERAÇÃO DE IMAGEM
# ────────────────────────────────────────

def _gerar_imagem_canvas(titulo: str, categoria: str, slug: str) -> str | None:
    """Gera imagem via Pollinations.AI (serviço gratuito, sem CORS no servidor)."""
    try:
        prompt_encoded = urllib.parse.quote(
            f"circus social art Brazil colorful {titulo[:60]} vibrant illustration"
        )
        url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1200&height=630&nologo=true"

        with urllib.request.urlopen(url, timeout=30) as resp:
            img_data = resp.read()

        nome_arquivo = f"{slug}.jpg"
        caminho = IMAGES_DIR / nome_arquivo
        caminho.write_bytes(img_data)
        print(f"     🖼️  Imagem salva: {nome_arquivo}")
        return f"/images/{nome_arquivo}"

    except Exception as e:
        print(f"     ⚠️  Imagem falhou ({e}). Usando placeholder.")
        return None


# ────────────────────────────────────────
# CRIAÇÃO DO ARQUIVO MARKDOWN
# ────────────────────────────────────────

def _slugify(texto: str) -> str:
    """Converte título para slug URL-friendly."""
    slug = texto.lower().strip()
    slug = re.sub(r'[áàãâä]', 'a', slug)
    slug = re.sub(r'[éèêë]', 'e', slug)
    slug = re.sub(r'[íìîï]', 'i', slug)
    slug = re.sub(r'[óòõôö]', 'o', slug)
    slug = re.sub(r'[úùûü]', 'u', slug)
    slug = re.sub(r'[ç]', 'c', slug)
    slug = re.sub(r'[ñ]', 'n', slug)
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug[:80]


def _criar_markdown(post: dict, caminho_imagem: str | None) -> Path:
    """Cria o arquivo .md no formato Hugo com frontmatter YAML."""
    slug = _slugify(post['titulo'])
    data = post.get('data', datetime.now().strftime('%Y-%m-%d'))
    nome_arquivo = f"{data}-{slug}.md"
    caminho_md = POSTS_DIR / nome_arquivo

    # Tags como lista YAML
    tags = post.get('tags', [])
    tags_yaml = "\n".join(f'  - "{t}"' for t in tags) if tags else '  - "circo social"'

    categoria = post.get('categoria', 'Social')

    imagem_linha = f'image: "{caminho_imagem}"' if caminho_imagem else ""

    frontmatter = f"""---
title: "{post['titulo'].replace('"', "'")}"
subtitle: "{post.get('subtitulo', '').replace('"', "'")}"
date: {data}
categories:
  - "{categoria}"
tags:
{tags_yaml}
description: "{post.get('resumo_seo', '').replace('"', "'")}"
{imagem_linha}
draft: false
---

"""

    # Corpo: converte HTML básico para Markdown-friendly
    corpo = post.get('corpo', '')
    # Hugo renderiza HTML dentro de .md com unsafe: true no config
    conteudo = frontmatter + corpo

    caminho_md.write_text(conteudo, encoding='utf-8')
    print(f"     📄 Markdown criado: {nome_arquivo}")
    return caminho_md


# ────────────────────────────────────────
# DEPLOY VIA GITHUB (git push → GitHub Actions → GitHub Pages)
# ────────────────────────────────────────

def _deploy_github() -> bool:
    """Faz git add + commit + push. O GitHub Actions cuida do build e deploy."""
    from config import GITHUB_REPO, GITHUB_USER

    print("  📤 Enviando posts para o GitHub...")

    cmds = [
        ["git", "add", "content/", "static/images/"],
        ["git", "commit", "-m", f"Auto-post CircoLando {datetime.now().strftime('%d/%m/%Y %H:%M')}"],
        ["git", "push", "origin", "main"],
    ]

    for cmd in cmds:
        result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
        if result.returncode != 0:
            # "nothing to commit" não é erro
            if "nothing to commit" in result.stdout + result.stderr:
                print("  ℹ️  Nada para commitar.")
                return True
            print(f"  ❌ Erro em '{' '.join(cmd)}': {result.stderr}")
            return False

    print(f"  ✅ Push feito! GitHub Actions vai publicar automaticamente.")
    print(f"  🌐 Seu blog: https://{GITHUB_USER}.github.io/{GITHUB_REPO}/")
    return True


# ────────────────────────────────────────
# PUBLICAÇÃO PRINCIPAL
# ────────────────────────────────────────

def publicar(posts: list[dict]) -> list[dict]:
    print("🚀 Publicando posts no Hugo...")

    if not posts:
        print("  ⚠️  Nenhum post para publicar.")
        return []

    # Carrega histórico
    publicados = []
    if ARQUIVO_PUBLICADOS.exists():
        publicados = json.loads(ARQUIVO_PUBLICADOS.read_text())

    novos = []

    for post in posts:
        print(f"\n  📌 Publicando: {post['titulo'][:60]}")

        slug = _slugify(post['titulo'])

        # 1. Gerar imagem
        caminho_img = _gerar_imagem_canvas(post['titulo'], post.get('categoria', ''), slug)

        # 2. Criar arquivo .md
        caminho_md = _criar_markdown(post, caminho_img)

        registro = {
            "titulo":    post['titulo'],
            "slug":      slug,
            "data":      post.get('data', ''),
            "arquivo":   caminho_md.name,
            "imagem":    caminho_img,
            "publicado": datetime.now().isoformat(),
        }
        novos.append(registro)
        publicados.append(registro)
        print(f"     ✅ Pronto!")

    # Salva histórico
    ARQUIVO_PUBLICADOS.write_text(json.dumps(publicados, ensure_ascii=False, indent=2))

    # Deploy
    if novos:
        print(f"\n  📦 {len(novos)} posts adicionados. Enviando para GitHub...")
        _deploy_github()

    return novos


if __name__ == "__main__":
    gerados = json.loads(ARQUIVO_GERADOS.read_text()) if ARQUIVO_GERADOS.exists() else []
    publicar(gerados)
