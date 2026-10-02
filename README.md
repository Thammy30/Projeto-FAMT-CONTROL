# 💜 FAMT CONTROL

> **Seu dinheiro sob controle.**

O **FAMT CONTROL** é uma aplicação web de **gestão financeira pessoal**, desenvolvida para facilitar o controle de receitas, despesas, metas e movimentações financeiras em um único sistema.

O projeto possui uma interface moderna em **Dark Mode**, com identidade visual própria e dashboard interativo para acompanhamento da vida financeira.

---

## 📌 Sobre o Projeto

O FAMT CONTROL foi desenvolvido como uma solução de controle financeiro pessoal, permitindo que o usuário registre suas movimentações e acompanhe sua situação financeira por meio de indicadores, gráficos e informações organizadas.

A aplicação utiliza **Streamlit** para a interface, **SQLite** para armazenamento dos dados e **Plotly** para geração dos gráficos.

---

## ✨ Funcionalidades

### 🔐 Login e Cadastro

* Cadastro de novos usuários
* Login utilizando e-mail e senha
* Senhas armazenadas utilizando **hash SHA-256**
* Controle de primeiro acesso
* Alteração obrigatória da senha provisória no primeiro acesso

### 💰 Controle Financeiro

* Cadastro de **Receitas**
* Cadastro de **Despesas**
* Registro de valor, descrição, categoria e data
* Cálculo automático de:

  * Total de receitas
  * Total de despesas
  * Saldo atual
* Histórico das movimentações

### 📊 Dashboard

O painel principal apresenta:

* Total de receitas
* Total de despesas
* Saldo atual
* Meta financeira
* Progresso da meta
* Receitas x Despesas
* Gastos por categoria
* Últimos lançamentos
* Notificações
* Alertas e dicas financeiras

### 🎯 Metas

O sistema possui uma área destinada ao acompanhamento de metas financeiras e progresso dos objetivos.

### 🔔 Notificações

O sistema gera notificações de acordo com as movimentações financeiras, incluindo informações sobre saldo e últimos lançamentos.

### 📈 Gráficos

Utilização de gráficos interativos para facilitar a visualização das informações financeiras:

* Gráfico de Receitas x Despesas
* Gráfico de gastos por categoria

### 🧾 Extrato e Edição

Permite consultar os lançamentos cadastrados e realizar alterações nas movimentações.

### 🎨 Interface

* Dark Mode
* Identidade visual própria
* Logo oficial do FAMT CONTROL
* Layout responsivo
* Navegação por menu lateral
* Interface desenvolvida com CSS personalizado

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia   | Utilização                       |
| ------------ | -------------------------------- |
| 🐍 Python    | Linguagem principal              |
| 🎈 Streamlit | Desenvolvimento da interface web |
| 🗄️ SQLite   | Banco de dados                   |
| 🐼 Pandas    | Manipulação e análise dos dados  |
| 📊 Plotly    | Gráficos interativos             |
| 🔐 hashlib   | Hash das senhas                  |
| 🎨 HTML/CSS  | Personalização da interface      |

---

## 🗂️ Estrutura do Projeto

```text
FAMT-CONTROL/
│
├── famt-control-app-com-logo-v9.py
├── famt_control.db
├── Logo Fintech FAMT Control.png
├── README.md
└── requirements.txt
```

---

## ⚙️ Como Executar o Projeto

### 1. Clone o repositório

```bash
git clone https://github.com/SEU-USUARIO/FAMT-CONTROL.git
```

Entre na pasta:

```bash
cd FAMT-CONTROL
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

Caso ainda não exista um `requirements.txt`, instale as principais bibliotecas:

```bash
pip install streamlit pandas plotly
```

### 3. Execute a aplicação

```bash
python -m streamlit run famt-control-app-com-logo-v9.py
```

O Streamlit abrirá a aplicação no navegador, normalmente em:

```text
http://localhost:8501
```

---

## 🔑 Acesso para Demonstração

O projeto possui um usuário padrão para testes.

**E-mail:**

```text
thamirys@umc.edu.br
```

**Senha:**

```text
famt123
```

> ⚠️ Essa credencial existe apenas para demonstração/testes do projeto. Em um ambiente de produção, recomenda-se utilizar credenciais próprias e não manter senhas padrão no código.

---

## 🗄️ Banco de Dados

O projeto utiliza **SQLite**.

Entre as tabelas utilizadas estão:

### `Usuarios`

Responsável pelo armazenamento dos usuários do sistema.

Principais campos:

* `id`
* `email`
* `senha_hash`
* `primeiro_acesso`

### `Transacoes`

Responsável pelo armazenamento das movimentações financeiras.

Principais campos:

* `id`
* `usuario_id`
* `valor`
* `tipo`
* `data`
* `descricao`
* `categoria`

As transações possuem relacionamento com o usuário por meio da chave estrangeira `usuario_id`.

---

## 🔐 Segurança

O projeto possui algumas medidas básicas de segurança, incluindo:

* Hash de senha utilizando **SHA-256**
* Separação dos dados financeiros por usuário
* Chaves estrangeiras no banco de dados
* Validação de campos obrigatórios
* Controle de sessão utilizando `st.session_state`
* Alteração obrigatória da senha provisória no primeiro acesso

> Para utilização em produção, recomenda-se implementar mecanismos adicionais de segurança, como gerenciamento de sessões mais robusto, armazenamento seguro de segredos e um algoritmo moderno de derivação de senha com salt.

---

## 🎯 Objetivo do Projeto

O FAMT CONTROL tem como objetivo proporcionar uma experiência simples e visual para o gerenciamento das finanças pessoais.

A proposta é permitir que o usuário:

**Registre → Acompanhe → Analise → Organize → Alcance seus objetivos.**

---

## 🚀 Possíveis Evoluções

Entre as possibilidades de evolução do projeto estão:

* ☁️ Integração com banco de dados em nuvem
* 📱 Melhorias para dispositivos móveis
* 📧 Notificações por e-mail
* 📊 Relatórios financeiros
* 📥 Exportação para Excel/CSV
* 🎯 Metas financeiras personalizadas
* 🔐 Autenticação mais avançada
* 📈 Mais indicadores e análises financeiras
* 💳 Integração com cartões e contas bancárias

---

## 👩‍💻 Desenvolvimento

**FAMT CONTROL**

Projeto desenvolvido pelo **Squad FAMT** como uma aplicação de gestão financeira pessoal.

> **Seu dinheiro sob controle.**

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos e de demonstração.

Consulte o arquivo de licença do repositório para obter informações sobre utilização e distribuição.
