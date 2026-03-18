"""
coletor.py — Coleta notícias via RSS e Google News
"""
import json
import hashlib
from datetime import datetime, timedelta
import feedparser
from config import (
    RSS_FEEDS, ARQUIVO_COLETADOS, ARQUIVO_IDS_VISTOS
)


def _id_noticia(titulo: str, url: str) -> str:
    return hashlib.md5(f"{titulo}{url}".encode()).hexdigest()[:12]


def _carregar_ids_vistos() -> set:
    if ARQUIVO_IDS_VISTOS.exists():
        return set(ARQUIVO_IDS_VISTOS.read_text().splitlines())
    return set()


def _salvar_ids_vistos(ids: set):
    ARQUIVO_IDS_VISTOS.write_text("\n".join(ids))


def coletar() -> list[dict]:
    print("📡 Coletando notícias via RSS...")
    ids_vistos = _carregar_ids_vistos()
    novas = []
    corte = datetime.now() - timedelta(days=7)

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                titulo = getattr(entry, "title", "").strip()
                url    = getattr(entry, "link", "").strip()
                resumo = getattr(entry, "summary", "").strip()

                if not titulo or not url:
                    continue

                nid = _id_noticia(titulo, url)
                if nid in ids_vistos:
                    continue

                # Data
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    data = datetime(*entry.published_parsed[:6])
                    if data < corte:
                        continue
                    data_str = data.strftime("%Y-%m-%d")
                else:
                    data_str = datetime.now().strftime("%Y-%m-%d")

                novas.append({
                    "id":     nid,
                    "titulo": titulo,
                    "url":    url,
                    "resumo": resumo,
                    "data":   data_str,
                    "fonte":  feed.feed.get("title", "Desconhecido"),
                })
                ids_vistos.add(nid)

        except Exception as e:
            print(f"  ⚠️  Erro no feed {feed_url[:60]}: {e}")

    _salvar_ids_vistos(ids_vistos)
    ARQUIVO_COLETADOS.write_text(json.dumps(novas, ensure_ascii=False, indent=2))
    print(f"  ✅ {len(novas)} novas notícias coletadas → {ARQUIVO_COLETADOS}")
    return novas


if __name__ == "__main__":
    coletar()
