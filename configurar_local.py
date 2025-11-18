"""
SCRIPT AUXILIAR: Configurar .env para uso local
Cria o arquivo .env com suas credenciais de forma interativa
"""

import os
from pathlib import Path


def banner():
    print("\n" + "=" * 70)
    print("  🔧 CONFIGURADOR DE AMBIENTE LOCAL")
    print("  Cria arquivo .env com suas credenciais")
    print("=" * 70 + "\n")


def input_seguro(label, exemplo="", obrigatorio=True, ocultar=False):
    """Input com validação"""
    while True:
        if exemplo:
            prompt = f"{label}\n  Exemplo: {exemplo}\n  → "
        else:
            prompt = f"{label}\n  → "

        if ocultar:
            import getpass
            valor = getpass.getpass(prompt)
        else:
            valor = input(prompt).strip()

        if valor or not obrigatorio:
            return valor
        else:
            print("  ⚠️ Este campo é obrigatório!\n")


def main():
    banner()

    print("📝 Vou te ajudar a criar o arquivo .env\n")
    print("⚠️  IMPORTANTE: Essas credenciais ficam APENAS no seu PC!")
    print("    Não serão enviadas pro GitHub (já está no .gitignore)\n")

    input("Pressione ENTER para começar...")

    print("\n" + "=" * 70)
    print("1️⃣  INSTAGRAM")
    print("=" * 70 + "\n")

    instagram_user = input_seguro(
        "Digite seu usuário/email do Instagram:",
        exemplo="meuemail@gmail.com"
    )

    instagram_pass = input_seguro(
        "Digite sua senha do Instagram:",
        ocultar=True
    )

    print("\n" + "=" * 70)
    print("2️⃣  OPENAI")
    print("=" * 70 + "\n")

    print("💡 Pegue sua chave em: https://platform.openai.com/api-keys\n")

    openai_key = input_seguro(
        "Digite sua chave da OpenAI:",
        exemplo="sk-proj-..."
    )

    print("\n" + "=" * 70)
    print("3️⃣  GOOGLE SHEETS")
    print("=" * 70 + "\n")

    print("💡 O ID está na URL da planilha:")
    print("   https://docs.google.com/spreadsheets/d/[ESTE_ID_AQUI]/edit\n")

    planilha_id = input_seguro(
        "Digite o ID da sua planilha:",
        exemplo="1a2b3c4d5e6f..."
    )

    print("\n" + "=" * 70)
    print("4️⃣  PROXY (OPCIONAL)")
    print("=" * 70 + "\n")

    print("⚠️  Para uso LOCAL, NÃO precisa de proxy!")
    print("   Seu IP residencial já funciona bem.\n")

    usar_proxy = input("Quer configurar proxy mesmo assim? (s/N): ").strip().lower()

    if usar_proxy == 's':
        proxy_host = input_seguro("PROXY_HOST:", obrigatorio=False)
        proxy_port = input_seguro("PROXY_PORT:", obrigatorio=False)
        proxy_user = input_seguro("PROXY_USER:", obrigatorio=False)
        proxy_pass = input_seguro("PROXY_PASS:", ocultar=True, obrigatorio=False)
    else:
        proxy_host = ""
        proxy_port = ""
        proxy_user = ""
        proxy_pass = ""

    # Cria conteúdo do .env
    env_content = f"""# ============================================
# CREDENCIAIS - USO LOCAL
# Gerado automaticamente em {Path.cwd()}
# ============================================

# INSTAGRAM
INSTAGRAM_USER={instagram_user}
INSTAGRAM_PASS={instagram_pass}

# OPENAI
OPENAI_KEY={openai_key}

# GOOGLE SHEETS
PLANILHA_ID={planilha_id}

# PROXY (deixe vazio para usar seu IP residencial)
PROXY_HOST={proxy_host}
PROXY_PORT={proxy_port}
PROXY_USER={proxy_user}
PROXY_PASS={proxy_pass}
"""

    # Salva arquivo
    env_path = Path(__file__).parent / '.env'

    if env_path.exists():
        print("\n⚠️  Arquivo .env já existe!")
        sobrescrever = input("   Quer sobrescrever? (s/N): ").strip().lower()
        if sobrescrever != 's':
            print("\n❌ Operação cancelada!")
            return

    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)

    print("\n" + "=" * 70)
    print("✅ ARQUIVO .env CRIADO COM SUCESSO!")
    print("=" * 70)

    print(f"\n📁 Local: {env_path}")
    print("\n📋 Conteúdo (senhas ocultas):")
    print("-" * 70)
    print(f"INSTAGRAM_USER={instagram_user}")
    print(f"INSTAGRAM_PASS={'*' * len(instagram_pass)}")
    print(f"OPENAI_KEY={'*' * 10}...{openai_key[-4:] if len(openai_key) > 4 else '***'}")
    print(f"PLANILHA_ID={planilha_id}")

    if proxy_host:
        print(f"PROXY_HOST={proxy_host}")
        print(f"PROXY_PORT={proxy_port}")
        print(f"PROXY_USER={proxy_user}")
        print(f"PROXY_PASS={'*' * len(proxy_pass)}")
    else:
        print("PROXY: (não configurado - usa IP residencial)")

    print("-" * 70)

    print("\n🚀 PRÓXIMOS PASSOS:")
    print("\n1. Instale as dependências:")
    print("   pip install -r requirements.txt")
    print("\n2. Execute o app:")
    print("   streamlit run app.py")
    print("\n3. Ou use no terminal:")
    print("   python main.py")

    print("\n" + "=" * 70)
    print("✅ TUDO PRONTO! Pode começar a usar!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Configuração cancelada pelo usuário.\n")
    except Exception as e:
        print(f"\n❌ Erro: {e}\n")
