# 💻 Por Dentro do Projeto: Cadastro de Clientes da Livraria

Bem-vindo à documentação técnica do Sistema de Cadastro da Livraria! Este arquivo serve como um guia para entender a arquitetura, as tecnologias e as principais lógicas por trás do código.

---

### 🏛️ Visão Geral da Arquitetura

Este projeto foi construído em três camadas principais que trabalham juntas para criar a aplicação:

1.  **Interface com o Usuário (Frontend)**: A camada visual com a qual o usuário interage. Foi construída com **Tkinter**, a biblioteca padrão do Python para interfaces gráficas. É responsável por exibir janelas, botões, campos de texto e listas.

2.  **Lógica da Aplicação (Core)**: O cérebro do sistema, escrito em **Python**. Esta camada, representada principalmente pela classe `Aplicacao`, gerencia os eventos da interface (cliques de botão, seleção de itens), valida os dados e orquestra a comunicação entre a interface e o banco de dados.

3.  **Camada de Dados (Database)**: Onde todas as informações são armazenadas de forma permanente. Usamos o **SQLite 3**, um banco de dados leve e baseado em arquivo, que é perfeito para aplicações desktop, pois não requer um servidor separado.

A interação acontece da seguinte forma:
`Usuário na Interface (Tkinter)` -> `aciona um evento` -> `Lógica da Aplicação (Python)` -> `processa e consulta/grava no` -> `Banco de Dados (SQLite)`

---

### ⚙️ Comandos e Funções Principais

Aqui está uma referência rápida dos principais módulos, comandos e funções utilizados no projeto.

#### 🔹 Módulos Importados

| Módulo | O que faz no projeto |
|---|---|
| `tkinter` | Constrói toda a interface gráfica (janelas, botões, etc.). |
| `sqlite3` | Permite a conexão e a manipulação do banco de dados SQLite. |
| `requests` | Realiza as chamadas HTTP para a API do IBGE para buscar estados e cidades. |
| `csv` | Utilizado na função "Exportar para CSV" para escrever os dados em um arquivo. |
| `re` | Módulo de Expressões Regulares, usado para validar o formato do e-mail. |

#### 🔹 Comandos Tkinter (Interface Gráfica)

| Comando/Função | O que faz |
|---|---|
| `Tk()` | Cria a janela principal da aplicação. |
| `Frame(...)` | Cria um contêiner (uma "caixa") para organizar outros widgets. |
| `Label(...)` | Exibe um texto fixo na tela. |
| `Entry(...)` | Cria um campo para o usuário digitar texto. |
| `Button(...)` | Cria um botão clicável que executa uma função. |
| `ttk.Combobox(...)` | Cria uma caixa de seleção com uma lista de opções. |
| `ttk.Treeview(...)` | Cria a tabela para listar os clientes e as compras. |
| `Toplevel(...)` | Cria uma nova janela secundária (usada para a tela de compras). |
| `widget.place(...)` | Posiciona um widget na tela usando coordenadas. |
| `widget.bind(evento, funcao)` | Associa um evento (ex: duplo-clique) a uma função. |
| `janela.mainloop()` | Inicia o loop da aplicação, que a mantém aberta e responsiva. |

#### 🔹 Comandos SQLite (Banco de Dados)

| Comando/Função | O que faz |
|---|---|
| `sqlite3.connect('arquivo.db')` | Conecta-se a um arquivo de banco de dados (e o cria se não existir). |
| `conexao.cursor()` | Cria um objeto "cursor" para executar comandos SQL. |
| `cursor.execute('COMANDO SQL')` | Executa uma instrução SQL na base de dados. |
| `conexao.commit()` | Salva permanentemente as alterações (INSERT, UPDATE, DELETE) no banco. |
| `cursor.fetchall()` | Retorna todas as linhas resultantes de um comando `SELECT`. |

#### 🔹 Funções Principais da Aplicação

| Método da Classe | O que faz |
|---|---|
| `__init__()` | O construtor da classe. Inicializa e monta toda a aplicação. |
| `cadastrar_cliente()` | Pega os dados dos campos e os insere na tabela `clientes`. |
| `carregar_clientes()` | Lê os dados do banco de dados e os exibe na tabela `Treeview`. |
| `carregar_cliente_para_edicao()` | Preenche os campos do formulário ao dar um duplo-clique em um cliente. |
| `atualizar_cliente()` | Modifica os dados de um cliente já existente no banco. |
| `excluir_cliente()` | Remove um cliente e suas compras associadas do banco. |
| `abrir_janela_compras()` | Abre a janela secundária para gerenciar as compras de um cliente. |
| `buscar_estados_e_cidades()` | Conecta-se à API do IBGE para obter a lista de localidades. |
| `exportar_para_csv()` | Salva os dados dos clientes em um arquivo `.csv`. |

---

### ❤️ O Coração do Código: A Classe `Aplicacao`

Quase toda a funcionalidade do sistema está organizada dentro da classe `Aplicacao`. Essa abordagem de Programação Orientada a Objetos ajuda a manter o código organizado e coeso.

#### 🔹 O Método `__init__` (O Construtor)
O método `__init__` é o ponto de partida. Quando a aplicação é iniciada, ele executa uma sequência de tarefas essenciais:

1.  **Conexão com o Banco**: Chama `conectar_banco()` para estabelecer a conexão com o arquivo `clientes_livraria.db`.
2.  **Busca de Dados Externos**: Executa `buscar_estados_e_cidades()` para popular os menus de seleção de localidade via API do IBGE.
3.  **Criação da Janela Principal**: Define o título, tamanho e cor de fundo da janela principal (`self.janela`).
4.  **Construção dos Frames**: Chama `self.frames()` para criar os contêineres principais da interface.
5.  **Adição dos Widgets**: Chama `self.widgets_frame1()` e `self.widgets_frame2()` para popular os frames com botões, labels e campos de texto.
6.  **Carregamento Inicial**: Executa `self.carregar_clientes()` para que a lista de clientes já apareça na tela assim que o programa abre.
7.  **Bindings de Eventos**: Configura atalhos de teclado, como `Enter` para pular de campo e `Ctrl +` para o zoom.

---
### 🎨 Construindo a Interface com Tkinter

A interface é dividida em dois Frames principais, que funcionam como caixas para organizar os componentes. Dentro deles, usamos vários Widgets.

🔹 Principais Widgets Utilizados:
Label: Para exibir textos fixos (ex: "Nome:", "E-mail:").

Entry: Campos de texto onde o usuário pode digitar informações.

Button: Botões clicáveis que acionam funções (ex: "Cadastrar", "Excluir").

ttk.Combobox: Caixas de seleção suspensas, usadas para escolher o Estado e a Cidade.

ttk.Treeview: O componente mais complexo, usado para exibir a lista de clientes e de compras em um formato de tabela organizada.

🔹 Posicionamento com .place()
Para posicionar os widgets, usamos o método .place(). Ele permite um controle preciso sobre a localização e o tamanho de cada elemento usando coordenadas relativas (relx, rely) e tamanho relativo (relwidth, relheight), o que ajuda a interface a se adaptar a diferentes tamanhos de janela.

# Exemplo de criação de um widget
self.lbl_nome = Label(self.frame_1, text="Nome:", bg="#dbeadf")
self.lbl_nome.place(x=10, y=20) # Posição absoluta dentro do frame

self.entry_nome = Entry(self.frame_1, width=50)
self.entry_nome.place(x=100, y=20)

🗄️ Interagindo com o Banco de Dados (SQLite)
Toda a persistência de dados é feita através do SQLite. A comunicação é gerenciada por dois objetos principais:

conexao: A conexão ativa com o arquivo do banco de dados.

cursor: Um objeto que nos permite executar comandos SQL.

🔹 Executando um Comando (CRUD)
Vamos analisar a função cadastrar_cliente como exemplo de uma operação de Create (Criar).

Obtenção dos Dados: Os dados são pegos dos widgets Entry e Combobox.

Execução do SQL: O comando self.cursor.execute() é chamado.

Segurança (Query Parameters): Note o uso de ? no comando SQL. Isso é uma prática de segurança essencial para prevenir ataques de SQL Injection. A biblioteca sqlite3 substitui os ? pelos valores da tupla (nome, email, ...) de forma segura.

Commit: O comando self.conexao.commit() efetivamente salva as alterações no arquivo do banco de dados. Sem ele, as mudanças seriam perdidas.

# Exemplo da função de cadastro
def cadastrar_cliente(self):
    # 1. Pega os dados da interface
    nome = self.entry_nome.get().strip()
    email = self.entry_email.get().strip()
    # ...

    # 2. Executa o comando SQL de forma segura
    try:
        self.cursor.execute("""
            INSERT INTO clientes (nome, email, telefone, cidade, estado) 
            VALUES (?, ?, ?, ?, ?)
        """, (nome, email, telefone, cidade, estado))
        
        # 4. Salva as alterações
        self.conexao.commit()
        # ...
    except sqlite3.IntegrityError:
        # Trata o erro de e-mail duplicado
        messagebox.showerror("Erro", f"O e-mail '{email}' já está cadastrado.")

### ✨ Funções e Eventos Principais

🔹 carregar_cliente_para_edicao(self, event)
Esta função demonstra o poder dos eventos em Tkinter.

Binding: Na configuração da Treeview, a linha self.lista_clientes.bind("<Double-1>", ...) associa o evento de "duplo-clique do botão esquerdo do mouse" a esta função.

Ação: Quando o evento ocorre, a função identifica o item selecionado, extrai seus valores e preenche os campos Entry e Combobox para edição.

🔹 abrir_janela_compras() - A Janela Secundária
Toplevel: Para não travar a janela principal, criamos uma nova janela com o widget Toplevel. Isso permite que ambas as janelas (principal e de compras) coexistam.

Funções Aninhadas e nonlocal: Para manter a lógica da janela de compras organizada e contida, foram usadas funções aninhadas (uma função definida dentro de outra). A palavra-chave nonlocal é usada para permitir que a função aninhada modifique uma variável que pertence à função "mãe" (abrir_janela_compras), como a id_compra_selecionada.

🔹 buscar_estados_e_cidades() - Conectando com o Mundo Real
API Externa: Esta função usa a biblioteca requests para fazer uma chamada HTTP à API pública do IBGE.

Tratamento de Erros: O bloco try...except é fundamental aqui. Ele "tenta" fazer a conexão com a internet. Se falhar (por exemplo, se o usuário estiver offline ou a API do IBGE estiver fora do ar), o except captura o erro, exibe uma mensagem amigável e carrega uma lista mínima de cidades, garantindo que o programa não trave.

💡 Pequenos Detalhes, Grande Diferença
---
O projeto inclui algumas funcionalidades de experiência do usuário que enriquecem a aplicação:

Máscara de Telefone: A função formatar_telefone_mask aplica dinamicamente o formato (DD) XXXXX-XXXX enquanto o usuário digita, melhorando a usabilidade e a padronização dos dados.

Funcionalidade de Zoom: Usando os atalhos Ctrl + / Ctrl - ou a roda do mouse com Ctrl, o usuário pode aumentar e diminuir o tamanho da fonte de toda a aplicação, melhorando a acessibilidade.

---
## 📚 Documentação Oficial

Para aprofundar os estudos nas tecnologias utilizadas neste projeto, consulte as documentações oficiais:

* [**Python**](https://docs.python.org/3/): A documentação completa da linguagem Python.
* [**Tkinter**](https://docs.python.org/3/library/tkinter.html): Documentação oficial da biblioteca para interfaces gráficas.
* [**SQLite**](https://www.sqlite.org/docs.html): Documentação oficial do banco de dados SQLite.
* [**Requests**](https://requests.readthedocs.io/en/latest/): Guia do usuário da biblioteca `requests`.
* [**Módulo `csv`**](https://docs.python.org/3/library/csv.html): Documentação do módulo Python para manipulação de arquivos CSV.
* [**Módulo `re`**](https://docs.python.org/3/library/re.html): Guia do módulo de Expressões Regulares do Python.

---
### 📂 Estrutura dos Arquivos

<pre>
📁 sistema-cadastro-livraria/
├── 📄 clientes.py             # Arquivo principal com todo o código Python da aplicação
├── 📄 clientes_livraria.db    # Banco de dados SQLite. É criado e atualizado pelo programa
├── 📄 README.md               # Resumo do projeto (você pode criar este)
├── 📄 imagens_execucao        # Imagens do app em execução e do banco de dados. 
└── 📄 Documentacao.md         # Este arquivo que você está lendo
</pre>
