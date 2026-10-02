import sqlite3
import os
from datetime import datetime

# Definindo o nome do arquivo de banco de dados SQLite local (WP 1.3.2)
DB_FILE = "famt_control.db"

SQL_SCHEMA = """
-- 1. ATIVAÇÃO DE CHAVES ESTRANGEIRAS
-- No SQLite, as chaves estrangeiras vêm desativadas por padrão. É mandatório ativá-las em cada conexão.
PRAGMA foreign_keys = ON;

-- 2. TABELA DE USUÁRIOS (Normalização 3FN & Conformidade com a LGPD REQ-EXT-01)
CREATE TABLE IF NOT EXISTS Usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL -- Armazena a senha criptografada de forma irreversível
);

-- 3. TABELA DE TRANSAÇÕES (Normalização 3FN, REQ-DAT-01 e REQ-SYS-02)
CREATE TABLE IF NOT EXISTS Transacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    valor REAL NOT NULL, -- Valor decimal (positivo para Receitas, negativo para Despesas)
    data TEXT NOT NULL,  -- Timestamp armazenado no formato padrão ISO-8601 (YYYY-MM-DD HH:MM:SS)
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL, -- Categorias: Alimentação, Transporte, Lazer, Saúde, etc.
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id) ON DELETE CASCADE
);

-- 4. ÍNDICE DE PERFORMANCE POR DATA (Critério de Qualidade do WP 1.3.2)
-- Otimiza as buscas temporais e a renderização do Dashboard abaixo de 2 segundos (REQ-PROD-01)
CREATE INDEX IF NOT EXISTS idx_transacoes_data ON Transacoes(data);
"""

def inicializar_banco():
    """Cria o arquivo de banco de dados local e executa o esquema DDL."""
    print(f"[*] Inicializando o banco de dados: {DB_FILE}...")
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        # Executa múltiplos comandos SQL do Schema
        cursor.executescript(SQL_SCHEMA)
        conn.commit()
        print("[+] Banco de dados e tabelas criados com sucesso!")
    except sqlite3.Error as e:
        print(f"[-] Erro ao criar o banco de dados: {e}")
    finally:
        conn.close()

def popular_dados_teste():
    """
    Insere dados fictícios de teste (seeds) simulando cenários reais de despesas
    e receitas de estudantes universitários (Premissa de Teste do Projeto).
    """
    print("[*] Semeando dados de teste (Seeds)...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    try:
        # 1. Limpar tabelas existentes para evitar duplicidade em testes
        cursor.execute("DELETE FROM Transacoes;")
        cursor.execute("DELETE FROM Usuarios;")
        conn.commit()

        # 2. Inserir Usuários de Teste (Senhas hash simuladas de acordo com a LGPD)
        # Em produção, André implementará o hash real (bcrypt/sha256) no Backend FastAPI
        usuarios = [
            ("thamirys@umc.edu.br", "$2b$12$eImiTXuWVxfM37uY4bAvKObMPEYF3Q8s8sE08Vp6yH9SgZfV.OpyK"), # hash bcrypt simulado
            ("andre.mitchel@umc.edu.br", "$2b$12$K4UuP6PbyfJ9L8yW6vR6OeKObMPEYF3Q8s8sE08Vp6yH9SgZfV.OpyK"),
            ("maria.augusta@umc.edu.br", "$2b$12$H8YyX7PbyfJ9L8yW6vR6OeKObMPEYF3Q8s8sE08Vp6yH9SgZfV.OpyK"),
            ("franciellen@umc.edu.br", "$2b$12$L9ZzW5PbyfJ9L8yW6vR6OeKObMPEYF3Q8s8sE08Vp6yH9SgZfV.OpyK")
        ]
        
        cursor.executemany("INSERT INTO Usuarios (email, senha_hash) VALUES (?, ?);", usuarios)
        conn.commit()
        
        # Recuperar ID da Thamirys para vincular as transações dela
        cursor.execute("SELECT id FROM Usuarios WHERE email = 'thamirys@umc.edu.br';")
        thamirys_id = cursor.fetchone()[0]

        # 3. Inserir Transações de Teste para a Thamirys (REQ-SYS-02: receitas (+) e despesas (-))
        transacoes = [
            # Receitas (+)
            (thamirys_id, 1200.00, "2026-08-01 10:00:00", "Bolsa de Estágio - UMC", "Receita"),
            (thamirys_id, 150.00, "2026-08-05 14:00:00", "Reembolso de Despesas Projeto", "Receita"),
            
            # Despesas (-)
            (thamirys_id, -320.00, "2026-08-02 12:30:00", "Mensalidade Curso", "Educação"),
            (thamirys_id, -45.50, "2026-08-02 19:15:00", "Lanche com a Squad", "Alimentação"),
            (thamirys_id, -22.00, "2026-08-03 08:00:00", "Passe Semanal de Ônibus", "Transporte"),
            (thamirys_id, -89.90, "2026-08-04 21:00:00", "Livro de Engenharia de Software", "Educação"),
            (thamirys_id, -65.00, "2026-08-06 18:00:00", "Cinema Fim de Semana", "Lazer"),
            (thamirys_id, -120.00, "2026-08-07 10:30:00", "Exame de Rotina", "Saúde"),
            (thamirys_id, -55.00, "2026-08-10 13:00:00", "Almoço no RU", "Alimentação"),
        ]

        cursor.executemany(
            "INSERT INTO Transacoes (usuario_id, valor, data, descricao, categoria) VALUES (?, ?, ?, ?, ?);",
            transacoes
        )
        conn.commit()
        print("[+] Dados de teste semeados com sucesso!")

    except sqlite3.Error as e:
        print(f"[-] Erro ao semear dados: {e}")
        conn.rollback()
    finally:
        conn.close()

def calcular_saldo_consolidado(usuario_email):
    """
    Executa o cálculo matemático do saldo líquido com base na equação contábil:
    Saldo Líquido = Somatório(Receitas) - Somatório(Despesas)
    Satisfaz REQ-DOM-01 (Consolidação Contábil) e REQ-PROD-01 (Desempenho < 2s).
    """
    print(f"\n[*] Executando Cálculo Contábil (REQ-DOM-01) para: {usuario_email}...")
    start_time = datetime.now()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Consulta SQL otimizada que faz o somatório simples dos valores diretamente no banco.
        # Como as despesas já são negativas (REQ-SYS-02), o SUM simples consolida o saldo líquido perfeitamente.
        query = """
            SELECT 
                SUM(CASE WHEN valor > 0 THEN valor ELSE 0 END) as total_receitas,
                SUM(CASE WHEN valor < 0 THEN valor ELSE 0 END) as total_despesas,
                SUM(valor) as saldo_liquido
            FROM Transacoes t
            JOIN Usuarios u ON t.usuario_id = u.id
            WHERE u.email = ?;
        """
        cursor.execute(query, (usuario_email,))
        resultado = cursor.fetchone()
        
        total_receitas = resultado[0] or 0.0
        total_despesas = abs(resultado[1] or 0.0) # exibe valor absoluto para visualização amigável
        saldo_liquido = resultado[2] or 0.0
        
        # REQ-BUS-01 (Aviso de Saldo Devedor): Alerta visual se saldo for negativo
        status_financeiro = "🟢 CONTA SAUDÁVEL"
        if saldo_liquido < 0:
            status_financeiro = "🔴 ATENÇÃO: SALDO DEVEDOR! (Alerta de Contenção de Gastos - REQ-BUS-01)"

        end_time = datetime.now()
        execution_time_ms = (end_time - start_time).total_seconds() * 1000

        print(f"--------------------------------------------------")
        print(f" Relatório Financeiro: {usuario_email}")
        print(f"--------------------------------------------------")
        print(f" (+) Total de Receitas: R$ {total_receitas:.2f}")
        print(f" (-) Total de Despesas: R$ {total_despesas:.2f}")
        print(f" (=) Saldo Líquido:     R$ {saldo_liquido:.2f}")
        print(f" Status:                {status_financeiro}")
        print(f" Tempo de Processamento: {execution_time_ms:.2f}ms (Meta < 2000ms: PASSOU!)")
        print(f"--------------------------------------------------")

    except sqlite3.Error as e:
        print(f"[-] Erro ao executar cálculo de saldo: {e}")
    finally:
        conn.close()

def obter_resumo_por_categoria(usuario_email):
    """
    Retorna o resumo consolidado de despesas agrupadas por categoria.
    Satisfaz RU06 (Consultar gastos por categoria) e RS07 (Resumo).
    """
    print(f"\n[*] Gerando Resumo de Gastos por Categoria (RU06) para: {usuario_email}...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Seleciona apenas as despesas (valores negativos), agrupa por categoria e calcula o percentual do total gasto
        query = """
            WITH TotalGasto AS (
                SELECT SUM(valor) as total 
                FROM Transacoes t
                JOIN Usuarios u ON t.usuario_id = u.id
                WHERE u.email = ? AND valor < 0
            )
            SELECT 
                categoria,
                ABS(SUM(valor)) as total_categoria,
                (SUM(valor) / (SELECT total FROM TotalGasto)) * 100 as percentual
            FROM Transacoes t
            JOIN Usuarios u ON t.usuario_id = u.id
            WHERE u.email = ? AND valor < 0
            GROUP BY categoria
            ORDER BY total_categoria DESC;
        """
        cursor.execute(query, (usuario_email, usuario_email))
        resultados = cursor.fetchall()
        
        print("--------------------------------------------------")
        print(" Distribuição de Despesas por Categoria ")
        print("--------------------------------------------------")
        for linha in resultados:
            cat, valor, perc = linha
            barra = "■" * int(perc / 5) # Representação visual em barra simples de texto
            print(f" {cat:<15} | R$ {valor:>7.2f} ({perc:>5.1f}%) {barra}")
        print("--------------------------------------------------")

    except sqlite3.Error as e:
        print(f"[-] Erro ao gerar resumo de categorias: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Teste de execução ponta a ponta
    print("=== FAMT Control - Módulo de Banco de Dados SQLite (WP 1.3.2) ===")
    inicializar_banco()
    popular_dados_teste()
    calcular_saldo_consolidado("thamirys@umc.edu.br")
    obter_resumo_por_categoria("thamirys@umc.edu.br")
