import sqlite3
import hashlib
from datetime import datetime

class FAMTDatabaseManager:
    """
    FAMT Control - Classe Gerenciadora do Banco de Dados SQLite.
    Desenvolvida por: Thamirys Matos da Silva (Database Engineer - Squad FAMT)
    
    Esta classe encapsula todas as operações de banco de dados do projeto,
    garantindo a integridade referencial, criptografia de senhas (LGPD) e 
    as regras de negócio contábeis (valores de despesas negativos, receitas positivos).
    """

    def __init__(self, db_path="famt_control.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        """Retorna uma conexão ativa com o SQLite com chaves estrangeiras ativadas."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome (ex: row['email'])
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        """Inicializa o banco de dados criando as tabelas se não existirem."""
        with self._get_connection() as conn:
            # Tabela de Usuários (LGPD: guarda hash de senha, nunca senha aberta)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    senha_hash TEXT NOT NULL
                );
            """)
            
            # Tabela de Transações (REQ-DAT-01)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Transacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    valor REAL NOT NULL,
                    data TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id) ON DELETE CASCADE
                );
            """)
            
            # Índices de performance para busca temporal e por ID de usuário (WP 1.3.2)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_data ON Transacoes(data);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_usuario_id ON Transacoes(usuario_id);")
            conn.commit()

    def _hash_senha(self, senha: str) -> str:
        """Gera um hash SHA-256 irreversível para a senha, atendendo à LGPD (REQ-EXT-01)."""
        return hashlib.sha256(senha.encode('utf-8')).hexdigest()

    # --- OPERAÇÕES DE USUÁRIO ---

    def cadastrar_usuario(self, email: str, senha_limpa: str) -> int:
        """
        Cadastra um novo usuário no banco com senha criptografada.
        Retorna o ID do usuário cadastrado.
        """
        senha_hash = self._hash_senha(senha_limpa)
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Usuarios (email, senha_hash) VALUES (?, ?);",
                    (email.strip().lower(), senha_hash)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"O email '{email}' já está cadastrado no sistema.")

    def autenticar_usuario(self, email: str, senha_limpa: str) -> dict:
        """
        Autentica o usuário comparando o hash da senha enviada com o do banco.
        Retorna um dicionário com os dados básicos do usuário se autenticado, ou None.
        """
        senha_hash = self._hash_senha(senha_limpa)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, email FROM Usuarios WHERE email = ? AND senha_hash = ?;",
                (email.strip().lower(), senha_hash)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    # --- OPERAÇÕES DE TRANSAÇÕES ---

    def registrar_transacao(self, usuario_id: int, valor: float, descricao: str, categoria: str, data: str = None) -> int:
        """
        Registra uma transação validando o sinal de entrada conforme o requisito RF-SYS-02.
        - Receitas: devem ser salvas como números estritamente positivos (+).
        - Despesas: devem ser salvas como números estritamente negativos (-).
        """
        if valor == 0:
            raise ValueError("O valor de uma transação não pode ser zero.")

        # Validação RF-SYS-02 (Garantir persistência negativa de despesas e positiva de receitas)
        categoria_lower = categoria.strip().lower()
        despesa_categorias = ["alimentação", "alimentacao", "transporte", "lazer", "saúde", "saude", "educação", "educacao", "despesa", "gastos"]
        
        is_despesa = any(cat in categoria_lower for cat in despesa_categorias) or valor < 0

        if is_despesa:
            # Força o valor a ser negativo no banco
            valor = -abs(valor)
        else:
            # Força o valor a ser positivo no banco
            valor = abs(valor)

        # Se não informar a data, utiliza a data e hora atual (padrão ISO-8601)
        if not data:
            data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Transacoes (usuario_id, valor, data, descricao, categoria) VALUES (?, ?, ?, ?, ?);",
                    (usuario_id, valor, data, descricao.strip(), categoria.strip())
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError as e:
                raise ValueError("Erro de integridade referencial: ID de usuário inexistente.") from e

    # --- CÁLCULOS E RELATÓRIOS ---

    def calcular_saldo_consolidado(self, usuario_id: int) -> dict:
        """
        Calcula o saldo utilizando a equação matemática contábil elementar (REQ-DOM-01):
        Saldo Líquido = Somatório de Receitas - Somatório de Despesas.
        
        Retorna um dicionário contendo:
        - total_receitas (soma dos valores positivos)
        - total_despesas (soma absoluta dos valores negativos)
        - saldo_liquido (balanço final)
        - status (🟢 Conta Saudável ou 🔴 Atenção: Saldo Devedor!)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Busca todas as transações do usuário
            cursor.execute("SELECT valor FROM Transacoes WHERE usuario_id = ?;", (usuario_id,))
            transacoes = cursor.fetchall()
            
            total_receitas = 0.0
            total_despesas = 0.0
            
            for row in transacoes:
                v = row['valor']
                if v > 0:
                    total_receitas += v
                else:
                    total_despesas += abs(v)  # Guardamos o total gasto de forma absoluta para o relatório
                    
            saldo_liquido = total_receitas - total_despesas
            
            # Regra de Alerta REQ-BUS-01 / REQ-BUS-02
            status = "🟢 CONTA SAUDÁVEL" if saldo_liquido >= 0 else "🔴 ATENÇÃO: SALDO DEVEDOR!"
            
            return {
                "total_receitas": total_receitas,
                "total_despesas": total_despesas,
                "saldo_liquido": saldo_liquido,
                "status": status
            }

    def obter_resumo_por_categoria(self, usuario_id: int) -> list:
        """
        Retorna o agrupamento de despesas por categoria, ordenado do maior gasto para o menor.
        Útil para alimentar o dashboard e os relatórios visuais (RU06).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT categoria, SUM(ABS(valor)) as total
                FROM Transacoes
                WHERE usuario_id = ? AND valor < 0
                GROUP BY categoria
                ORDER BY total DESC;
            """, (usuario_id,))
            return [dict(row) for row in cursor.fetchall()]

    def listar_transacoes(self, usuario_id: int) -> list:
        """Retorna a lista completa de transações de um usuário ordenadas pela data mais recente."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, valor, data, descricao, categoria 
                FROM Transacoes 
                WHERE usuario_id = ? 
                ORDER BY data DESC;
            """, (usuario_id,))
            return [dict(row) for row in cursor.fetchall()]
