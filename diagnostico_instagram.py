"""
DIAGNÓSTICO COMPLETO - Instagram
Testa TUDO e mostra logs detalhados
"""

import sys
import os
import logging
import json
from datetime import datetime
from pathlib import Path
import requests
from config import CONFIG
from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired, ChallengeRequired,
    TwoFactorRequired, BadPassword,
    PleaseWaitFewMinutes, RateLimitError
)

# Setup logging detalhado
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = log_dir / f"diagnostico_instagram_{timestamp}.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def banner():
    print("\n" + "=" * 70)
    print("  🔬 DIAGNÓSTICO COMPLETO - INSTAGRAM")
    print("  Testando TUDO e logando TUDO!")
    print("=" * 70 + "\n")

def teste_1_config():
    """Teste 1: Verificar configurações"""
    print("\n" + "="*70)
    print("📋 TESTE 1: Verificando Configurações")
    print("="*70)

    logger.info("=== TESTE 1: Configurações ===")

    erros = []

    # Usuário
    if CONFIG["INSTAGRAM_USER"]:
        logger.info(f"✅ INSTAGRAM_USER: {CONFIG['INSTAGRAM_USER']}")
        print(f"✅ Usuário: {CONFIG['INSTAGRAM_USER']}")
    else:
        logger.error("❌ INSTAGRAM_USER não configurado!")
        print("❌ Usuário não configurado!")
        erros.append("INSTAGRAM_USER faltando")

    # Senha
    if CONFIG["INSTAGRAM_PASS"]:
        logger.info(f"✅ INSTAGRAM_PASS: {'*' * 10} (configurado)")
        print(f"✅ Senha: {'*' * 10} (configurado)")
    else:
        logger.error("❌ INSTAGRAM_PASS não configurado!")
        print("❌ Senha não configurada!")
        erros.append("INSTAGRAM_PASS faltando")

    # Proxy
    if all([CONFIG.get("PROXY_HOST"), CONFIG.get("PROXY_PORT")]):
        logger.info(f"⚠️ PROXY: {CONFIG['PROXY_HOST']}:{CONFIG['PROXY_PORT']}")
        print(f"⚠️ Proxy configurado: {CONFIG['PROXY_HOST']}:{CONFIG['PROXY_PORT']}")
    else:
        logger.warning("⚠️ Proxy NÃO configurado (pode dar bloqueio)")
        print("⚠️ Proxy NÃO configurado (Instagram pode bloquear)")

    return len(erros) == 0, erros


def teste_2_ip():
    """Teste 2: Verificar IP"""
    print("\n" + "="*70)
    print("🌐 TESTE 2: Verificando IP e Conectividade")
    print("="*70)

    logger.info("=== TESTE 2: IP e Conectividade ===")

    try:
        logger.info("Consultando IP público...")
        ip = requests.get("https://api.ipify.org", timeout=10).text
        logger.info(f"✅ IP público: {ip}")
        print(f"✅ Seu IP público: {ip}")

        # Testa se consegue acessar Instagram
        logger.info("Testando acesso ao Instagram.com...")
        response = requests.get("https://www.instagram.com/", timeout=10)
        logger.info(f"✅ Instagram acessível - Status: {response.status_code}")
        print(f"✅ Instagram.com acessível (Status: {response.status_code})")

        return True, ip

    except requests.exceptions.Timeout:
        logger.error("❌ Timeout ao acessar internet!")
        print("❌ Timeout - Problema de conexão!")
        return False, None

    except Exception as e:
        logger.error(f"❌ Erro ao testar IP/conectividade: {e}", exc_info=True)
        print(f"❌ Erro: {e}")
        return False, None


def teste_3_sessao():
    """Teste 3: Verificar session.json"""
    print("\n" + "="*70)
    print("💾 TESTE 3: Verificando Sessão Salva")
    print("="*70)

    logger.info("=== TESTE 3: Sessão Salva ===")

    session_file = Path("session.json")

    if session_file.exists():
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            logger.info(f"✅ session.json encontrado")
            print(f"✅ session.json existe")

            # Verifica idade do arquivo
            idade_segundos = (datetime.now() - datetime.fromtimestamp(session_file.stat().st_mtime)).total_seconds()
            idade_horas = idade_segundos / 3600

            logger.info(f"📅 Idade da sessão: {idade_horas:.1f} horas")
            print(f"📅 Sessão tem {idade_horas:.1f} horas")

            if idade_horas > 24:
                logger.warning("⚠️ Sessão tem mais de 24h (pode estar expirada)")
                print("⚠️ Sessão antiga (mais de 24h) - pode estar expirada")

            # Verifica campos importantes
            if 'authorization_data' in session_data:
                logger.info("✅ Sessão tem dados de autorização")
                print("✅ Sessão parece válida")
            else:
                logger.warning("⚠️ Sessão pode estar incompleta")
                print("⚠️ Sessão pode estar incompleta")

            return True, session_file

        except Exception as e:
            logger.error(f"❌ Erro ao ler session.json: {e}", exc_info=True)
            print(f"❌ Erro ao ler sessão: {e}")
            return False, session_file
    else:
        logger.warning("⚠️ session.json NÃO encontrado")
        print("⚠️ session.json não existe (vai fazer login fresh)")
        return True, None


def teste_4_login():
    """Teste 4: Tentar login"""
    print("\n" + "="*70)
    print("🔐 TESTE 4: Testando Login no Instagram")
    print("="*70)

    logger.info("=== TESTE 4: Login ===")

    try:
        logger.info("Inicializando Client...")
        client = Client()
        client.delay_range = [3, 7]  # Delay maior para evitar bloqueio

        logger.info("Client criado com sucesso")
        print("✅ Client criado")

        # Tenta carregar sessão
        session_loaded = False
        session_file = Path("session.json")

        if session_file.exists():
            try:
                logger.info("Tentando carregar session.json...")
                client.load_settings(str(session_file))
                logger.info("✅ Sessão carregada")
                print("✅ Sessão anterior carregada")
                session_loaded = True
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar sessão: {e}")
                print(f"⚠️ Não conseguiu carregar sessão: {e}")

        # Tenta login
        username = CONFIG["INSTAGRAM_USER"]
        password = CONFIG["INSTAGRAM_PASS"]

        logger.info(f"Tentando login como {username}...")
        print(f"🔑 Tentando login como {username}...")

        try:
            client.login(username, password)
            logger.info("✅ LOGIN REALIZADO COM SUCESSO!")
            print("✅ LOGIN FUNCIONOU!")

            # Salva sessão
            if not session_loaded:
                logger.info("Salvando nova sessão...")
                client.dump_settings("session.json")
                logger.info("✅ Sessão salva")
                print("✅ Sessão salva")

            # Testa pegando info do próprio usuário
            logger.info("Testando API - buscando info do usuário logado...")
            user_id = client.user_id
            logger.info(f"✅ User ID: {user_id}")
            print(f"✅ User ID obtido: {user_id}")

            return True, client

        except PleaseWaitFewMinutes as e:
            logger.error(f"❌ Instagram pediu para aguardar: {e}")
            print("❌ Instagram bloqueou temporariamente!")
            print("💡 Aguarde 10-15 minutos e tente novamente")
            return False, None

        except ChallengeRequired as e:
            logger.error(f"❌ Desafio de segurança necessário: {e}")
            print("❌ Instagram pediu verificação de segurança!")
            print("💡 Acesse instagram.com pelo navegador e resolva")
            return False, None

        except TwoFactorRequired as e:
            logger.error(f"❌ 2FA ativado: {e}")
            print("❌ Autenticação de dois fatores ativada!")
            print("💡 Desative 2FA ou implemente suporte no código")
            return False, None

        except BadPassword as e:
            logger.error(f"❌ Senha incorreta: {e}")
            print("❌ Senha incorreta!")
            print("💡 Verifique INSTAGRAM_PASS no .env")
            return False, None

        except Exception as e:
            logger.error(f"❌ Erro ao fazer login: {e}", exc_info=True)
            print(f"❌ Erro no login: {e}")

            # Analisa o erro
            erro_str = str(e).lower()

            if "checkpoint" in erro_str:
                print("💡 Conta com checkpoint - resolva no app Instagram")
            elif "spam" in erro_str:
                print("💡 Detectado como spam - use proxy ou aguarde")
            elif "ip" in erro_str or "block" in erro_str:
                print("💡 IP bloqueado - configure proxy residencial")

            return False, None

    except Exception as e:
        logger.error(f"❌ Erro fatal no teste de login: {e}", exc_info=True)
        print(f"❌ Erro fatal: {e}")
        return False, None


def teste_5_busca_perfil(client):
    """Teste 5: Tentar buscar um perfil público"""
    print("\n" + "="*70)
    print("🔍 TESTE 5: Testando Busca de Perfil")
    print("="*70)

    logger.info("=== TESTE 5: Busca de Perfil ===")

    if not client:
        logger.error("❌ Cliente não disponível (login falhou)")
        print("❌ Pulando teste (login não funcionou)")
        return False

    try:
        # Testa com perfil público conhecido
        perfil_teste = "instagram"  # Perfil oficial do Instagram

        logger.info(f"Buscando perfil @{perfil_teste}...")
        print(f"🔍 Buscando @{perfil_teste}...")

        user_info = client.user_info_by_username(perfil_teste)

        logger.info(f"✅ Perfil encontrado!")
        logger.info(f"   Username: {user_info.username}")
        logger.info(f"   Seguidores: {user_info.follower_count}")
        logger.info(f"   Posts: {user_info.media_count}")

        print(f"✅ Perfil encontrado!")
        print(f"   Username: {user_info.username}")
        print(f"   Seguidores: {user_info.follower_count:,}")
        print(f"   Posts: {user_info.media_count}")

        return True

    except RateLimitError as e:
        logger.error(f"❌ Rate limit atingido: {e}")
        print("❌ Muitas requisições! Instagram bloqueou temporariamente")
        print("💡 Aguarde 15-30 minutos")
        return False

    except Exception as e:
        logger.error(f"❌ Erro ao buscar perfil: {e}", exc_info=True)
        print(f"❌ Erro: {e}")

        erro_str = str(e).lower()
        if "data" in erro_str or "json" in erro_str:
            print("💡 Instagram retornou resposta inesperada (possível bloqueio)")

        return False


def main():
    banner()

    print(f"📝 Log detalhado será salvo em: {log_file}\n")
    logger.info("=== INICIANDO DIAGNÓSTICO COMPLETO ===")

    resultados = {}

    # Teste 1: Config
    ok, erros = teste_1_config()
    resultados['config'] = ok
    if not ok:
        logger.error(f"Teste 1 falhou: {erros}")
        print(f"\n❌ Configure os itens faltando no .env antes de continuar!")
        return

    # Teste 2: IP
    ok, ip = teste_2_ip()
    resultados['ip'] = ok
    if not ok:
        logger.error("Teste 2 falhou: Sem conectividade")
        print(f"\n❌ Verifique sua conexão com a internet!")
        return

    # Teste 3: Sessão
    ok, session_file = teste_3_sessao()
    resultados['sessao'] = ok

    # Teste 4: Login (CRÍTICO)
    ok, client = teste_4_login()
    resultados['login'] = ok

    if not ok:
        print("\n" + "="*70)
        print("❌ LOGIN FALHOU - Este é o problema principal!")
        print("="*70)

        print("\n💡 PRÓXIMOS PASSOS:")
        print("   1. Verifique se consegue logar no Instagram pelo navegador")
        print("   2. Se tiver verificação pendente, resolva primeiro")
        print("   3. Considere configurar proxy residencial")
        print("   4. Aguarde 15-30 minutos se foi bloqueio temporário")

        if session_file and session_file.exists():
            print("\n🗑️  DICA: Tente deletar session.json e rodar novamente:")
            print("   del session.json")

        logger.error("=== DIAGNÓSTICO FINALIZADO COM ERRO ===")
        return

    # Teste 5: Busca
    ok = teste_5_busca_perfil(client)
    resultados['busca'] = ok

    # Resumo final
    print("\n" + "="*70)
    print("📊 RESUMO DO DIAGNÓSTICO")
    print("="*70)

    for teste, resultado in resultados.items():
        status = "✅" if resultado else "❌"
        logger.info(f"{status} {teste.upper()}: {'OK' if resultado else 'FALHOU'}")
        print(f"{status} {teste.upper()}: {'OK' if resultado else 'FALHOU'}")

    if all(resultados.values()):
        print("\n🎉 TUDO FUNCIONANDO! Pode usar o main.py normalmente!")
        logger.info("=== DIAGNÓSTICO: TUDO OK ===")
    else:
        print("\n⚠️ Alguns testes falharam. Veja os logs acima para detalhes.")
        logger.warning("=== DIAGNÓSTICO: Alguns testes falharam ===")

    print(f"\n📝 Log completo salvo em: {log_file}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Diagnóstico interrompido pelo usuário.\n")
        logger.warning("Diagnóstico interrompido (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        logger.critical(f"Erro fatal não tratado: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
