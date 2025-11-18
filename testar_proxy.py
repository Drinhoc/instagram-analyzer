"""
TESTE DE PROXY - Valida configuração antes de usar no Instagram
Execute este script para verificar se o proxy está funcionando!
"""

import sys
from config import CONFIG, get_proxy_dict
import requests


def banner():
    print("\n" + "=" * 70)
    print("  🔧 TESTE DE CONFIGURAÇÃO DE PROXY")
    print("  Valida se o proxy está funcionando antes de usar no Instagram")
    print("=" * 70 + "\n")


def testar_ip_sem_proxy():
    """Testa conexão sem proxy"""
    print("📍 PASSO 1: Verificando IP sem proxy...")
    try:
        ip = requests.get("https://api.ipify.org", timeout=5).text
        print(f"✅ Seu IP: {ip}")
        return ip
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


def testar_ip_com_proxy():
    """Testa conexão com proxy"""
    print("\n🌐 PASSO 2: Testando proxy configurado...")

    proxy_dict = get_proxy_dict()

    if not proxy_dict:
        print("❌ PROXY NÃO CONFIGURADO!")
        print("\n💡 Configure as variáveis de ambiente:")
        print("   - PROXY_HOST")
        print("   - PROXY_PORT")
        print("   - PROXY_USER")
        print("   - PROXY_PASS")
        return None

    print(f"🔑 Host: {CONFIG['PROXY_HOST']}:{CONFIG['PROXY_PORT']}")
    print(f"🔑 User: {CONFIG['PROXY_USER']}")

    try:
        ip = requests.get("https://api.ipify.org", proxies=proxy_dict, timeout=15).text
        print(f"✅ IP com proxy: {ip}")
        return ip
    except requests.exceptions.ProxyError as e:
        print(f"❌ ERRO DE PROXY: {e}")
        print("\n💡 Possíveis causas:")
        print("   • Credenciais incorretas (user/pass)")
        print("   • Host/porta inválidos")
        print("   • Proxy offline")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


def testar_proxy_instagram():
    """Testa se consegue acessar Instagram através do proxy"""
    print("\n📸 PASSO 3: Testando acesso ao Instagram...")

    proxy_dict = get_proxy_dict()

    if not proxy_dict:
        print("❌ Pulando (sem proxy configurado)")
        return False

    try:
        response = requests.get(
            "https://www.instagram.com/",
            proxies=proxy_dict,
            timeout=15,
            headers={'User-Agent': 'Mozilla/5.0'}
        )

        if response.status_code == 200:
            print("✅ Instagram acessível através do proxy!")
            return True
        else:
            print(f"⚠️ Status: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Erro ao acessar Instagram: {e}")
        return False


def main():
    banner()

    # Testa IP sem proxy
    ip_sem_proxy = testar_ip_sem_proxy()

    # Testa IP com proxy
    ip_com_proxy = testar_ip_com_proxy()

    # Compara IPs
    if ip_sem_proxy and ip_com_proxy:
        print("\n" + "=" * 70)
        print("📊 RESULTADO DA COMPARAÇÃO")
        print("=" * 70)

        if ip_sem_proxy != ip_com_proxy:
            print(f"✅ IPs DIFERENTES! Proxy está funcionando! 🎉")
            print(f"   Sem proxy: {ip_sem_proxy}")
            print(f"   Com proxy: {ip_com_proxy}")
        else:
            print(f"⚠️ IPs IGUAIS! Proxy pode não estar ativo!")
            print(f"   IP: {ip_sem_proxy}")

    # Testa acesso ao Instagram
    instagram_ok = testar_proxy_instagram()

    # Resumo final
    print("\n" + "=" * 70)
    print("✅ RESUMO FINAL")
    print("=" * 70)

    if ip_com_proxy and instagram_ok:
        print("✅ PROXY FUNCIONANDO CORRETAMENTE!")
        print("✅ Instagram acessível através do proxy!")
        print("\n💡 Você pode prosseguir com a análise do Instagram.")
    elif ip_com_proxy:
        print("⚠️ Proxy funciona mas Instagram pode estar bloqueado")
        print("\n💡 Tente mesmo assim, mas pode precisar de proxy residencial.")
    else:
        print("❌ PROXY NÃO ESTÁ FUNCIONANDO!")
        print("\n💡 Verifique:")
        print("   1. Credenciais do proxy (user/pass)")
        print("   2. Host e porta corretos")
        print("   3. Proxy está online")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
        sys.exit(1)
