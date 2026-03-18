# CircoLando — Guia Completo
**Blog estático Hugo + Python + GitHub Pages (gratuito para sempre)**

---

## Como funciona

```
Python coleta notícias (RSS + Google News)
       ↓
Gemini gera o post completo
       ↓
Você aprova por e-mail
       ↓
Python salva o post como arquivo .md
       ↓
git push → GitHub
       ↓
GitHub Actions builda o Hugo automaticamente
       ↓
Blog no ar em: https://ttpap.github.io/EcoBuzios-Blog/
```

---

## Estrutura do projeto

```
circolando-blog/
├── .github/workflows/deploy.yml  ← Deploy automático (não mexa)
├── config.toml                   ← ⭐ Configure o baseURL aqui
├── content/posts/                ← Posts gerados (.md)
├── static/images/                ← Imagens dos posts
├── themes/circolando/            ← Tema visual completo
└── automacao/
    ├── config.py                 ← ⭐ Configure aqui
    └── run_daily.py              ← Rodar todo dia
```

---

## PASSO 1 — Criar conta no GitHub

1. Acesse **https://github.com** e clique em **"Sign up"**
2. Crie sua conta (pode usar o e-mail do Google)
3. Anote seu **nome de usuário** — você vai precisar dele

---

## PASSO 2 — Criar o repositório

1. No GitHub, clique em **"New repository"** (botão verde "+")
2. Nome do repositório: `circolando-blog`
3. Deixe como **Public** (obrigatório para GitHub Pages gratuito)
4. **NÃO** marque "Initialize with README"
5. Clique em **"Create repository"**

---

## PASSO 3 — Instalar Git e Hugo no seu computador

**Git:** https://git-scm.com/downloads — baixe e instale

**Hugo:** https://gohugo.io/installation/
- Windows: baixe `hugo_extended_X.X_windows-amd64.zip`, extraia e adicione ao PATH
- Mac: `brew install hugo`

Teste:
```
git --version
hugo version
```

---

## PASSO 4 — Configurar o projeto

### 4a. Edite `config.toml`:
Troque `SEU_USUARIO` pelo seu usuário do GitHub:
```toml
baseURL = "https://ttpap.github.io/EcoBuzios-Blog/"
```

### 4b. Edite `automacao/config.py`:
```python
GITHUB_USER = "antonpap"        # ← seu usuário GitHub
GITHUB_REPO = "EcoBuzios-Blog"
```

---

## PASSO 5 — Subir o projeto para o GitHub

Abra o terminal/prompt dentro da pasta `circolando-blog` e rode:

```bash
git init
git add .
git commit -m "primeiro commit CircoLando"
git branch -M main
git remote add origin https://github.com/ttpap/EcoBuzios-Blog.git
git push -u origin main
```

> Substitua `SEU_USUARIO` pelo seu usuário do GitHub.

---

## PASSO 6 — Ativar o GitHub Pages

1. No GitHub, abra o repositório `circolando-blog`
2. Clique em **Settings** (engrenagem)
3. Menu lateral: **Pages**
4. Em **"Source"**, selecione: **"GitHub Actions"**
5. Clique em **Save**

Pronto! Na próxima vez que você fizer `git push`, o GitHub Actions vai buildar e publicar o blog automaticamente.

---

## PASSO 7 — Ver o blog no ar

Após o primeiro push, aguarde ~2 minutos e acesse:
```
https://ttpap.github.io/EcoBuzios-Blog/
```

Você pode acompanhar o deploy em:
**GitHub → seu repositório → aba "Actions"**

---

## PASSO 8 — Instalar Python e rodar a automação

```bash
cd automacao
pip install -r requirements.txt

# Rodar o fluxo completo:
python run_daily.py

# Só testar a coleta:
python run_daily.py --so-coletar
```

---

## Automação diária (opcional)

**Windows — Agendador de Tarefas:**
1. Abra "Agendador de Tarefas"
2. Nova tarefa → Diariamente às 08:00
3. Ação: `python C:\caminho\circolando-blog\automacao\run_daily.py`

**Mac/Linux — Cron:**
```bash
crontab -e
# Adicione:
0 8 * * * cd /caminho/circolando-blog/automacao && python run_daily.py
```

---

## Adicionar um post manualmente

Crie um arquivo em `content/posts/YYYY-MM-DD-titulo.md`:

```markdown
---
title: "Título do Post"
subtitle: "Subtítulo complementar"
date: 2026-03-18
categories:
  - "Social"
tags:
  - "circo social"
description: "Resumo para SEO"
image: "/images/nome-da-imagem.jpg"
draft: false
---

Conteúdo em **Markdown**...
```

Depois:
```bash
git add .
git commit -m "novo post"
git push
```
O blog atualiza sozinho em ~2 minutos! 🎪

---

## Usar domínio próprio (ex: circolando.com.br)

1. No GitHub → Settings → Pages → **Custom domain**
2. Digite seu domínio e salve
3. No seu registrador (Registro.br), aponte o DNS para:
   ```
   185.199.108.153
   185.199.109.153
   185.199.110.153
   185.199.111.153
   ```
4. Aguarde até 24h para propagar

---

**Dúvidas?** Este sistema foi criado pelo Claude no Cowork. 🎪
