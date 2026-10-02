import sqlite3
import os

DB_NAME = "famt_control.db"

def inicializar_banco():
    """Cria a estrutura oficial do banco de dados se não existir."""
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Tabela oficial de usuários com controle de primeiro acesso
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        primeiro_acesso INTEGER DEFAULT 1 -- 1 para Sim, 0 para Não
    );
    """)
    
    # Tabela oficial de transações
    cursor.execute("""
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
    conexao.commit()
    conexao.close()

def cadastrar_usuario():
    """Permite cadastrar QUALQUER e-mail novo no banco de dados."""
    print("\n" + "-"*45)
    print("        CADASTRO DE NOVO USUÁRIO             ")
    print("-"*45)
    
    email = input("Digite o e-mail que deseja cadastrar: ").strip().lower()
    
    if not email or "@" not in email:
        print("❌ Erro: Digite um e-mail válido (exemplo@email.com).")
        return

    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    
    try:
        # Cadastra o novo e-mail com a senha provisória padrão 'famt123'
        cursor.execute("""
            INSERT INTO Usuarios (email, senha_hash, primeiro_acesso) 
            VALUES (?, 'famt123', 1)
        """, (email,))
        conexao.commit()
        print(f"\n✅ Usuário '{email}' cadastrado com sucesso!")
        print("🔑 A senha provisória para o primeiro acesso é: famt123")
    except sqlite3.IntegrityError:
        print("\n❌ Erro: Este e-mail já está cadastrado no sistema!")
    finally:
        conexao.close()

def realizar_login():
    """Gerencia o login e força a redefinição se for o primeiro acesso."""
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
        
    usuario_id, senha_banco, primeiro_acesso = usuario
    
    if senha != senha_banco:
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
                cursor.execute("""
                    UPDATE Usuarios 
                    SET senha_hash = ?, primeiro_acesso = 0 
                    WHERE id = ?
                """, (nova_senha, usuario_id))
                conexao.commit()
                print("\n✅ Senha definitiva salva com sucesso!")
                break
                
    print(f"\n🔓 Login efetuado com sucesso! Bem-vindo(a) ao FAMT Control.")
    conexao.close()
    return usuario_id

def exibir_painel_principal(usuario_id):
    print("\n" + "=" * 45)
    print("       SISTEMA FAMT CONTROL LIBERADO!        ")
    print("=" * 45)
    print(f"Painel Financeiro do Usuário ID: {usuario_id}")
    input("\nPressione Enter para sair do sistema...")

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
                break # Fecha após sair do painel
        elif opcao == "2":
            cadastrar_usuario()
        elif opcao == "3":
            print("Encerrando o programa...")
            break
        else:
            print("❌ Opção inválida! Escolha 1, 2 ou 3.")