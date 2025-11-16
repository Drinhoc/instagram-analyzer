-- ===========================================
-- SCHEMA DO BANCO DE DADOS
-- Analisador de Instagram com SQLite
-- ===========================================

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
    post_id TEXT UNIQUE NOT NULL,  -- ID do Instagram
    codigo TEXT NOT NULL,  -- Código curto do post
    url TEXT NOT NULL,
    tipo TEXT,  -- Foto/Video/Carrossel
    caption TEXT,
    likes INTEGER DEFAULT 0,
    comentarios_count INTEGER DEFAULT 0,
    visualizacoes INTEGER DEFAULT 0,
    alcance INTEGER,  -- Só conta verificada
    impressoes INTEGER,  -- Só conta verificada
    salvamentos INTEGER,  -- Só conta verificada
    data_post TIMESTAMP NOT NULL,
    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analisado BOOLEAN DEFAULT 0,
    FOREIGN KEY (perfil_id) REFERENCES perfis(id)
);

-- Comentários brutos
CREATE TABLE IF NOT EXISTS comentarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    comentario_id TEXT UNIQUE NOT NULL,  -- ID do Instagram
    usuario TEXT NOT NULL,
    nome_completo TEXT,
    texto TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    data_comentario TIMESTAMP NOT NULL,
    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    editado BOOLEAN DEFAULT 0,
    deletado BOOLEAN DEFAULT 0,
    analisado BOOLEAN DEFAULT 0,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

-- Análises GPT dos comentários
CREATE TABLE IF NOT EXISTS analises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comentario_id INTEGER NOT NULL UNIQUE,
    sentimento TEXT NOT NULL,  -- positivo/neutro/negativo
    categoria TEXT NOT NULL,  -- elogio/reclamacao/duvida/sugestao/spam/outro
    topico TEXT,
    urgencia TEXT,  -- sim/nao
    intent TEXT,  -- compra/informacao/feedback/reclamacao/outro
    palavras_chave TEXT,  -- JSON array
    resumo TEXT,
    sugestao_resposta TEXT,  -- sim/nao
    resposta_sugerida TEXT,
    confianca REAL DEFAULT 1.0,  -- Confiança da análise (0-1)
    data_analise TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    custo_gpt REAL DEFAULT 0.0,
    modelo_gpt TEXT DEFAULT 'gpt-4o-mini',
    FOREIGN KEY (comentario_id) REFERENCES comentarios(id)
);

-- Histórico de execuções
CREATE TABLE IF NOT EXISTS execucoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    perfil_id INTEGER NOT NULL,
    tipo TEXT DEFAULT 'completa',  -- completa/incremental
    posts_processados INTEGER DEFAULT 0,
    comentarios_novos INTEGER DEFAULT 0,
    comentarios_atualizados INTEGER DEFAULT 0,
    analises_realizadas INTEGER DEFAULT 0,
    custo_total_gpt REAL DEFAULT 0.0,
    data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fim TIMESTAMP,
    duracao_segundos INTEGER,
    status TEXT DEFAULT 'em_andamento',  -- em_andamento/concluida/erro
    mensagem_erro TEXT,
    planilha_url TEXT,  -- URL do Google Sheets gerado
    FOREIGN KEY (perfil_id) REFERENCES perfis(id)
);

-- Alertas gerados
CREATE TABLE IF NOT EXISTS alertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execucao_id INTEGER NOT NULL,
    comentario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,  -- negativo_visivel/urgencia/reclamacao
    descricao TEXT,
    severidade INTEGER DEFAULT 1,  -- 1-5
    resolvido BOOLEAN DEFAULT 0,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_resolucao TIMESTAMP,
    FOREIGN KEY (execucao_id) REFERENCES execucoes(id),
    FOREIGN KEY (comentario_id) REFERENCES comentarios(id)
);

-- Métricas agregadas por perfil (cache de estatísticas)
CREATE TABLE IF NOT EXISTS metricas_perfil (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    perfil_id INTEGER NOT NULL,
    data_referencia DATE NOT NULL,
    total_posts INTEGER DEFAULT 0,
    total_comentarios INTEGER DEFAULT 0,
    total_likes_posts INTEGER DEFAULT 0,
    total_likes_comentarios INTEGER DEFAULT 0,
    sentimento_positivo_perc REAL DEFAULT 0,
    sentimento_neutro_perc REAL DEFAULT 0,
    sentimento_negativo_perc REAL DEFAULT 0,
    total_urgencias INTEGER DEFAULT 0,
    total_intencao_compra INTEGER DEFAULT 0,
    total_reclamacoes INTEGER DEFAULT 0,
    engagement_rate REAL DEFAULT 0,
    data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(perfil_id, data_referencia),
    FOREIGN KEY (perfil_id) REFERENCES perfis(id)
);

-- Usuários mais ativos (top comentadores)
CREATE TABLE IF NOT EXISTS usuarios_ativos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    perfil_id INTEGER NOT NULL,
    usuario TEXT NOT NULL,
    nome_completo TEXT,
    total_comentarios INTEGER DEFAULT 0,
    sentimento_predominante TEXT,
    ultima_interacao TIMESTAMP,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(perfil_id, usuario),
    FOREIGN KEY (perfil_id) REFERENCES perfis(id)
);

-- ===========================================
-- ÍNDICES PARA PERFORMANCE
-- ===========================================

CREATE INDEX IF NOT EXISTS idx_posts_perfil ON posts(perfil_id);
CREATE INDEX IF NOT EXISTS idx_posts_data ON posts(data_post);
CREATE INDEX IF NOT EXISTS idx_posts_analisado ON posts(analisado);

CREATE INDEX IF NOT EXISTS idx_comentarios_post ON comentarios(post_id);
CREATE INDEX IF NOT EXISTS idx_comentarios_usuario ON comentarios(usuario);
CREATE INDEX IF NOT EXISTS idx_comentarios_data ON comentarios(data_comentario);
CREATE INDEX IF NOT EXISTS idx_comentarios_analisado ON comentarios(analisado);
CREATE INDEX IF NOT EXISTS idx_comentarios_deletado ON comentarios(deletado);

CREATE INDEX IF NOT EXISTS idx_analises_sentimento ON analises(sentimento);
CREATE INDEX IF NOT EXISTS idx_analises_categoria ON analises(categoria);
CREATE INDEX IF NOT EXISTS idx_analises_urgencia ON analises(urgencia);
CREATE INDEX IF NOT EXISTS idx_analises_intent ON analises(intent);

CREATE INDEX IF NOT EXISTS idx_execucoes_perfil ON execucoes(perfil_id);
CREATE INDEX IF NOT EXISTS idx_execucoes_data ON execucoes(data_inicio);
CREATE INDEX IF NOT EXISTS idx_execucoes_status ON execucoes(status);

CREATE INDEX IF NOT EXISTS idx_alertas_execucao ON alertas(execucao_id);
CREATE INDEX IF NOT EXISTS idx_alertas_resolvido ON alertas(resolvido);

CREATE INDEX IF NOT EXISTS idx_metricas_perfil ON metricas_perfil(perfil_id);
CREATE INDEX IF NOT EXISTS idx_metricas_data ON metricas_perfil(data_referencia);

-- ===========================================
-- VIEWS ÚTEIS
-- ===========================================

-- View: Comentários com análise completa
CREATE VIEW IF NOT EXISTS v_comentarios_completos AS
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
WHERE c.deletado = 0;

-- View: Resumo por perfil
CREATE VIEW IF NOT EXISTS v_resumo_perfil AS
SELECT 
    p.id,
    p.username,
    p.nome_completo,
    p.seguidores,
    COUNT(DISTINCT po.id) as total_posts,
    COUNT(DISTINCT c.id) as total_comentarios,
    SUM(po.likes) as total_likes,
    AVG(CASE WHEN a.sentimento = 'positivo' THEN 1.0 ELSE 0.0 END) * 100 as perc_positivo,
    AVG(CASE WHEN a.sentimento = 'negativo' THEN 1.0 ELSE 0.0 END) * 100 as perc_negativo,
    SUM(CASE WHEN a.urgencia = 'sim' THEN 1 ELSE 0 END) as total_urgencias,
    MAX(po.data_coleta) as ultima_coleta
FROM perfis p
LEFT JOIN posts po ON p.id = po.perfil_id
LEFT JOIN comentarios c ON po.id = c.post_id
LEFT JOIN analises a ON c.id = a.comentario_id
WHERE p.ativo = 1
GROUP BY p.id;

-- View: Posts mais engajados
CREATE VIEW IF NOT EXISTS v_posts_top AS
SELECT 
    p.username,
    po.codigo,
    po.url,
    po.tipo,
    po.likes,
    po.comentarios_count,
    (po.likes + po.comentarios_count * 10) as score_engajamento,
    po.data_post
FROM posts po
JOIN perfis p ON po.perfil_id = p.id
ORDER BY score_engajamento DESC;

-- View: Alertas pendentes
CREATE VIEW IF NOT EXISTS v_alertas_pendentes AS
SELECT 
    a.id,
    a.tipo,
    a.descricao,
    a.severidade,
    c.texto as comentario,
    c.usuario,
    po.url as post_url,
    p.username as perfil,
    a.data_criacao
FROM alertas a
JOIN comentarios c ON a.comentario_id = c.id
JOIN posts po ON c.post_id = po.id
JOIN perfis p ON po.perfil_id = p.id
WHERE a.resolvido = 0
ORDER BY a.severidade DESC, a.data_criacao DESC;
