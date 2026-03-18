"""
run_daily.py — Orquestrador principal do CircoLando
Executa: Coletar → Filtrar → Gerar → Aprovar → Publicar

Uso:
  python run_daily.py              # Fluxo completo
  python run_daily.py --so-coletar # Só coleta (testa feeds)
  python run_daily.py --etapa gerar # Só uma etapa específica
"""
import argparse
import sys
import json
from datetime import datetime

from coletor    import coletar
from filtro     import filtrar
from gerador    import gerar
from aprovacao  import processar_aprovacao
from publicador import publicar
from config     import ARQUIVO_GERADOS


def banner():
    print("""
╔═══════════════════════════════════════╗
║   CircoLando — Automação de Posts     ║
║   Hugo + Gemini + Netlify             ║
╚═══════════════════════════════════════╝
""")


def main():
    banner()

    parser = argparse.ArgumentParser(description="CircoLando — Pipeline de posts")
    parser.add_argument("--so-coletar", action="store_true", help="Apenas coleta notícias")
    parser.add_argument("--etapa", choices=["coletar", "filtrar", "gerar", "aprovar", "publicar"],
                        help="Executa apenas uma etapa")
    args = parser.parse_args()

    inicio = datetime.now()
    print(f"▶ Início: {inicio.strftime('%d/%m/%Y %H:%M')}\n")

    try:
        if args.so_coletar:
            coletar()
            return

        if args.etapa:
            etapas = {
                "coletar":  coletar,
                "filtrar":  filtrar,
                "gerar":    gerar,
                "aprovar":  lambda: processar_aprovacao(
                    json.loads(ARQUIVO_GERADOS.read_text()) if ARQUIVO_GERADOS.exists() else []
                ),
                "publicar": lambda: publicar(
                    json.loads(ARQUIVO_GERADOS.read_text()) if ARQUIVO_GERADOS.exists() else []
                ),
            }
            etapas[args.etapa]()
            return

        # ── Fluxo completo ──────────────────────
        print("━" * 45)
        print("1️⃣  ETAPA 1: Coleta de notícias")
        print("━" * 45)
        noticias = coletar()

        if not noticias:
            print("\n⚠️  Nenhuma notícia nova hoje. Encerrando.")
            return

        print(f"\n━" * 45)
        print("2️⃣  ETAPA 2: Filtragem por relevância")
        print("━" * 45)
        filtradas = filtrar()

        if not filtradas:
            print("\n⚠️  Nenhuma notícia relevante. Encerrando.")
            return

        print(f"\n━" * 45)
        print("3️⃣  ETAPA 3: Geração de posts (Gemini)")
        print("━" * 45)
        gerados = gerar()

        if not gerados:
            print("\n⚠️  Não foi possível gerar posts. Encerrando.")
            return

        print(f"\n━" * 45)
        print("4️⃣  ETAPA 4: Aprovação por e-mail")
        print("━" * 45)
        aprovados = processar_aprovacao(gerados)

        if not aprovados:
            print("\n⚠️  Nenhum post aprovado. Encerrando.")
            return

        print(f"\n━" * 45)
        print("5️⃣  ETAPA 5: Publicação (Hugo → Netlify)")
        print("━" * 45)
        publicados = publicar(aprovados)

        # ── Resumo final ────────────────────────
        fim = datetime.now()
        duracao = (fim - inicio).seconds
        print(f"""
╔═══════════════════════════════════════╗
║   ✅ Concluído com sucesso!           ║
╠═══════════════════════════════════════╣
║  📰 Coletadas:  {len(noticias):>3} notícias             ║
║  🔍 Filtradas: {len(filtradas):>3} relevantes           ║
║  ✍️  Gerados:   {len(gerados):>3} posts                 ║
║  ✅ Aprovados: {len(aprovados):>3} posts                 ║
║  🚀 Publicados:{len(publicados):>3} posts                 ║
║  ⏱️  Duração:  {duracao:>4}s                       ║
╚═══════════════════════════════════════╝
""")

    except KeyboardInterrupt:
        print("\n\n⏹️  Interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        raise


if __name__ == "__main__":
    main()
