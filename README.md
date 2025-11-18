# 📊 Analisador de Instagram com GPT-4

Sistema completo de análise de comentários do Instagram usando GPT-4, com suporte a proxy residencial para evitar bloqueios.

---

## 🚀 INÍCIO RÁPIDO

### Quer usar AGORA? (Rodando local)
👉 **[GUIA_USO_LOCAL.md](GUIA_USO_LOCAL.md)** - Configure em 5 minutos!

### Quer rodar na nuvem 24/7? (Streamlit Cloud)
👉 **[GUIA_PROXY_RESIDENCIAL.md](GUIA_PROXY_RESIDENCIAL.md)** - Proxy residencial passo a passo!

---

## ✨ Funcionalidades

- 🔍 Coleta automática de posts e comentários do Instagram
- 🤖 Análise inteligente com GPT-4 (sentimentos, categorias, intenções)
- 📊 Relatórios detalhados no Google Sheets
- 💾 Banco de dados SQLite para análise incremental
- 🌐 **Suporte a proxy residencial (evita bloqueio do Instagram)**
- 🚀 Interface web com Streamlit
- 💰 Economia de 90% no custo de GPT (análise apenas de novos comentários)

---

## 🚀 Deploy no Streamlit Cloud (Recomendado)

### 1️⃣ Preparação

1. Faça fork/clone deste repositório
2. Configure os secrets no Streamlit Cloud

### 2️⃣ Configurar Secrets no Streamlit

Acesse: **Settings → Secrets** e adicione:

```toml
# Instagram
INSTAGRAM_USER = "seu_usuario_ou_email"
INSTAGRAM_PASS = "sua_senha"

# OpenAI
OPENAI_KEY = "sk-sua-chave-aqui"

# Google Sheets
PLANILHA_ID = "id_da_sua_planilha"

# PROXY RESIDENCIAL (IMPORTANTE!)
PROXY_HOST = "45.38.107.97"
PROXY_PORT = "6014"
PROXY_USER = "xddyewxz"
PROXY_PASS = "flmpw9zuxfkn"

# Google Credentials (cole o JSON inteiro)
[google_credentials]
type = "service_account"
project_id = "seu-projeto"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

### 3️⃣ Deploy

1. Faça push do código para GitHub
2. No Streamlit Cloud: **New app → Deploy**
3. Aguarde o deploy (2-3 minutos)
4. Acesse sua aplicação!

---

## 💻 Uso Local

### 1️⃣ Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo

# Instale as dependências
pip install -r requirements.txt
```

### 2️⃣ Configuração

Copie o `.env.example` para `.env` e preencha:

```bash
cp .env.example .env
```

Edite o `.env` com suas credenciais:

```env
INSTAGRAM_USER=seu_usuario
INSTAGRAM_PASS=sua_senha
OPENAI_KEY=sk-...
PLANILHA_ID=seu_id
PROXY_HOST=seu_proxy
PROXY_PORT=porta
PROXY_USER=usuario_proxy
PROXY_PASS=senha_proxy
```

### 3️⃣ Teste o Proxy

**IMPORTANTE**: Antes de usar, teste se o proxy está funcionando!

```bash
python testar_proxy.py
```

Você deve ver:

```
✅ IPs DIFERENTES! Proxy está funcionando! 🎉
   Sem proxy: 123.456.789.0
   Com proxy: 45.38.107.97
```

### 4️⃣ Execute

**Modo CLI (recomendado para primeira vez):**

```bash
python main.py
```

**Modo Web (Streamlit):**

```bash
streamlit run app.py
```

---

## 🌐 Sobre o Proxy

### Por que usar proxy?

O Instagram **bloqueia IPs de servidores** (data centers). Ao fazer login de um IP suspeito, você recebe:

```
❌ IP address is added to the blacklist of the Instagram Server
```

### Tipos de Proxy

1. **Datacenter** (gratuito/barato, como Webshare)
   - ⚠️ Pode ser bloqueado
   - ✅ Melhor que nada
   - 💡 Use o fornecido acima como teste

2. **Residencial** (pago, mais confiável)
   - ✅ IPs reais de residências
   - ✅ Raramente bloqueado
   - 💰 Mais caro (~$5-10/GB)

### Configuração do Proxy

O sistema já está configurado para usar proxy! Basta adicionar as credenciais nos secrets/variáveis de ambiente.

O código automaticamente:
- ✅ Configura proxy no instagrapi
- ✅ Testa se o proxy está funcionando
- ✅ Mostra IP antes/depois do proxy
- ✅ Fornece logs detalhados

---

## 📁 Estrutura do Projeto

```
.
├── app.py                  # Interface Streamlit
├── main.py                 # Script CLI
├── config.py               # Configurações centralizadas
├── coletor.py              # Coleta dados do Instagram (COM PROXY!)
├── analisador.py           # Análise GPT-4
├── database.py             # Banco SQLite
├── sheets_reporter.py      # Google Sheets
├── testar_proxy.py         # Teste de proxy
├── requirements.txt        # Dependências
└── README.md              # Este arquivo
```

---

## 🔧 Troubleshooting

### ❌ "IP address is added to the blacklist"

**Solução:**
1. Configure um proxy residencial
2. Teste com `python testar_proxy.py`
3. Aguarde 24h se já tentou muitas vezes

### ❌ "Challenge Required"

**Solução:**
1. Entre no app do Instagram
2. Confirme que é você
3. Tente novamente

### ❌ Proxy não funciona

**Solução:**
1. Execute `python testar_proxy.py`
2. Verifique se as credenciais estão corretas
3. Teste outro proxy

### ❌ Google Credentials não encontrado

**Solução (Streamlit Cloud):**
- Adicione `google_credentials` nos secrets como JSON

**Solução (Local):**
- Baixe o arquivo `credentials.json` do Google Cloud Console
- Coloque na raiz do projeto

---

## 📊 Exemplo de Uso

1. **Configure o proxy** nos secrets/env
2. **Teste o proxy**: `python testar_proxy.py`
3. **Execute**: `streamlit run app.py`
4. **Digite os perfis** que deseja analisar
5. **Aguarde** a análise (login → coleta → GPT → planilha)
6. **Acesse** o Google Sheets gerado!

---

## 💰 Custos Estimados

- **GPT-4o-mini**: ~$0.0001 por comentário
- **100 comentários**: ~$0.01
- **1000 comentários**: ~$0.10

Com análise incremental, você **só paga pelos comentários novos**!

---

## 🛡️ Segurança

- ✅ Credenciais NUNCA são commitadas
- ✅ `.gitignore` configurado
- ✅ Secrets do Streamlit são encriptados
- ✅ Variáveis de ambiente locais

**Arquivos sensíveis ignorados:**
- `credentials.json`
- `config.py` (apenas `config.example.py` é versionado)
- `.env`
- `session.json`
- `*.db`

---

## 🤝 Contribuindo

Pull requests são bem-vindos! Para mudanças importantes, abra uma issue primeiro.

---

## 📝 Licença

MIT License - use livremente!

---

## 🆘 Suporte

Problemas? Abra uma issue no GitHub!

**Principais correções desta versão:**
- ✅ Proxy configurado corretamente no `app.py`
- ✅ Logs de debug para verificar proxy
- ✅ Script de teste `testar_proxy.py`
- ✅ Documentação completa
- ✅ Correção de bugs no `main.py`

---

**Feito com ❤️ para análise de Instagram**
