"""
MÓDULO DE BANCO DE DADOS
Gerenciamento completo do SQLite com queries otimizadas
"""

import sqlite3
import json
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import List, Dict, Optional, Tuple
import os


class Database:
    """Classe para gerenciar o banco de dados SQLite"""
    
    def __init__(self, db_path="instagram_analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexão com banco"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Retorna dict-like objects
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Inicializa banco e cria tabelas"""
        try:
            with self.get_connection() as conn:
                # Cria tabelas direto (mais confiável que ler arquivo)
                conn.executescript("""
                    -- Perfis monitorados
                    CREATE TABLE IF NOT EXISTS perfis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        nome_completo TEXT,
                        biografia TEXT,
                        seguidores INTEGER,
                        seguindo INTEGER,
                        total_posts INTEGER,
                        eh_comercial BOOLEAN DEFAULT 0,
                        eh_verificado BOOLEAN DEFAULT 0,
                        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data_ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ativo BOOLEAN DEFAULT 1
                    );

                    -- Posts coletados
                    CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        perfil_id INTEGER NOT NULL,
                        post_id TEXT UNIQUE NOT NULL,
                        codigo TEXT NOT NULL,
                        url TEXT NOT NULL,
                        tipo TEXT,
                        caption TEXT,
                        likes INTEGER DEFAULT 0,
                        comentarios_count INTEGER DEFAULT 0,
                        visualizacoes INTEGER DEFAULT 0,
                        alcance INTEGER,
                        impressoes INTEGER,
                        salvamentos INTEGER,
                        data_post TIMESTAMP NOT NULL,
                        data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data_ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        analisado BOOLEAN DEFAULT 0,
                        FOREIGN KEY (perfil_id) REFERENCES perfis(id)
                    );

                    -- Comentários
                    CREATE TABLE IF NOT EXISTS comentarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER NOT NULL,
                        comentario_id TEXT UNIQUE NOT NULL,
                        usuario TEXT NOT NULL,
                        nome_completo TEXT,
                        texto TEXT NOT NULL,
                        likes INTEGER DEFAULT 0,
                        data_comentario TIMESTAMP NOT NULL,
                        data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data_ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        analisado BOOLEAN DEFAULT 0,
                        deletado BOOLEAN DEFAULT 0,
                        editado BOOLEAN DEFAULT 0,
                        FOREIGN KEY (post_id) REFERENCES posts(id)
                    );

                    -- Análises GPT
                    CREATE TABLE IF NOT EXISTS analises (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        comentario_id INTEGER UNIQUE NOT NULL,
                        sentimento TEXT,
                        categoria TEXT,
                        topico TEXT,
                        urgencia TEXT,
                        intent TEXT,
                        palavras_chave TEXT,
                        resumo TEXT,
                        sugestao_resposta TEXT,
                        resposta_sugerida TEXT,
                        custo_gpt REAL DEFAULT 0,
                        data_analise TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (comentario_id) REFERENCES comentarios(id)
                    );

                    -- Execuções
                    CREATE TABLE IF NOT EXISTS execucoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        perfil_id INTEGER NOT NULL,
                        tipo TEXT,
                        posts_processados INTEGER DEFAULT 0,
                        comentarios_novos INTEGER DEFAULT 0,
                        comentarios_atualizados INTEGER DEFAULT 0,
                        analises_realizadas INTEGER DEFAULT 0,
                        custo_total_gpt REAL DEFAULT 0,
                        data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data_fim TIMESTAMP,
                        duracao_segundos INTEGER,
                        status TEXT DEFAULT 'em_andamento',
                        mensagem_erro TEXT,
                        planilha_url TEXT,
                        FOREIGN KEY (perfil_id) REFERENCES perfis(id)
                    );

                    -- Alertas
                    CREATE TABLE IF NOT EXISTS alertas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        execucao_id INTEGER NOT NULL,
                        comentario_id INTEGER,
                        tipo TEXT NOT NULL,
                        descricao TEXT NOT NULL,
                        severidade INTEGER DEFAULT 1,
                        resolvido BOOLEAN DEFAULT 0,
                        data_alerta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data_resolucao TIMESTAMP,
                        FOREIGN KEY (execucao_id) REFERENCES execucoes(id),
                        FOREIGN KEY (comentario_id) REFERENCES comentarios(id)
                    );

                    -- Índices para performance
                    CREATE INDEX IF NOT EXISTS idx_posts_perfil ON posts(perfil_id);
                    CREATE INDEX IF NOT EXISTS idx_posts_data ON posts(data_post);
                    CREATE INDEX IF NOT EXISTS idx_comentarios_post ON comentarios(post_id);
                    CREATE INDEX IF NOT EXISTS idx_comentarios_data ON comentarios(data_comentario);
                    CREATE INDEX IF NOT EXISTS idx_comentarios_analisado ON comentarios(analisado);
                    CREATE INDEX IF NOT EXISTS idx_analises_comentario ON analises(comentario_id);
                """)

            print(f"✅ Banco de dados inicializado: {self.db_path}")
        except Exception as e:
            print(f"❌ Erro ao inicializar banco: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    # ==========================================
    # PERFIS
    # ==========================================
    
    def inserir_perfil(self, dados_perfil: Dict) -> int:
        """Insere ou atualiza perfil"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO perfis (
                    username, nome_completo, biografia, seguidores, seguindo,
                    total_posts, eh_comercial, eh_verificado
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    nome_completo = excluded.nome_completo,
                    biografia = excluded.biografia,
                    seguidores = excluded.seguidores,
                    seguindo = excluded.seguindo,
                    total_posts = excluded.total_posts,
                    eh_comercial = excluded.eh_comercial,
                    eh_verificado = excluded.eh_verificado,
                    data_ultima_atualizacao = CURRENT_TIMESTAMP
            """, (
                dados_perfil['username'],
                dados_perfil.get('nome_completo'),
                dados_perfil.get('biografia'),
                dados_perfil.get('seguidores', 0),
                dados_perfil.get('seguindo', 0),
                dados_perfil.get('total_posts', 0),
                dados_perfil.get('eh_comercial', False),
                dados_perfil.get('eh_verificado', False)
            ))
            
            # Retorna ID do perfil
            cursor.execute("SELECT id FROM perfis WHERE username = ?", 
                         (dados_perfil['username'],))
            return cursor.fetchone()[0]
    
    def buscar_perfil(self, username: str) -> Optional[Dict]:
        """Busca perfil por username"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM perfis WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ==========================================
    # POSTS
    # ==========================================
    
    def inserir_post(self, perfil_id: int, dados_post: Dict) -> int:
        """Insere ou atualiza post"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO posts (
                    perfil_id, post_id, codigo, url, tipo, caption,
                    likes, comentarios_count, visualizacoes,
                    alcance, impressoes, salvamentos, data_post
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(post_id) DO UPDATE SET
                    likes = excluded.likes,
                    comentarios_count = excluded.comentarios_count,
                    visualizacoes = excluded.visualizacoes,
                    alcance = excluded.alcance,
                    impressoes = excluded.impressoes,
                    salvamentos = excluded.salvamentos,
                    data_ultima_atualizacao = CURRENT_TIMESTAMP
            """, (
                perfil_id,
                dados_post['id'],
                dados_post['codigo'],
                dados_post['url'],
                dados_post['tipo'],
                dados_post.get('caption', ''),
                dados_post.get('likes', 0),
                dados_post.get('comentarios_count', 0),
                dados_post.get('visualizacoes', 0),
                dados_post.get('alcance'),
                dados_post.get('impressoes'),
                dados_post.get('salvamentos'),
                dados_post['data']
            ))
            
            cursor.execute("SELECT id FROM posts WHERE post_id = ?", 
                         (dados_post['id'],))
            return cursor.fetchone()[0]
    
    def buscar_posts_nao_analisados(self, perfil_id: int, limit: int = 100) -> List[Dict]:
        """Busca posts que ainda não foram completamente analisados"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM posts 
                WHERE perfil_id = ? AND analisado = 0
                ORDER BY data_post DESC
                LIMIT ?
            """, (perfil_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def marcar_post_analisado(self, post_id: int):
        """Marca post como analisado"""
        with self.get_connection() as conn:
            conn.execute("UPDATE posts SET analisado = 1 WHERE id = ?", (post_id,))
    
    # ==========================================
    # COMENTÁRIOS
    # ==========================================
    
    def inserir_comentario(self, post_id: int, dados_comentario: Dict) -> int:
        """Insere ou atualiza comentário"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO comentarios (
                    post_id, comentario_id, usuario, nome_completo,
                    texto, likes, data_comentario
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(comentario_id) DO UPDATE SET
                    likes = excluded.likes,
                    texto = excluded.texto,
                    editado = CASE 
                        WHEN comentarios.texto != excluded.texto THEN 1 
                        ELSE comentarios.editado 
                    END,
                    data_ultima_atualizacao = CURRENT_TIMESTAMP
            """, (
                post_id,
                dados_comentario['id'],
                dados_comentario['usuario'],
                dados_comentario.get('nome_completo', ''),
                dados_comentario['texto'],
                dados_comentario.get('likes', 0),
                dados_comentario['data']
            ))
            
            cursor.execute("SELECT id FROM comentarios WHERE comentario_id = ?",
                         (dados_comentario['id'],))
            return cursor.fetchone()[0]
    
    def buscar_comentarios_nao_analisados(self, perfil_id: int = None) -> List[Dict]:
        """Busca comentários que ainda não foram analisados"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if perfil_id:
                cursor.execute("""
                    SELECT c.* FROM comentarios c
                    JOIN posts p ON c.post_id = p.id
                    WHERE p.perfil_id = ? AND c.analisado = 0 AND c.deletado = 0
                    ORDER BY c.data_comentario DESC
                """, (perfil_id,))
            else:
                cursor.execute("""
                    SELECT * FROM comentarios 
                    WHERE analisado = 0 AND deletado = 0
                    ORDER BY data_comentario DESC
                """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def marcar_comentarios_deletados(self, comentarios_ids: List[str]):
        """Marca comentários como deletados (não aparecem mais no Instagram)"""
        with self.get_connection() as conn:
            placeholders = ','.join('?' * len(comentarios_ids))
            conn.execute(f"""
                UPDATE comentarios 
                SET deletado = 1, data_ultima_atualizacao = CURRENT_TIMESTAMP
                WHERE comentario_id IN ({placeholders})
            """, comentarios_ids)
    
    # ==========================================
    # ANÁLISES GPT
    # ==========================================
    
    def inserir_analise(self, comentario_id: int, analise: Dict, custo: float = 0.0):
        """Insere análise GPT de um comentário"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Converte palavras-chave para JSON
            palavras_json = json.dumps(analise.get('palavras_chave', []))
            
            cursor.execute("""
                INSERT INTO analises (
                    comentario_id, sentimento, categoria, topico,
                    urgencia, intent, palavras_chave, resumo,
                    sugestao_resposta, resposta_sugerida, custo_gpt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(comentario_id) DO UPDATE SET
                    sentimento = excluded.sentimento,
                    categoria = excluded.categoria,
                    topico = excluded.topico,
                    urgencia = excluded.urgencia,
                    intent = excluded.intent,
                    palavras_chave = excluded.palavras_chave,
                    resumo = excluded.resumo,
                    sugestao_resposta = excluded.sugestao_resposta,
                    resposta_sugerida = excluded.resposta_sugerida,
                    data_analise = CURRENT_TIMESTAMP
            """, (
                comentario_id,
                analise.get('sentimento'),
                analise.get('categoria'),
                analise.get('topico'),
                analise.get('urgencia'),
                analise.get('intent'),
                palavras_json,
                analise.get('resumo'),
                analise.get('sugestao_resposta'),
                analise.get('resposta_sugerida'),
                custo
            ))
            
            # Marca comentário como analisado
            conn.execute("""
                UPDATE comentarios SET analisado = 1 
                WHERE id = ?
            """, (comentario_id,))
    
    # ==========================================
    # EXECUÇÕES
    # ==========================================
    
    def iniciar_execucao(self, perfil_id: int, tipo: str = 'completa') -> int:
        """Registra início de execução"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO execucoes (perfil_id, tipo, status)
                VALUES (?, ?, 'em_andamento')
            """, (perfil_id, tipo))
            return cursor.lastrowid
    
    def finalizar_execucao(self, execucao_id: int, dados: Dict, planilha_url: str = None):
        """Finaliza execução com estatísticas"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE execucoes SET
                    posts_processados = ?,
                    comentarios_novos = ?,
                    comentarios_atualizados = ?,
                    analises_realizadas = ?,
                    custo_total_gpt = ?,
                    data_fim = CURRENT_TIMESTAMP,
                    duracao_segundos = ?,
                    status = 'concluida',
                    planilha_url = ?
                WHERE id = ?
            """, (
                dados.get('posts_processados', 0),
                dados.get('comentarios_novos', 0),
                dados.get('comentarios_atualizados', 0),
                dados.get('analises_realizadas', 0),
                dados.get('custo_total_gpt', 0.0),
                dados.get('duracao_segundos', 0),
                planilha_url,
                execucao_id
            ))
    
    def registrar_erro_execucao(self, execucao_id: int, erro: str):
        """Registra erro em execução"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE execucoes SET
                    status = 'erro',
                    mensagem_erro = ?,
                    data_fim = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (erro, execucao_id))
    
    # ==========================================
    # ALERTAS
    # ==========================================
    
    def inserir_alerta(self, execucao_id: int, comentario_id: int, 
                      tipo: str, descricao: str, severidade: int = 1):
        """Registra alerta"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO alertas (
                    execucao_id, comentario_id, tipo, descricao, severidade
                ) VALUES (?, ?, ?, ?, ?)
            """, (execucao_id, comentario_id, tipo, descricao, severidade))
    
    def buscar_alertas_pendentes(self, perfil_id: int = None) -> List[Dict]:
        """Busca alertas não resolvidos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if perfil_id:
                cursor.execute("""
                    SELECT * FROM v_alertas_pendentes
                    WHERE perfil = (SELECT username FROM perfis WHERE id = ?)
                """, (perfil_id,))
            else:
                cursor.execute("SELECT * FROM v_alertas_pendentes")
            
            return [dict(row) for row in cursor.fetchall()]
    
    # ==========================================
    # QUERIES DE RELATÓRIOS
    # ==========================================
    
    def get_resumo_perfil(self, perfil_id: int) -> Dict:
        """Retorna resumo completo de um perfil"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM v_resumo_perfil WHERE id = ?
            """, (perfil_id,))
            row = cursor.fetchone()
            return dict(row) if row else {}

    def get_comentarios_completos(self, perfil_id: int,
                                  limit: int = 1000) -> List[Dict]:
        """Retorna comentários com análises"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    c.id,
                    c.comentario_id,
                    p.username as perfil,
                    po.codigo as post_codigo,
                    po.url as post_url,
                    c.usuario,
                    c.nome_completo,
                    c.texto,
                    c.likes,
                    c.data_comentario,
                    c.deletado,
                    a.sentimento,
                    a.categoria,
                    a.topico,
                    a.urgencia,
                    a.intent,
                    a.palavras_chave,
                    a.resumo,
                    a.resposta_sugerida
                FROM comentarios c
                LEFT JOIN analises a ON c.id = a.comentario_id
                JOIN posts po ON c.post_id = po.id
                JOIN perfis p ON po.perfil_id = p.id
                WHERE c.deletado = 0 AND p.id = ?
                ORDER BY c.data_comentario DESC
                LIMIT ?
            """, (perfil_id, limit))

            results = []
            for row in cursor.fetchall():
                item = dict(row)
                # Parse JSON das palavras-chave
                if item.get('palavras_chave'):
                    try:
                        item['palavras_chave'] = json.loads(item['palavras_chave'])
                    except:
                        item['palavras_chave'] = []
                results.append(item)

            return results
    
    def get_posts_top(self, perfil_id: int, limit: int = 10) -> List[Dict]:
        """Retorna posts mais engajados"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM v_posts_top
                WHERE username = (SELECT username FROM perfis WHERE id = ?)
                LIMIT ?
            """, (perfil_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_evolucao_temporal(self, perfil_id: int, 
                             dias: int = 30) -> List[Dict]:
        """Retorna evolução de sentimentos ao longo do tempo"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            data_inicio = (datetime.now() - timedelta(days=dias)).date()
            
            cursor.execute("""
                SELECT 
                    DATE(c.data_comentario) as data,
                    COUNT(*) as total,
                    SUM(CASE WHEN a.sentimento = 'positivo' THEN 1 ELSE 0 END) as positivos,
                    SUM(CASE WHEN a.sentimento = 'neutro' THEN 1 ELSE 0 END) as neutros,
                    SUM(CASE WHEN a.sentimento = 'negativo' THEN 1 ELSE 0 END) as negativos,
                    AVG(c.likes) as media_likes
                FROM comentarios c
                JOIN posts p ON c.post_id = p.id
                LEFT JOIN analises a ON c.id = a.comentario_id
                WHERE p.perfil_id = ? AND DATE(c.data_comentario) >= ?
                GROUP BY DATE(c.data_comentario)
                ORDER BY data
            """, (perfil_id, data_inicio))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_top_usuarios(self, perfil_id: int, limit: int = 10) -> List[Dict]:
        """Retorna usuários mais ativos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    c.usuario,
                    c.nome_completo,
                    COUNT(*) as total_comentarios,
                    AVG(c.likes) as media_likes,
                    MAX(c.data_comentario) as ultimo_comentario,
                    GROUP_CONCAT(DISTINCT a.sentimento) as sentimentos
                FROM comentarios c
                JOIN posts p ON c.post_id = p.id
                LEFT JOIN analises a ON c.id = a.comentario_id
                WHERE p.perfil_id = ? AND c.deletado = 0
                GROUP BY c.usuario
                ORDER BY total_comentarios DESC
                LIMIT ?
            """, (perfil_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_estatisticas_gerais(self, perfil_id: int) -> Dict:
        """Retorna estatísticas gerais do perfil"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total de dados
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT p.id) as total_posts,
                    COUNT(DISTINCT c.id) as total_comentarios,
                    COUNT(DISTINCT c.usuario) as total_usuarios_unicos,
                    SUM(p.likes) as total_likes_posts,
                    SUM(c.likes) as total_likes_comentarios
                FROM posts p
                LEFT JOIN comentarios c ON p.id = c.post_id
                WHERE p.perfil_id = ?
            """, (perfil_id,))
            stats = dict(cursor.fetchone())
            
            # Sentimentos
            cursor.execute("""
                SELECT 
                    sentimento,
                    COUNT(*) as count
                FROM analises a
                JOIN comentarios c ON a.comentario_id = c.id
                JOIN posts p ON c.post_id = p.id
                WHERE p.perfil_id = ?
                GROUP BY sentimento
            """, (perfil_id,))
            
            sentimentos = {row['sentimento']: row['count'] for row in cursor.fetchall()}
            stats['sentimentos'] = sentimentos
            
            return stats
