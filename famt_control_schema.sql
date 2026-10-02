-- =============================================================================
-- SQUAD FAMT - FAMT CONTROL - SCHEMAS OFICIAIS DO BANCO DE DADOS (SQLITE)
-- Atividade Prática 6: Dicionário da EAP (WP 1.3.2)
-- Engenheira de Banco de Dados: Thamirys Matos da Silva
-- =============================================================================

-- 1. CONFIGURAÇÕES DE AMBIENTE SQLITE
-- Garante que o motor do SQLite aplique as chaves estrangeiras para integridade referencial.
PRAGMA foreign_keys = ON;

-- 2. TABELA: USUARIOS
-- Armazena credenciais dos usuários locais do sistema.
-- Em total conformidade com a LGPD (REQ-EXT-01) quanto ao armazenamento seguro de senhas.
CREATE TABLE IF NOT EXISTS Usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL -- Armazenará criptografia irreversível (ex: hash Bcrypt/SHA-256)
);

-- 3. TABELA: TRANSACOES
-- Armazena lançamentos financeiros de receitas (+) e despesas (-) (REQ-SYS-02).
-- Relação de Integridade Referencial de um para muitos (Um usuário possui N transações).
-- Exclusão automática em cascata (ON DELETE CASCADE) para manter integridade lógica de dados.
CREATE TABLE IF NOT EXISTS Transacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    valor REAL NOT NULL, -- Valor numérico decimal positivo (receita) ou negativo (despesa)
    data TEXT NOT NULL,  -- Timestamp armazenado em formato textual ISO-8601 (YYYY-MM-DD HH:MM:SS)
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL, -- Alimentação, Transporte, Lazer, Educação, Saúde, Outros (EAP 1.3.0)
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id) ON DELETE CASCADE
);

-- 4. ÍNDICES DE PERFORMANCE (Critério de Qualidade do WP 1.3.2)
-- Criação de estrutura de árvore B para otimização de busca de lançamentos por período ou data.
-- Garante que os relatórios e dashboard carreguem em menos de 2 segundos (REQ-PROD-01).
CREATE INDEX IF NOT EXISTS idx_transacoes_data ON Transacoes(data);
CREATE INDEX IF NOT EXISTS idx_transacoes_usuario_id ON Transacoes(usuario_id);
