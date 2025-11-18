# 🏠 GUIA: Rodar Local (Seu WiFi)

## Por que rodar local funciona?
- ✅ Seu IP de casa é RESIDENCIAL (Instagram não bloqueia)
- ✅ Não precisa proxy
- ✅ Funciona 90% das vezes
- ❌ Desvantagem: precisa deixar PC ligado

---

## 🚀 PASSO A PASSO COMPLETO

### 1. Puxa as últimas mudanças do GitHub

```bash
cd "C:\Users\Pedro\Documents\ANALISTA DE INSTAGRAM"
git pull
```

### 2. Cria arquivo .env (CREDENCIAIS LOCAIS)

Copia o .env.example:
```bash
copy .env.example .env
```

### 3. Edita o .env com suas credenciais

Abre o arquivo `.env` e preenche:

```env
# INSTAGRAM (sua conta que funciona no celular)
INSTAGRAM_USER=seu_usuario_ou_email_aqui
INSTAGRAM_PASS=sua_senha_aqui

# OPENAI
OPENAI_KEY=sua_chave_openai_aqui

# GOOGLE SHEETS
PLANILHA_ID=id_da_sua_planilha_aqui

# PROXY - DEIXA VAZIO! (usa seu IP residencial)
PROXY_HOST=
PROXY_PORT=
PROXY_USER=
PROXY_PASS=
```

**IMPORTANTE:**
- ✅ Preenche só Instagram, OpenAI e Planilha
- ✅ Deixa proxy VAZIO (não precisa!)
- ✅ Não commita esse arquivo (já está no .gitignore)

### 4. Instala dependências (se não tiver)

```bash
pip install -r requirements.txt
```

### 5. RODA!

**Opção A: Interface Web (RECOMENDADO)**
```bash
streamlit run app.py
```

**Opção B: Terminal/CLI**
```bash
python main.py
```

### 6. Usa normalmente!

- ✅ Digite os perfis que quer analisar
- ✅ Aguarde a coleta
- ✅ Veja o relatório no Google Sheets!

---

## ⚠️ IMPORTANTE

1. **NÃO commita o .env:**
   - Já está no .gitignore
   - Mas confira que não vai pro GitHub!

2. **Mantém PC ligado:**
   - Enquanto estiver analisando
   - Pode fechar depois que terminar

3. **Usa com moderação:**
   - Não analise 50 perfis de uma vez
   - Dá intervalos entre análises
   - Instagram monitora automação

---

## 🆘 Se der erro

**"Módulo não encontrado":**
```bash
pip install -r requirements.txt
```

**"Credenciais não encontradas":**
- Verifica se o .env está preenchido
- Confirma que está na pasta raiz do projeto

**"Erro de login":**
- Testa no celular primeiro
- Confere usuário/senha no .env
- Aguarda alguns minutos e tenta de novo

---

## 💡 Dica

Depois que configurar o proxy residencial, você pode comentar/apagar o .env e usar só o Streamlit Cloud!

---

**Pronto! Você já pode usar localmente enquanto prepara o proxy residencial!** 🎉
