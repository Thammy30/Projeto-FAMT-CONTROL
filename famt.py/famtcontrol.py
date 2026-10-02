import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "famt_control.db"

def _hash_senha(senha: str) -> str:
    """Gera um hash SHA-256 para a senha (atende à LGPD / REQ-EXT-01)."""
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def inicializar_banco():
    """Cria a estrutura oficial do banco de dados na Versão 2 se não existir."""
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Tabela de Usuários (LGPD: guarda hash de senha, nunca senha aberta)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        primeiro_acesso INTEGER DEFAULT 1 CHECK (primeiro_acesso IN (0, 1))
    );
    """)
    
    # Tabela de Transações V2 (Com coluna 'tipo' explícita e travas físicas)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        valor REAL NOT NULL CHECK (valor > 0), -- Apenas valores absolutos positivos
        tipo TEXT NOT NULL CHECK (tipo IN ('Receita', 'Despesa')), -- Natureza contábil explícita
        data TEXT NOT NULL,  -- Timestamp ISO-8601 (YYYY-MM-DD HH:MM:SS)
        descricao TEXT NOT NULL,
        categoria TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES Usuarios(id) ON DELETE CASCADE
    );
    """)
    
    # Índices de performance para busca temporal e por ID de usuário (WP 1.3.2)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_data ON Transacoes(data);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_usuario_id ON Transacoes(usuario_id);")
    
    conexao.commit()
    conexao.close()

def cadastrar_usuario():
    """Permite cadastrar um e-mail novo no banco de dados com senha hash segura."""
    print("\n" + "-"*45)
    print("        CADASTRO DE NOVO USUÁRIO             ")
    print("-"*45)
    
    email = input("Digite o e-mail que deseja cadastrar: ").strip().lower()
    
    if not email or "@" not in email:
        print("❌ Erro: Digite um e-mail válido (exemplo@email.com).")
        return

    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    
    # Criptografa a senha padrão 'famt123' usando SHA-256 (REQ-EXT-01)
    senha_hash_padrao = _hash_senha("famt123")
    
    try:
        cursor.execute("""
            INSERT INTO Usuarios (email, senha_hash, primeiro_acesso) 
            VALUES (?, ?, 1)
        """, (email, senha_hash_padrao))
        conexao.commit()
        print(f"\n✅ Usuário '{email}' cadastrado com sucesso!")
        print("🔑 A senha provisória para o primeiro acesso é: famt123")
    except sqlite3.IntegrityError:
        print("\n❌ Erro: Este e-mail já está cadastrado no sistema!")
    finally:
        conexao.close()

def realizar_login():
    """Gerencia o login, valida hashes e força a redefinição se for o primeiro acesso."""
    print("\n" + "-"*45)
    print("        LOGIN DO SISTEMA                     ")
    print("-"*45)
    
    email = input("Digite seu e-mail: ").strip().lower()
    senha = input("Digite sua senha: ").strip()
    
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    
    cursor.execute("SELECT id, senha_hash, primeiro_acesso FROM Usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    
    if not usuario:
        print("\n❌ Erro: E-mail não encontrado no banco de dados.")
        conexao.close()
        return None
        
    usuario_id, hash_banco, primeiro_acesso = usuario
    
    # Compara o hash da senha digitada com o hash salvo no banco (REQ-EXT-01)
    if _hash_senha(senha) != hash_banco:
        print("\n❌ Erro: Senha incorreta.")
        conexao.close()
        return None
        
    # FLUXO DO PRIMEIRO ACESSO
    if primeiro_acesso == 1:
        print("\n⚠️  [PRIMEIRO ACESSO DETECTADO]")
        print("Por segurança, você DEVE redefinir sua senha provisória agora.")
        
        while True:
            nova_senha = input("Digite sua NOVA senha: ").strip()
            confirma_senha = input("Confirme sua NOVA senha: ").strip()
            
            if nova_senha == "famt123":
                print("❌ Erro: A nova senha não pode ser a senha provisória.")
            elif nova_senha != confirma_senha:
                print("❌ Erro: As senhas não coincidem.")
            elif len(nova_senha) < 4:
                print("❌ Erro: A senha deve ter pelo menos 4 caracteres.")
            else:
                # Salva a nova senha criptografada (hash SHA-256)
                novo_hash = _hash_senha(nova_senha)
                cursor.execute("""
                    UPDATE Usuarios 
                    SET senha_hash = ?, primeiro_acesso = 0 
                    WHERE id = ?
                """, (novo_hash, usuario_id))
                conexao.commit()
                print("\n✅ Senha definitiva salva com sucesso!")
                break
                
    print(f"\n🔓 Login efetuado com sucesso! Bem-vindo(a) ao FAMT Control.")
    conexao.close()
    return usuario_id

# --- ADICIONADO: FUNÇÕES DE LANÇAMENTO E CONTROLE FINANCEIRO ---

def registrar_lancamento(usuario_id):
    """Registra uma receita ou despesa no banco de dados usando valores absolutos."""
    print("\n" + "-"*45)
    print("        REGISTRAR NOVO LANÇAMENTO            ")
    print("-"*45)
    print("1. Registrar Receita (+)")
    print("2. Registrar Despesa (-)")
    
    opcao = input("\nEscolha o tipo (1/2): ").strip()
    if opcao == "1":
        tipo = "Receita"
    elif opcao == "2":
        tipo = "Despesa"
    else:
        print("❌ Opção inválida!")
        return

    try:
        valor_input = input("Digite o valor (ex: 150.50): ").strip()
        valor = float(valor_input)
        if valor <= 0:
            print("❌ Erro: O valor deve ser maior que zero.")
            return
    except ValueError:
        print("❌ Erro: Digite um número decimal válido.")
        return

    descricao = input("Digite uma descrição curta (ex: Almoço RU): ").strip()
    if not descricao:
        descricao = "Sem descrição"

    print("\nCategorias sugeridas: Alimentação, Transporte, Lazer, Saúde, Educação, Outros")
    categoria = input("Digite a categoria: ").strip()
    if not categoria:
        categoria = "Outros"

    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    try:
        cursor.execute("""
            INSERT INTO Transacoes (usuario_id, valor, tipo, data, descricao, categoria)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (usuario_id, valor, tipo, data_atual, descricao, categoria))
        conexao.commit()
        print(f"\n✅ {tipo} de R$ {valor:.2f} registrada com sucesso!")
    except sqlite3.Error as e:
        print(f"❌ Erro ao salvar transação: {e}")
    finally:
        conexao.close()

def consultar_saldo(usuario_id):
    """Calcula e apresenta o saldo contábil com o Alerta de Saldo Devedor (REQ-BUS-01)."""
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    
    # Query matemática de consolidação usando a nova coluna 'tipo' (REQ-DOM-01)
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN tipo = 'Receita' THEN valor ELSE 0 END) as total_receitas,
            SUM(CASE WHEN tipo = 'Despesa' THEN valor ELSE 0 END) as total_despesas
        FROM Transacoes 
        WHERE usuario_id = ?;
    """, (usuario_id,))
    
    resultado = cursor.fetchone()
    conexao.close()
    
    total_receitas = resultado[0] or 0.0
    total_despesas = resultado[1] or 0.0
    saldo_liquido = total_receitas - total_despesas
    
    print("\n" + "="*45)
    print("             SALDO CONSOLIDADO               ")
    print("="*45)
    print(f"(+) Total Receitas: R$ {total_receitas:.2f}")
    print(f"(-) Total Despesas: R$ {total_despesas:.2f}")
    print(f"(=) Saldo Líquido:  R$ {saldo_liquido:.2f}")
    print("-"*45)
    
    # Regra de Alerta de Saldo Devedor (REQ-BUS-01)
    if saldo_liquido < 0:
        print("\033[1;31m🔴 ATENÇÃO: SALDO DEVEDOR! (Alerta de Contenção de Gastos)\033[0m")
    else:
        print("\033[1;32m🟢 CONTA SAUDÁVEL\033[0m")
    print("="*45)

def listar_movimentacoes(usuario_id):
    """Lista todas as transações cadastradas pelo usuário logado."""
    print("\n" + "-"*65)
    print("             HISTÓRICO DE MOVIMENTAÇÕES              ")
    print("-"*65)
    
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT valor, tipo, data, descricao, categoria 
        FROM Transacoes 
        WHERE usuario_id = ? 
        ORDER BY data DESC;
    """, (usuario_id,))
    
    transacoes = cursor.fetchall()
    conexao.close()
    
    if not transacoes:
        print("Nenhum lançamento cadastrado neste usuário.")
        print("-"*65)
        return
        
    print(f"{'DATA':<20} | {'TIPO':<8} | {'VALOR':<10} | {'CATEGORIA':<12} | {'DESCRIÇÃO'}")
    print("-"*65)
    for t in transacoes:
        valor, tipo, data, desc, cat = t
        sinal = "+" if tipo == "Receita" else "-"
        print(f"{data:<20} | {tipo:<8} | {sinal}R${valor:>7.2f} | {cat:<12} | {desc}")
    print("-"*65)

def ver_resumo_por_categoria(usuario_id):
    """Exibe o agrupamento gráfico em texto de despesas por categoria (RU06)."""
    print("\n" + "-"*45)
    print("         DESPESAS POR CATEGORIA (RU06)       ")
    print("-"*45)
    
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    
    # Soma as despesas agrupando por categoria
    cursor.execute("""
        SELECT categoria, SUM(valor) as total
        FROM Transacoes
        WHERE usuario_id = ? AND tipo = 'Despesa'
        GROUP BY categoria
        ORDER BY total DESC;
    """, (usuario_id,))
    
    gastos = cursor.fetchall()
    conexao.close()
    
    if not gastos:
        print("Nenhuma despesa lançada para gerar resumo.")
        print("-"*45)
        return
        
    # Calcula o total de despesas para tirar o percentual
    total_gasto = sum([g[1] for g in gastos])
    
    for g in gastos:
        cat, valor = g
        perc = (valor / total_gasto) * 100 if total_gasto > 0 else 0
        barra = "■" * int(perc / 5)
        print(f"{cat:<12} | R$ {valor:>7.2f} ({perc:>5.1f}%) {barra}")
    print("-"*45)

def exibir_painel_principal(usuario_id):
    """Menu principal do usuário logado (Painel Financeiro)."""
    while True:
        print("\n" + "=" * 45)
        print("       SISTEMA FAMT CONTROL LIBERADO!        ")
        print("=" * 45)
        print("1. Consultar Saldo e Status")
        print("2. Registrar Novo Lançamento (Receita/Despesa)")
        print("3. Consultar Histórico de Movimentações")
        print("4. Consultar Resumo por Categoria")
        print("5. Fazer Logout")
        
        opcao = input("\nEscolha uma opção (1/2/3/4/5): ").strip()
        
        if opcao == "1":
            consultar_saldo(usuario_id)
        elif opcao == "2":
            registrar_lancamento(usuario_id)
        elif opcao == "3":
            listar_movimentacoes(usuario_id)
        elif opcao == "4":
            ver_resumo_por_categoria(usuario_id)
        elif opcao == "5":
            print("\nSaindo do painel e fechando sessão...")
            break
        else:
            print("❌ Opção inválida!")

# PROGRAMA PRINCIPAL
if __name__ == "__main__":
    inicializar_banco()
    
    while True:
        print("\n" + "=" * 45)
        print("             SQUAD FAMT CONTROL              ")
        print("=" * 45)
        print("1. Fazer Login")
        print("2. Cadastrar Novo Usuário")
        print("3. Fechar Programa")
        
        opcao = input("\nEscolha uma opção (1/2/3): ").strip()
        
        if opcao == "1":
            usuario_logado = realizar_login()
            if usuario_logado:
                exibir_painel_principal(usuario_logado)
                # Opcional: retira o break anterior se quiser que o programa volte ao menu inicial pós logout,
                # ou mantém se quiser que feche. Deixarei livre para voltar ao menu de login!
        elif opcao == "2":
            cadastrar_usuario()
        elif opcao == "3":
            print("Encerrando o programa...")
            break
        else:
            print("❌ Opção inválida! Escolha 1, 2 ou 3.")
