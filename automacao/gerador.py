"""
gerador.py — Gera posts completos via Gemini
"""
import json
import re
import google.generativeai as genai
from config import (
    GEMINI_API_KEY, ARQUIVO_FILTRADOS, ARQUIVO_GERADOS,
    MODELO_GEMINI, CATEGORIAS
)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODELO_GEMINI)


def _gerar_post(noticia: dict) -> dict | None:
    prompt = f"""Você é um redator do blog CircoLando — blog brasileiro sobre circo social,
arte circense e transformação social. Escreva um post de blog completo em português.

Baseie-se NESTA notícia:
Título original: {noticia['titulo']}
Resumo: {noticia['resumo']}
Fonte: {noticia['fonte']}
URL original: {noticia['url']}

Gere o post no seguinte formato JSON (responda APENAS com o JSON, sem markdown):
{{
  "titulo": "Título criativo e atraente em português (máx 80 chars)",
  "subtitulo": "Subtítulo/lead que complementa o título (máx 120 chars)",
  "categoria": "Uma de: {', '.join(CATEGORIAS)}",
  "tags": ["tag1", "tag2", "tag3", "tag4"],
  "resumo_seo": "Resumo de 155 chars para SEO",
  "prompt_imagem": "Descrição visual da imagem ideal para este post (em inglês, para geração de imagem)",
  "corpo": "Corpo completo do post em HTML (use <h2>, <p>, <blockquote>, <ul>, <strong>). Mínimo 400 palavras. Termine com um parágrafo de chamada à ação convidando o leitor a acompanhar o CircoLando."
}}"""

    try:
        resp = model.generate_content(prompt)
        texto = resp.text.strip()

        # Limpar markdown se vier
        texto = re.sub(r"^```json\s*", "", texto)
        texto = re.sub(r"\s*```$", "", texto)

        dados = json.loads(texto)

        # Validações básicas
        if not dados.get("titulo") or not dados.get("corpo"):
            return None

        if dados.get("categoria") not in CATEGORIAS:
            dados["categoria"] = "Social"

        dados["fonte_url"]   = noticia["url"]
        dados["fonte_nome"]  = noticia["fonte"]
        dados["data"]        = noticia["data"]
        dados["noticia_id"]  = noticia["id"]

        return dados

    except Exception as e:
        print(f"  ⚠️  Erro ao gerar post: {e}")
        return None


def gerar() -> list[dict]:
    print("✍️  Gerando posts com Gemini...")

    if not ARQUIVO_FILTRADOS.exists():
        print("  ⚠️  Nenhuma notícia filtrada.")
        return []

    filtrados = json.loads(ARQUIVO_FILTRADOS.read_text())
    gerados = []

    for noticia in filtrados:
        print(f"  📝 Gerando: {noticia['titulo'][:60]}...")
        post = _gerar_post(noticia)
        if post:
            gerados.append(post)
            print(f"     ✅ Post gerado: {post['titulo'][:60]}")
        else:
            print(f"     ❌ Falhou")

    ARQUIVO_GERADOS.write_text(json.dumps(gerados, ensure_ascii=False, indent=2))
    print(f"  ✅ {len(gerados)} posts gerados → {ARQUIVO_GERADOS}")
    return gerados


if __name__ == "__main__":
    gerar()
