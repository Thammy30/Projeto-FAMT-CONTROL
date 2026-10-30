# 💜 FAMT CONTROL

> **Seu dinheiro sob controle.**

Aplicativo web de **gestão financeira pessoal**, desenvolvido para facilitar o controle de receitas, despesas, metas e movimentações financeiras em um único sistema.

O projeto possui uma interface moderna em **Dark Mode**, identidade visual própria e dashboard interativo para acompanhamento da vida financeira.

> **Universidade de Mogi das Cruzes (UMC)**  
> Curso: Engenharia de Software  
> Semestre: 2026/2  
> Orientador: Prof. Renato  
> Projeto desenvolvido pela Squad FAMT.

---

## 📌 Sobre o Projeto

O **FAMT CONTROL** foi desenvolvido como uma solução de controle financeiro pessoal, permitindo que os usuários registrem suas movimentações, acompanhem sua situação financeira e organizem seus objetivos por meio de indicadores, gráficos e informações centralizadas.

A proposta é oferecer uma ferramenta simples, intuitiva e acessível, substituindo controles manuais e planilhas complexas por uma aplicação web organizada.

O sistema utiliza **Python**, **Streamlit**, **SQLite** e **Plotly**, combinando funcionalidades financeiras com uma interface visual personalizada.

### 🌟 Principais benefícios

- Centralização das informações financeiras.
- Controle de receitas e despesas.
- Acompanhamento de metas e objetivos.
- Visualização de indicadores financeiros.
- Gráficos interativos.
- Organização do histórico de movimentações.
- Controle de acesso por usuário.

---

## 👥 Squad FAMT e Atribuições

O desenvolvimento do projeto foi realizado de forma colaborativa, com responsabilidades distribuídas entre os integrantes da equipe.

| Integrante | Matrícula (RA) | Papel | Principais atribuições |
|---|---|---|---|
| Franciellen Moreira Santos | 11261403634 | Gerente de Projetos (PM) | Coordenação geral, cronograma CPM, documentação TAP/EAP e matriz de comunicação. |
| Maria Augusta S. Toledo | 11241102057 | Product Owner (PO) / QA | Priorização do Backlog, aceite de User Stories, BDD e testes com Pytest. |
| André Mitchel Ruiz Santos | 11231102531 | Tech Lead / Desenvolvedor | Arquitetura Python/Streamlit, regras de negócio, gráficos Plotly e segurança. |
| Thamirys Matos da Silva | 11261403155 | Engenheira de Dados (DBA) | Modelagem relacional em 3FN, estrutura do banco de dados, constraints e índices. |

---

## ✨ Funcionalidades do Sistema

### 🔐 Login e Cadastro

- Cadastro de novos usuários.
- Login utilizando e-mail e senha.
- Armazenamento de senhas utilizando hash SHA-256.
- Controle de primeiro acesso.
- Alteração obrigatória da senha provisória no primeiro acesso.

### 💰 Controle Financeiro

- Cadastro de receitas.
- Cadastro de despesas.
- Registro de valor, descrição, categoria e data.
- Cálculo automático de:
  - Total de receitas.
  - Total de despesas.
  - Saldo atual.
- Histórico das movimentações financeiras.

### 📊 Dashboard

O painel principal apresenta:

- Total de receitas.
- Total de despesas.
- Saldo atual.
- Meta financeira.
- Progresso da meta.
- Receitas x Despesas.
- Gastos por categoria.
- Últimos lançamentos.
- Notificações.
- Alertas e dicas financeiras.

### 🎯 Metas Financeiras

Área destinada ao acompanhamento de metas e objetivos financeiros, permitindo visualizar o progresso das economias.

### 🔔 Notificações

O sistema apresenta notificações relacionadas às movimentações financeiras, incluindo informações sobre saldo e últimos lançamentos.

### 📈 Gráficos Interativos

Utilização da biblioteca Plotly para facilitar a visualização das informações financeiras:

- Gráfico de Receitas x Despesas.
- Gráfico de gastos por categoria.

### 🧾 Extrato e Edição

Permite consultar as movimentações cadastradas, visualizar o histórico e realizar alterações ou exclusões de lançamentos.

### 🎨 Interface

- Dark Mode.
- Identidade visual própria.
- Logo oficial do FAMT CONTROL.
- Layout responsivo.
- Navegação por menu lateral.
- Interface personalizada com CSS.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Utilização |
|---|---|
| 🐍 Python | Linguagem principal de desenvolvimento. |
| 🎈 Streamlit | Desenvolvimento da interface web. |
| 🗄️ SQLite | Banco de dados relacional. |
| 🐼 Pandas | Manipulação e análise dos dados. |
| 📊 Plotly | Criação de gráficos interativos. |
| 🔐 hashlib | Funções de hash para senhas. |
| 🎨 HTML/CSS | Personalização da interface. |
| 🧪 Pytest | Testes automatizados. |
| 🔧 Git/GitHub | Controle de versão e colaboração. |

---

## 🏗️ Arquitetura do Sistema

O FAMT CONTROL utiliza uma estrutura modular, com responsabilidades organizadas em três camadas principais:

| Camada | Responsabilidade |
|---|---|
| Interface de Usuário (UI) | Apresentação das informações e interação com o usuário por meio do Streamlit. |
| Regras de Negócio | Processamento das movimentações, cálculos financeiros e validações. |
| Persistência de Dados | Armazenamento, consultas e gerenciamento das informações no SQLite. |

Essa organização facilita a manutenção, a compreensão do código e a evolução do sistema.

---

## 🗄️ Banco de Dados

O projeto utiliza **SQLite** para armazenar os dados financeiros e informações dos usuários.

Entre as principais estruturas do banco de dados estão:

### `Usuarios`

Responsável pelo armazenamento dos usuários do sistema.

Principais campos:

- `id`
- `email`
- `senha_hash`
- `primeiro_acesso`

### `Transacoes`

Responsável pelo armazenamento das movimentações financeiras.

Principais campos:

- `id`
- `usuario_id`
- `valor`
- `tipo`
- `data`
- `descricao`
- `categoria`

As transações possuem relacionamento com os usuários por meio da chave estrangeira `usuario_id`, permitindo organizar os registros de acordo com cada conta.

---

## 🔐 Segurança e Proteção de Dados

O FAMT CONTROL possui mecanismos básicos de segurança para proteger as informações dos usuários:

- Hash de senhas utilizando SHA-256.
- Separação dos dados financeiros por usuário.
- Chaves estrangeiras no banco de dados.
- Validação de campos obrigatórios.
- Controle de sessão utilizando `st.session_state`.
- Alteração obrigatória da senha provisória no primeiro acesso.

**Observação:** para utilização em produção, recomenda-se substituir o SHA-256 isolado por algoritmos específicos para armazenamento de senhas, como Argon2 ou bcrypt, além de implementar mecanismos adicionais de proteção.

O tratamento das informações também deve observar os princípios e requisitos aplicáveis da Lei Geral de Proteção de Dados (LGPD).

---

## 📊 Governança e Metodologia Híbrida

Além do desenvolvimento da aplicação, o projeto envolveu práticas de planejamento, organização e gerenciamento de projetos de software.

A Squad FAMT adotou uma **metodologia híbrida**, combinando características do modelo Waterfall (Cascata) com práticas do Scrum.

### 🏛️ Planejamento — Waterfall

Na etapa de planejamento, foram utilizados instrumentos de gerenciamento baseados nas práticas do PMI/PMBOK:

- Termo de Abertura do Projeto (TAP).
- Estrutura Analítica do Projeto (EAP/WBS).
- Dicionário da EAP.
- Cronograma PDM.
- Análise do Caminho Crítico (CPM).
- Matriz de Probabilidade e Impacto (PxI).
- Matriz RACI.

### 🔄 Execução — Scrum

Durante a execução, foram utilizados artefatos e práticas do Scrum:

- Product Backlog.
- User Stories (US-001 a US-006).
- BDD (Behavior Driven Development).
- Definition of Done (DoD).
- Definition of Ready (DoR).
- Quadro Kanban.
- Gráfico Burndown.

A combinação dessas abordagens permitiu estruturar o planejamento e, ao mesmo tempo, acompanhar a execução e a evolução das funcionalidades.

---

## 🎯 Priorização das Funcionalidades — Matriz MoSCoW

A técnica MoSCoW foi utilizada para organizar e priorizar os requisitos do projeto de acordo com sua importância.

### 🔴 Must Have — Obrigatórias

- Cadastro de receitas e despesas.
- Categorização das movimentações.
- Cálculo automático do saldo.
- Extrato e histórico financeiro.
- Controle de acesso.
- Proteção das informações dos usuários.

### 🟡 Should Have — Desejáveis

- Dashboard com indicadores financeiros.
- Atalhos rápidos na página inicial.
- Filtros de extrato por período e categoria.

### 🟢 Could Have — Opcionais

- Simulador de economia mensal.
- Metas financeiras.
- Exportação de dados e extratos.

### ⚪ Won't Have — Fora do Escopo

- Integração direta com Open Finance ou APIs bancárias reais.
- Aplicativo móvel nativo para Android e iOS.
- Gateway de pagamentos.

---

## 📈 Indicadores Financeiros e Cronograma do Projeto

O planejamento financeiro e temporal foi estruturado durante a etapa de gerenciamento do projeto.

| Indicador | Valor |
|---|---:|
| Orçamento Previsto (BAC) | R$ 12.454,50 |
| Linha de Base de Custos | R$ 11.913,00 |
| Reserva de Contingência | R$ 541,50 |
| Prazo total | 21 dias úteis |
| Execução planejada | 4 Sprints semanais |

---

## 🗂️ Estrutura do Projeto

O repositório está organizado para separar os arquivos da aplicação, banco de dados, documentação e testes.

```text
FAMT-CONTROL/
│
├── famt-control-app-com-logo.py
├── famt_control.db
├── Logo Fintech FAMT Control.png
├── README.md
├── requirements.txt
│
├── docs/
│   ├── famt-control-documento-completo-projeto-m1.docx
│   ├── famt-control-relatorio-qualidade-comunicacao-stakeholders.docx
│   └── famt-control-relatorio-transicao-waterfall-scrum.docx
│
└── tests/
    └── test_famt_control.py
```

### Descrição dos principais arquivos

| Arquivo | Descrição |
|---|---|
| `famt-control-app-com-logo.py` | Arquivo principal da aplicação Streamlit. |
| `famt_control.db` | Banco de dados SQLite. |
| `Logo Fintech FAMT Control.png` | Identidade visual oficial do sistema. |
| `requirements.txt` | Dependências necessárias para execução. |
| `docs/` | Documentação técnica e gerencial do projeto. |
| `tests/` | Arquivos destinados aos testes automatizados. |

---

## 🚀 Como Executar o Projeto

Siga os passos abaixo para executar o FAMT CONTROL localmente.

### 1. Clone o repositório

```bash
git clone https://github.com/SEU-USUARIO/FAMT-CONTROL.git
```

### 2. Entre na pasta do projeto

```bash
cd FAMT-CONTROL
```

### 3. Crie um ambiente virtual

```bash
python -m venv .venv
```

### 4. Ative o ambiente virtual

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 5. Instale as dependências

```bash
pip install -r requirements.txt
```

Caso ainda não tenha um arquivo `requirements.txt`, instale as principais bibliotecas:

```bash
pip install streamlit pandas plotly
```

### 6. Execute a aplicação

```bash
python -m streamlit run famt-control-app-com-logo.py
```

Após a execução, acesse a aplicação pelo navegador:

```text
http://localhost:8501
```

---

## 🔑 Acesso para Demonstração

O projeto possui um usuário padrão para testes e demonstração.

**E-mail:**

```text
thamirys@umc.edu.br
```

**Senha:**

```text
famt123
```

> ⚠️ Credenciais destinadas exclusivamente à demonstração acadêmica. Recomenda-se não utilizar contas ou senhas padrão em ambientes de produção.

---

## 🧪 Qualidade e Testes

A qualidade do software é considerada durante o desenvolvimento e a validação das funcionalidades, tendo como referência a norma **ISO/IEC 25010**, que estabelece características para avaliação da qualidade de produtos de software.

Os testes automatizados são organizados utilizando o framework Pytest.

Para executar os testes, utilize:

```bash
pytest -v
```

---

## 🚀 Possíveis Evoluções

Entre as possibilidades de evolução do FAMT CONTROL estão:

- ☁️ Integração com banco de dados em nuvem.
- 📱 Melhorias para dispositivos móveis.
- 📧 Notificações por e-mail.
- 📊 Relatórios financeiros.
- 📥 Exportação para Excel/CSV.
- 🎯 Metas financeiras personalizadas.
- 🔐 Autenticação mais avançada.
- 📈 Novos indicadores e análises financeiras.
- 💳 Integração com cartões e contas bancárias.

---

## 📄 Licença e Direitos Autorais

Este projeto foi desenvolvido pela **Squad FAMT** para fins acadêmicos, como parte das atividades do curso de Engenharia de Software da Universidade de Mogi das Cruzes (UMC).

© 2026 Squad FAMT. Todos os direitos reservados.

---

<p align="center">
  💜 <strong>FAMT CONTROL</strong><br>
  <em>Seu dinheiro sob controle.</em><br><br>
  Desenvolvido com dedicação pela Squad FAMT.
</p>
