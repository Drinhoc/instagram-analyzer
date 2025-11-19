"""
TESTE URGENTE - Login Instagram com Proxy Pago
Testa se o login funciona com as novas credenciais do proxy
"""

import sys
from config import CONFIG
from coletor import ColetorInstagram

def main():
    print("\n" + "=" * 70)
    print("  🚨 TESTE URGENTE - LOGIN INSTAGRAM")
    print("=" * 70)

    # Mostra configuração
    print("\n📋 CONFIGURAÇÃO ATUAL:")
    print(f"  Instagram: {CONFIG['INSTAGRAM_USER']}")
    print(f"  Proxy: {CONFIG['PROXY_HOST']}:{CONFIG['PROXY_PORT']}")
    print(f"  User: {CONFIG['PROXY_USER']}")
    print()

    # Cria coletor (já configura proxy)
    print("🔧 Inicializando coletor...")
    coletor = ColetorInstagram()

    # Tenta login
    print("\n🔐 TESTANDO LOGIN...")
    print("-" * 70)

    try:
        # Faz login (agora lança exceção se falhar)
        coletor.fazer_login()

        print("\n" + "=" * 70)
        print("  ✅ LOGIN FUNCIONOU!!!")
        print("  🎉 PROXY ESTÁ OK!")
        print("=" * 70)
        print("\n💡 Agora pode fazer deploy no Streamlit tranquilo!")

        return True

    except Exception as e:
        print("\n" + "=" * 70)
        print("  ❌ LOGIN FALHOU!")
        print("=" * 70)

        erro_str = str(e)

        print(f"\n🔍 ERRO ESPECÍFICO:")
        print(f"  {erro_str}")

        print(f"\n💡 DIAGNÓSTICO:")

        if "CHALLENGE_REQUIRED" in erro_str or "CHECKPOINT" in erro_str:
            print("  🚨 Conta com verificação de segurança!")
            print()
            print("  📝 AÇÃO NECESSÁRIA:")
            print("  1. Abra instagram.com no navegador")
            print("  2. Faça login com: papo.fiadobr@gmail.com")
            print("  3. Resolva a verificação de segurança")
            print("  4. Rode este script novamente")

        elif "IP_BLOCKED" in erro_str:
            print("  🚫 IP bloqueado pelo Instagram!")
            print()
            print("  💡 POSSÍVEIS CAUSAS:")
            print("  1. Proxy não está funcionando corretamente")
            print("  2. IP do proxy já está bloqueado")
            print("  3. Configuração do proxy incorreta")
            print()
            print("  📝 AÇÕES:")
            print("  1. Verifique no painel do Webshare.io se o proxy está ativo")
            print("  2. Tente outro proxy da lista")
            print("  3. Aguarde 15-30 minutos e tente novamente")

        elif "BAD_CREDENTIALS" in erro_str:
            print("  🔑 Credenciais incorretas!")
            print()
            print("  📝 VERIFIQUE:")
            print("  1. Email está correto? papo.fiadobr@gmail.com")
            print("  2. Senha está correta? (confira no .env)")
            print("  3. Consegue logar no instagram.com com essas credenciais?")

        elif "TWO_FACTOR" in erro_str:
            print("  🔐 Autenticação de 2 fatores ativada!")
            print()
            print("  📝 AÇÃO:")
            print("  Desative o 2FA temporariamente em instagram.com/accounts/two_factor_authentication/")

        else:
            print("  ❓ Erro desconhecido!")
            print()
            print("  📝 AÇÕES:")
            print("  1. Copie o erro acima")
            print("  2. Me mande amanhã que eu te ajudo!")

        print("\n" + "=" * 70)

        return False


if __name__ == "__main__":
    try:
        sucesso = main()
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste cancelado pelo usuário.\n")
        sys.exit(1)
