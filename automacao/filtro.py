"""
filtro.py — Filtra notícias por relevâncie (local + Gemini)
"""
import json
import google.generativeai as genai
from config import (
    GEMINI_API_KEY, ARQUIVO_COLETADOS, ARQUIVO_FILTRADOS,
    TERMOS_POSITIVOS, TERMOS_NEGATIVOS, MIN_SCORE_POSITIVO,
    POSTS_POR_DIA, MODELO_GEMINI
)

genai.configure(api_key=GEMINI_API_KEY)


def _score_local(item: dict) -> int:
    texto = f"{item['titulo']} {item['resumo']}".lower()
    pos = sum(1 for t in TERMOS_POSITIVOS if t in texto)
    neg = sum(1 for t in TERMOS_NEGATIVOS if t in texto)
    return pos - (neg * 3)


def _validar_gemini(itens: list[dict]) -> list[dict]:
    model = genai.GenerativeModel(MODELO_GEMINI)
    validos = []

    for item in itens:
        prompt = f"""Analise se esta notícia é relevante para um blog de circo social brasileiro
(arte circense como transformação social, cultura, educação, comunidade).

Título: {item['titulo']}
Resumo: {item['resumo']}

Responda APENAS com: RELEVANTE ou IRRELEVANTE"""

        try:
            resp = model.generate_content(prompt)
            if "RELEVANTE" in resp.text.upper():
                validos.append(item)
                print(f"  ✅ RELEVANTE: {item['titulo'][:60]}")
            else:
                print(f"  ❌ IRRELEVANTE: {item['titulo'][:60]}")
        except Exception as e:
            print(f"  ⚠️  Erro Gemini: {e}")
            validos.append(item)  # Em caso de erro, mantém

    return validos


def filtrar() -> list[dict]:
    print("🔍 Filtrando notícias...")

    if not ARQUIVO_COLETADOS.exists():
        print("  ⚠️  Nenhuma notícia coletada ainda.")
        return []

    notícias = json.loads(ARQUIVO_COLETADOS.read_text())

    # 1. Filtro local por score
    candidatos = [n for n in notícias if _score_local(n) >= MIN_SCORE_POSITIVO]
    print(f"  📊 {len(candidatos)}/{len(notícias)} passaram no filtro local")

    # 2. Validação Gemini (limita ao necessário para economizar API)
    limite = min(len(candidatos), POSTS_POR_DIA * 3)
    validados = _validar_gemini(candidatos[:limite])

    # Pega apenas os necessários para hoje
    resultado = validados[:POSTS_POR_DIA]
    ARQUIVO_FILTRADOS.write_text(json.dumps(resultado, ensure_ascii=False, indent=2))
    print(f"  ✅ {len(resultado)} notícias aprovadas → {ARQUIVO_FILTRADOS}")
    return resultado


if __name__ == "__main__":
    filtrar()
