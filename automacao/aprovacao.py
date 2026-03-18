"""
aprovacao.py — Envia posts por e-mail para aprovação e aguarda resposta
"""
import json
import smtplib
import imaplib
import email
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from config import (
    GMAIL_USER, GMAIL_APP_PASSWORD, ARQUIVO_GERADOS, ARQUIVO_FILTRADOS
)


def _enviar_email_aprovacao(posts: list[dict]) -> bool:
    if not GMAIL_APP_PASSWORD:
        print("  ⚠️  Gmail não configurado. Pulando aprovação — todos aprovados.")
        return True

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[CircoLando] {len(posts)} post(s) para aprovação — {datetime.now().strftime('%d/%m/%Y')}"
    msg["From"]    = GMAIL_USER
    msg["To"]      = GMAIL_USER

    html = f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto;">
    <div style="background:#00A3AD; padding:24px; border-radius:8px 8px 0 0;">
      <h1 style="color:white; margin:0;">CircoLando</h1>
      <p style="color:rgba(255,255,255,0.85); margin:8px 0 0;">Posts aguardando aprovação</p>
    </div>
    <div style="background:#f9f9f9; padding:24px; border-radius:0 0 8px 8px;">
      <p>Responda este e-mail com:</p>
      <ul>
        <li><strong>APROVAR TODOS</strong> — para publicar todos</li>
        <li><strong>APROVAR 1</strong> (ou 2, 3...) — para aprovar posts específicos</li>
        <li><strong>REPROVAR TODOS</strong> — para descartar tudo</li>
      </ul>
      <hr style="border:1px solid #e0e0e0; margin:20px 0;">
    """

    for i, p in enumerate(posts, 1):
        html += f"""
        <div style="background:white; border-radius:8px; padding:20px; margin-bottom:16px;
                    border-left:4px solid #00A3AD; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
          <p style="color:#00A3AD; font-weight:bold; margin:0 0 4px; font-size:12px;">
            POST {i} — {p.get('categoria','').upper()}
          </p>
          <h2 style="margin:0 0 8px; font-size:18px;">{p['titulo']}</h2>
          <p style="color:#666; margin:0 0 12px; font-size:14px;">{p.get('subtitulo','')}</p>
          <p style="font-size:13px; color:#888; margin:0;">📰 Fonte: {p.get('fonte_nome','')} · 📅 {p.get('data','')}</p>
        </div>
        """

    html += """
      <p style="color:#888; font-size:12px; margin-top:24px;">
        Este e-mail foi gerado automaticamente pelo sistema CircoLando.
      </p>
    </div></body></html>
    """

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
        print(f"  📧 E-mail enviado para {GMAIL_USER}")
        return True
    except Exception as e:
        print(f"  ❌ Erro ao enviar e-mail: {e}")
        return False


def _ler_resposta(timeout_min: int = 120) -> str:
    if not GMAIL_APP_PASSWORD:
        return "APROVAR TODOS"

    print(f"  ⏳ Aguardando resposta por até {timeout_min} minutos...")
    deadline = time.time() + timeout_min * 60

    while time.time() < deadline:
        try:
            with imaplib.IMAP4_SSL("imap.gmail.com") as imap:
                imap.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                imap.select("INBOX")
                _, msgs = imap.search(None, 'SUBJECT "[CircoLando]" UNSEEN')
                for num in msgs[0].split():
                    _, data = imap.fetch(num, "(RFC822)")
                    msg = email.message_from_bytes(data[0][1])
                    corpo = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                corpo = part.get_payload(decode=True).decode()
                    else:
                        corpo = msg.get_payload(decode=True).decode()
                    imap.store(num, "+FLAGS", "\\Seen")
                    return corpo.strip().upper()
        except Exception:
            pass
        time.sleep(60)

    print("  ⏰ Timeout! Aprovando automaticamente todos os posts.")
    return "APROVAR TODOS"


def processar_aprovacao(posts: list[dict]) -> list[dict]:
    print("📬 Iniciando processo de aprovação...")

    if not posts:
        return []

    enviado = _enviar_email_aprovacao(posts)
    if not enviado:
        return posts  # Se falhou, aprova tudo

    resposta = _ler_resposta()
    print(f"  📩 Resposta recebida: {resposta[:60]}")

    if "REPROVAR TODOS" in resposta:
        print("  ❌ Todos os posts foram reprovados.")
        return []

    if "APROVAR TODOS" in resposta:
        print(f"  ✅ Todos os {len(posts)} posts aprovados.")
        return posts

    # Aprovação seletiva: "APROVAR 1 3"
    aprovados = []
    for i, post in enumerate(posts, 1):
        if f"APROVAR {i}" in resposta or f"APROVAR{i}" in resposta:
            aprovados.append(post)
            print(f"  ✅ Post {i} aprovado: {post['titulo'][:50]}")
        else:
            print(f"  ❌ Post {i} não aprovado.")

    return aprovados if aprovados else posts  # Fallback


if __name__ == "__main__":
    gerados = json.loads(ARQUIVO_GERADOS.read_text()) if ARQUIVO_GERADOS.exists() else []
    aprovados = processar_aprovacao(gerados)
    print(f"\n{len(aprovados)} posts aprovados para publicação.")
