# ===================================================
# 1. IMPORTAÇÕES
# ===================================================
import sqlite3                    # Importa o módulo para trabalhar com banco de dados SQLite
import csv                        # Importa o módulo para manipular arquivos CSV 
import re                         # Importa o módulo de expressões regulares, útil para validações
from tkinter import *             # Importa todos os componentes da biblioteca Tkinter para a interface gráfica
from tkinter import messagebox    # Importa caixas de mensagens como showinfo, showerror, etc.
from tkinter import ttk           # Importa o módulo ttk, que fornece widgets mais modernos para o Tkinter
from tkinter import filedialog    # Importa o módulo para abrir janelas de diálogo de arquivos (abrir/salvar)
import requests                   # Importa a biblioteca requests para fazer requisições HTTP (APIs)
import json                       # Importa o módulo json para trabalhar com dados no formato JSON
from datetime import datetime     # Importa a classe datetime para manipulação de datas
# ===================================================
# 2. FUNÇÕES AUXILIARES E BANCO DE DADOS
# ===================================================

def buscar_estados_e_cidades(): # Busca os estados e suas respectivas cidades da API pública do IBGE.
    print("Buscando dados de estados e cidades... Isso pode levar um momento.")
    try:
        url_estados = "https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome" # URL da API do IBGE para obter todos os estados do Brasil, ordenados por nome
        response_estados = requests.get(url_estados, timeout=10)  # Faz a requisição HTTP GET para obter os estados
        response_estados.raise_for_status() # Lança exceção se houver erro na resposta
        estados = response_estados.json()  # Converte a resposta JSON em lista de estados
        dados_completos = {}  # Dicionário para armazenar os estados e suas cidades
        for estado in estados: # Para cada estado, busca suas cidades (municípios)
            uf = estado['sigla']
            url_municipios = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
            response_municipios = requests.get(url_municipios, timeout=10)
            response_municipios.raise_for_status()
            municipios = response_municipios.json()
            dados_completos[uf] = sorted([m['nome'] for m in municipios]) # Armazena a lista de nomes de cidades (ordenadas) no dicionário usando a sigla do estado como chave
        print("Dados de localização carregados com sucesso!")
        return dados_completos
    except requests.exceptions.RequestException as e: # Em caso de falha de rede ou API, exibe erro e retorna um dicionário com dados mínimos locais
        messagebox.showerror("Erro de Rede", f"Não foi possível buscar a lista de cidades e estados.\nVerifique sua conexão com a internet.\nUsando dados locais mínimos.\n\nErro: {e}")
        return {"SP": ["São Paulo", "Campinas", "Guarulhos"], "RJ": ["Rio de Janeiro", "Niterói", "Duque de Caxias"], "MG": ["Belo Horizonte", "Uberlândia"], "AL": ["Maceió", "Arapiraca"]}


def conectar_banco(): # Conecta ao banco de dados e garante que as tabelas 'clientes' e 'vendas' existam.
    conexao = sqlite3.connect("clientes_livraria.db") # Conecta (ou cria) o banco de dados SQLite chamado 'clientes_livraria.db'
    cursor = conexao.cursor()  # Cria um cursor para executar comandos SQL
    # Cria a tabela 'clientes' caso ainda não exista:
    cursor.execute("""      
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telefone TEXT NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL
        )
    """)
    # Cria a tabela 'vendas' caso ainda não exista
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            livro_titulo TEXT NOT NULL,
            livro_autor TEXT NOT NULL,
            genero TEXT NOT NULL,
            data_compra DATE NOT NULL,
            valor_total REAL NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
        )
    """)
    conexao.commit() # Confirma as alterações no banco
    return conexao

# ===================================================
# 3. CLASSE PRINCIPAL DA APLICAÇÃO
# ===================================================
class Aplicacao:
    def __init__(self):
        # Conecta ao banco de dados e cria um cursor para execução de comandos SQL
        self.conexao = conectar_banco() 
        self.cursor = self.conexao.cursor()
        # Carrega os dados de localização (estados e cidades) a partir da API do IBGE
        self.dados_localizacao = buscar_estados_e_cidades()
        # Cria a janela principal da aplicação com título, tamanho e cor de fundo personalizados
        self.janela = Tk()
        self.janela.title("Cadastro de Clientes e Vendas: Livraria")
        self.janela.geometry("850x650")
        self.janela.configure(bg="#f0f7f4")
        self.id_cliente_selecionado = None # Inicializa o ID do cliente selecionado (usado para atualização/exclusão)
        self.font_size = 10
        self.frames() # Chama os métodos para criar os frames da interface
        # Adiciona os widgets (campos, labels, botões) ao primeiro e segundo frame
        self.widgets_frame1()
        self.widgets_frame2()
        # Carrega os dados dos clientes existentes do banco para a interface
        self.carregar_clientes()
        # Lista de widgets que serão afetados pelas funções de zoom (aumentar/reduzir fontes)
        self.widgets_para_zoom = [
            self.lbl_nome, self.lbl_email, self.lbl_telefone, self.lbl_estado, self.lbl_cidade,
            self.entry_nome, self.entry_email, self.entry_telefone,
            self.combo_estado, self.combo_cidade,
            self.btn_cadastrar, self.btn_limpar, self.btn_atualizar,
            self.btn_excluir, self.btn_limpar_todos, self.btn_exportar, self.btn_ver_compras
        ]
        self.style = ttk.Style() # Configura o estilo padrão do ttk
        self.atualizar_fontes() # Aplica o tamanho de fonte definido aos widgets
        # Ligações de teclas para facilitar a navegação nos campos:
        self.entry_nome.bind("<Return>", lambda e: self.entry_email.focus())
        self.entry_email.bind("<Return>", lambda e: self.entry_telefone.focus())
        self.entry_telefone.bind("<Return>", lambda e: self.combo_estado.focus())
        # Ligações de atalhos para funcionalidades adicionais:
        self.janela.bind("<Escape>", lambda e: self.limpar_campos())
        self.janela.bind("<Control-plus>", self.aumentar_zoom)
        self.janela.bind("<Control-minus>", self.diminuir_zoom)
        self.janela.bind("<Control-MouseWheel>", self.zoom_com_roda)
        # Inicia o loop principal da interface gráfica:
        self.janela.mainloop()

    # --- Métodos de construção da interface ---
    def frames(self):
        # Cria o frame superior (frame_1) que conterá os campos de cadastro:
        self.frame_1 = Frame(self.janela, bd=4, bg="#dbeadf", highlightbackground="#a8c3bc", highlightthickness=2)
        self.frame_1.place(relx=0.02, rely=0.02, relheight=0.44, relwidth=0.96)
        # Cria o frame inferior (frame_2) que conterá a lista de clientes e botões de ação:
        self.frame_2 = Frame(self.janela, bd=4, bg="#e6f2f1", highlightbackground="#a0b9c6", highlightthickness=2)
        self.frame_2.place(relx=0.02, rely=0.48, relheight=0.48, relwidth=0.96)

    def widgets_frame1(self):
        # Campo de entrada para o nome do cliente:
        self.lbl_nome = Label(self.frame_1, text="Nome:", bg="#dbeadf"); self.lbl_nome.place(x=10, y=20)
        self.entry_nome = Entry(self.frame_1, width=50); self.entry_nome.place(x=100, y=20)
        # Campo de entrada para o email:
        self.lbl_email = Label(self.frame_1, text="E-mail:", bg="#dbeadf"); self.lbl_email.place(x=10, y=60)
        self.entry_email = Entry(self.frame_1, width=50); self.entry_email.place(x=100, y=60)
        # Campo de entrada para o telefone com máscara e dicas de formatação:
        self.lbl_telefone = Label(self.frame_1, text="Telefone:", bg="#dbeadf"); self.lbl_telefone.place(x=10, y=100)
        self.entry_telefone = Entry(self.frame_1, width=20, fg='grey'); self.entry_telefone.place(x=100, y=100)
        self.entry_telefone.insert(0, '(DD) XXXXX-XXXX'); self.entry_telefone.bind('<FocusIn>', self.on_telefone_focus_in)
        self.entry_telefone.bind('<FocusOut>', self.on_telefone_focus_out); self.entry_telefone.bind('<KeyRelease>', self.formatar_telefone_mask)
        # Combobox para seleção do estado:
        self.lbl_estado = Label(self.frame_1, text="Estado:", bg="#dbeadf"); self.lbl_estado.place(x=10, y=140)
        self.combo_estado = ttk.Combobox(self.frame_1, values=list(self.dados_localizacao.keys())); self.combo_estado.place(x=100, y=140)
        self.combo_estado.bind("<<ComboboxSelected>>", self.atualizar_cidades)
        # Combobox para seleção da cidade, desabilitada até seleção do estado:
        self.lbl_cidade = Label(self.frame_1, text="Cidade:", bg="#dbeadf"); self.lbl_cidade.place(x=300, y=140)
        self.combo_cidade = ttk.Combobox(self.frame_1, width=30, state='disabled'); self.combo_cidade.place(x=370, y=140)
        # Botões de ação: cadastrar, limpar campos e atualizar cliente:
        self.btn_cadastrar = Button(self.frame_1, text="Cadastrar", command=self.cadastrar_cliente, bg="#a8d5ba"); self.btn_cadastrar.place(x=10, y=200)
        self.btn_limpar = Button(self.frame_1, text="Limpar Campos", command=self.limpar_campos, bg="#f7c6a3"); self.btn_limpar.place(x=100, y=200)
        self.btn_atualizar = Button(self.frame_1, text="Atualizar", command=self.atualizar_cliente, bg="#a3d1f7"); self.btn_atualizar.place(x=215, y=200)

    def widgets_frame2(self):
        # Cria a tabela Treeview para exibir os clientes com colunas personalizadas:
        self.lista_clientes = ttk.Treeview(self.frame_2, columns=("id", "nome", "email", "telefone", "cidade", "estado"), show='headings')
        # Define cabeçalhos e largura das colunas:
        self.lista_clientes.heading("id", text="ID"); self.lista_clientes.column("id", width=40, anchor="center")
        self.lista_clientes.heading("nome", text="Nome"); self.lista_clientes.column("nome", width=150)
        self.lista_clientes.heading("email", text="Email"); self.lista_clientes.column("email", width=200)
        self.lista_clientes.heading("telefone", text="Telefone"); self.lista_clientes.column("telefone", width=110)
        self.lista_clientes.heading("cidade", text="Cidade"); self.lista_clientes.column("cidade", width=120)
        self.lista_clientes.heading("estado", text="UF"); self.lista_clientes.column("estado", width=50, anchor="center")
        # Posiciona a tabela no frame com altura e largura relativas:
        self.lista_clientes.place(relx=0, rely=0, relwidth=0.97, relheight=0.8)
        # Permite editar cliente ao clicar duas vezes na linha:
        self.lista_clientes.bind("<Double-1>", self.carregar_cliente_para_edicao)
        # Adiciona barra de rolagem vertical à tabela:
        scrollbar = Scrollbar(self.frame_2, orient="vertical", command=self.lista_clientes.yview)
        self.lista_clientes.configure(yscrollcommand=scrollbar.set); scrollbar.place(relx=0.97, rely=0, relheight=0.8)
        # Botões de ações adicionais abaixo da tabela:
        self.btn_excluir = Button(self.frame_2, text="Excluir Selecionado", command=self.excluir_cliente, bg="#f6d1a5"); self.btn_excluir.place(relx=0.01, rely=0.83)
        self.btn_limpar_todos = Button(self.frame_2, text="Limpar Todos", command=self.limpar_tabela, bg="#f6a5a5"); self.btn_limpar_todos.place(relx=0.20, rely=0.83)
        self.btn_exportar = Button(self.frame_2, text="Exportar para CSV", command=self.exportar_para_csv, bg="#b3f6a5"); self.btn_exportar.place(relx=0.35, rely=0.83)
        self.btn_ver_compras = Button(self.frame_2, text="Ver/Adicionar Compras", command=self.abrir_janela_compras, bg="#a5c4f6"); self.btn_ver_compras.place(relx=0.53, rely=0.83)

    # --- 4. FUNÇÕES DE EVENTOS E VALIDAÇÕES ---
    def on_telefone_focus_in(self, event):  # Remove o placeholder do telefone ao focar no campo
        if self.entry_telefone.get() == '(DD) XXXXX-XXXX':
            self.entry_telefone.delete(0, 'end'); self.entry_telefone.config(fg='black')

    def on_telefone_focus_out(self, event): # Restaura o placeholder do telefone ao perder o foco, se o campo estiver vazio
        if not self.entry_telefone.get():
            self.entry_telefone.insert(0, '(DD) XXXXX-XXXX'); self.entry_telefone.config(fg='grey')

    def formatar_telefone_mask(self, event): # Aplica máscara de formatação ao campo telefone enquanto o usuário digita
        texto_limpo = "".join(filter(str.isdigit, self.entry_telefone.get()))
        formatado = texto_limpo
        if len(texto_limpo) > 2: formatado = f"({texto_limpo[:2]}) {texto_limpo[2:7]}"
        if len(texto_limpo) > 7: formatado = f"({texto_limpo[:2]}) {texto_limpo[2:7]}-{texto_limpo[7:11]}"
        self.entry_telefone.delete(0, 'end'); self.entry_telefone.insert(0, formatado)
        self.entry_telefone.icursor(len(formatado))

    def atualizar_cidades(self, event): # Atualiza a lista de cidades de acordo com o estado selecionado
        estado_selecionado = self.combo_estado.get()
        if estado_selecionado in self.dados_localizacao:
            self.combo_cidade.config(state='normal'); self.combo_cidade['values'] = self.dados_localizacao[estado_selecionado]
            self.combo_cidade.set('')

    def validar_email(self, email): # Valida o formato do e-mail com regex simples
        if re.match(r"[^@]+@[^@]+\.[^@]+", email): return True
        messagebox.showerror("Erro de Validação", "Formato de e-mail inválido."); return False

    def validar_valor(self, P): # Valida a entrada de um valor numérico com vírgula opcional (para campos monetários, por exemplo)
        if P == "": return True
        if P.count(',') > 1: return False
        try: float(P.replace(',', '.', 1)); return True
        except ValueError: return False

    # --- 5. FUNÇÕES DE CRUD (Create, Read, Update, Delete) ---
    def cadastrar_cliente(self): # Insere um novo cliente no banco de dados
        nome=self.entry_nome.get().strip(); email=self.entry_email.get().strip(); telefone=self.entry_telefone.get().strip()
        estado=self.combo_estado.get(); cidade=self.combo_cidade.get()
        # Verifica se todos os campos obrigatórios foram preenchidos:
        if not all([nome, email, estado, cidade]) or telefone == '(DD) XXXXX-XXXX' or not telefone:
            messagebox.showerror("Erro", "Preencha todos os campos."); return
        if not self.validar_email(email): return
        try:
            self.cursor.execute("INSERT INTO clientes (nome, email, telefone, cidade, estado) VALUES (?, ?, ?, ?, ?)",
                                (nome, email, telefone, cidade, estado))
            self.conexao.commit(); self.limpar_campos(); self.carregar_clientes()
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso.")
        except sqlite3.IntegrityError: messagebox.showerror("Erro", f"O e-mail '{email}' já está cadastrado.")

    def carregar_clientes(self): # Carrega todos os clientes da base de dados e exibe na tabela
        for i in self.lista_clientes.get_children(): self.lista_clientes.delete(i)
        self.cursor.execute("SELECT id, nome, email, telefone, cidade, estado FROM clientes ORDER BY nome ASC")
        for row in self.cursor.fetchall(): self.lista_clientes.insert("", "end", values=row)
        self.atualizar_estado_botoes()

    def carregar_cliente_para_edicao(self, event): # Preenche os campos do formulário com os dados do cliente selecionado
        self.limpar_campos(); selecionado = self.lista_clientes.selection()
        if not selecionado: return
        item=self.lista_clientes.item(selecionado[0]); valores=item['values']
        self.id_cliente_selecionado = valores[0]
        self.entry_nome.insert(0, valores[1]); self.entry_email.insert(0, valores[2])
        self.on_telefone_focus_in(None); self.entry_telefone.insert(0, valores[3])
        estado, cidade = valores[5], valores[4]
        self.combo_estado.set(estado); self.atualizar_cidades(None); self.combo_cidade.set(cidade)

    def atualizar_cliente(self): # Atualiza os dados do cliente selecionado
        if self.id_cliente_selecionado is None:
            messagebox.showwarning("Aviso", "Para atualizar, primeiro dê um duplo-clique no cliente desejado na lista."); return
        nome=self.entry_nome.get().strip(); email=self.entry_email.get().strip()
        telefone=self.entry_telefone.get().strip(); estado=self.combo_estado.get(); cidade=self.combo_cidade.get()
        if not all([nome, email, estado, cidade]) or telefone == '(DD) XXXXX-XXXX' or not telefone:
            messagebox.showerror("Erro", "Preencha todos os campos."); return
        if not self.validar_email(email): return
        try:
            self.cursor.execute("UPDATE clientes SET nome=?, email=?, telefone=?, cidade=?, estado=? WHERE id=?",
                                (nome, email, telefone, cidade, estado, self.id_cliente_selecionado))
            self.conexao.commit(); self.limpar_campos(); self.carregar_clientes()
            messagebox.showinfo("Sucesso", "Cadastro atualizado com sucesso.")
        except sqlite3.IntegrityError: messagebox.showerror("Erro", f"O e-mail '{email}' já pertence a outro cliente.")

    def excluir_cliente(self, event=None): # Exclui o cliente selecionado e suas compras
        selecionado = self.lista_clientes.selection()
        if not selecionado: messagebox.showwarning("Aviso", "Selecione um cliente para excluir."); return
        item = self.lista_clientes.item(selecionado[0]); cliente_id, cliente_nome = item["values"][0], item["values"][1]
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir '{cliente_nome}'?\nTodas as suas compras também serão apagadas."):
            self.cursor.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
            self.conexao.commit(); self.carregar_clientes(); self.limpar_campos()
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso.")

    def limpar_tabela(self): # Exclui todos os clientes e registros de compras
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja apagar TODOS os clientes e seus históricos de compra?"):
            self.cursor.execute("DELETE FROM clientes"); self.cursor.execute("DELETE FROM vendas")
            self.conexao.commit(); self.carregar_clientes(); self.limpar_campos()
            messagebox.showinfo("Limpou", "Todos os dados foram removidos.")

    def limpar_campos(self): # Limpa os campos do formulário e reseta o estado do formulário
        self.id_cliente_selecionado = None; self.entry_nome.delete(0, END); self.entry_email.delete(0, END)
        self.entry_telefone.delete(0, END); self.on_telefone_focus_out(None); self.combo_estado.set('')
        self.combo_cidade.set(''); self.combo_cidade.config(state='disabled'); self.entry_nome.focus()

    def atualizar_estado_botoes(self, event=None): # Habilita ou desabilita botões conforme presença de clientes na tabela
        tem_clientes = len(self.lista_clientes.get_children()) > 0
        self.btn_limpar_todos['state'] = 'normal' if tem_clientes else 'disabled'
        self.btn_exportar['state'] = 'normal' if tem_clientes else 'disabled'

# --- 6. FUNÇÃO DA JANELA DE COMPRAS ---
    def abrir_janela_compras(self):
        selecionado = self.lista_clientes.selection() # Obtém a seleção atual na lista de clientes

        if not selecionado: # Se nenhum cliente estiver selecionado, exibe um aviso e encerra a função
            messagebox.showwarning("Aviso", "Selecione um cliente para ver ou adicionar compras.")
            return
        # Obtém os dados do cliente selecionado (ID e Nome):
        item = self.lista_clientes.item(selecionado[0])
        cliente_id, cliente_nome = item['values'][0], item['values'][1]
    
        janela_compra = Toplevel(self.janela) # Toplevel cria uma nova janela acima da principal
        janela_compra.title(f"Compras de {cliente_nome}")
        janela_compra.geometry("800x550")
        janela_compra.configure(bg="#f0f7f4")
        janela_compra.transient(self.janela)
        janela_compra.focus_force()
        janela_compra.grab_set()

        # Variável que será usada pelo 'nonlocal'
        id_compra_selecionada = None

        # ========== FRAME DE CADASTRO ==========
        frame_cad = Frame(janela_compra, bd=2, bg="#dbeadf", relief="groove")
        frame_cad.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.45)

        Label(frame_cad, text="Título do Livro:", bg="#dbeadf").place(x=10, y=20)
        entry_titulo = Entry(frame_cad, width=50)
        entry_titulo.place(x=120, y=20)

        Label(frame_cad, text="Autor:", bg="#dbeadf").place(x=10, y=60)
        entry_autor = Entry(frame_cad, width=50)
        entry_autor.place(x=120, y=60)

        Label(frame_cad, text="Gênero:", bg="#dbeadf").place(x=10, y=100)
        combo_genero = ttk.Combobox(frame_cad, values=["Romance", "LGBTQIAPN+", "Suspense/Terror", "Ficção Científica", "Fantasia", "Biografia", "História", "Outro"])
        combo_genero.place(x=120, y=100)
        combo_genero.current(0)

        Label(frame_cad, text="Data da Compra:", bg="#dbeadf").place(x=10, y=140)
        entry_data = Entry(frame_cad, width=15, fg='grey')
        entry_data.place(x=120, y=140)
        entry_data.insert(0, 'DD/MM/AAAA')

        def on_data_focus_in(event, entry):
            if entry.get() == 'DD/MM/AAAA':
                entry.delete(0, 'end')
                entry.config(fg='black')

        def on_data_focus_out(event, entry):
            if not entry.get():
                entry.insert(0, 'DD/MM/AAAA')
                entry.config(fg='grey')

        entry_data.bind('<FocusIn>', lambda e: on_data_focus_in(e, entry_data))
        entry_data.bind('<FocusOut>', lambda e: on_data_focus_out(e, entry_data))

        Label(frame_cad, text="Valor Total (R$):", bg="#dbeadf").place(x=280, y=140)
        vcmd_valor = (janela_compra.register(self.validar_valor), '%P')
        entry_valor = Entry(frame_cad, width=15, validate="key", validatecommand=vcmd_valor)
        entry_valor.place(x=390, y=140)

        # ========== FUNÇÕES INTERNAS ==========

        def carregar_compras_do_cliente():
            for i in lista_compras_tv.get_children():
                lista_compras_tv.delete(i)
            self.cursor.execute("SELECT id, livro_titulo, livro_autor, genero, date(data_compra), valor_total FROM vendas WHERE cliente_id = ? ORDER BY data_compra DESC", (cliente_id,))
            for row in self.cursor.fetchall():
                data_fmt = datetime.strptime(row[4], '%Y-%m-%d').strftime('%d/%m/%Y')
                valor_fmt = f"{row[5]:.2f}".replace('.', ',')
                lista_compras_tv.insert("", "end", values=(row[0], row[1], row[2], row[3], data_fmt, valor_fmt))

        def limpar_campos():
            nonlocal id_compra_selecionada 
            id_compra_selecionada = None
            entry_titulo.delete(0, END)
            entry_autor.delete(0, END)
            entry_valor.delete(0, END)
            entry_data.delete(0, END)
            on_data_focus_out(None, entry_data) 
            combo_genero.current(0)
            btn_registrar.config(text="Registrar Compra", bg="#a8d5ba")

        def registrar_ou_atualizar():
            nonlocal id_compra_selecionada 
            titulo = entry_titulo.get().strip()
            autor = entry_autor.get().strip()
            genero = combo_genero.get()
            data_str = entry_data.get().strip()
            valor_str = entry_valor.get().strip().replace(',', '.')

            if not all([titulo, autor, genero, data_str, valor_str]) or data_str == 'DD/MM/AAAA':
                messagebox.showerror("Erro", "Preencha todos os campos da compra.", parent=janela_compra)
                return

            try:
                data_obj = datetime.strptime(data_str, '%d/%m/%Y')
                data_sql = data_obj.strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Erro de Validação", "Formato de data inválido. Use DD/MM/AAAA.", parent=janela_compra)
                return

            try:
                valor = float(valor_str)
            except ValueError:
                messagebox.showerror("Erro", "O valor total deve ser um número.", parent=janela_compra)
                return

            if id_compra_selecionada is None:
                self.cursor.execute(
                    "INSERT INTO vendas (cliente_id, livro_titulo, livro_autor, genero, data_compra, valor_total) VALUES (?, ?, ?, ?, ?, ?)",
                    (cliente_id, titulo, autor, genero, data_sql, valor)
                )
                messagebox.showinfo("Sucesso", "Compra registrada!", parent=janela_compra)
            else:
                self.cursor.execute(
                    "UPDATE vendas SET livro_titulo=?, livro_autor=?, genero=?, data_compra=?, valor_total=? WHERE id=?",
                    (titulo, autor, genero, data_sql, valor, id_compra_selecionada)
                )
                messagebox.showinfo("Sucesso", "Compra atualizada!", parent=janela_compra)

            self.conexao.commit()
            limpar_campos()
            carregar_compras_do_cliente()

        def carregar_para_edicao(event):
            nonlocal id_compra_selecionada 
            selecionado = lista_compras_tv.selection()
            if not selecionado:
                return
            item = lista_compras_tv.item(selecionado[0])['values']
            id_compra_selecionada = item[0]
            entry_titulo.delete(0, END)
            entry_titulo.insert(0, item[1])
            entry_autor.delete(0, END)
            entry_autor.insert(0, item[2])
            combo_genero.set(item[3])
            on_data_focus_in(None, entry_data) 
            entry_data.delete(0, END)
            entry_data.insert(0, item[4])
            entry_valor.delete(0, END)
            entry_valor.insert(0, str(item[5]).replace('.',',')) 
            btn_registrar.config(text="Atualizar Compra", bg="#a3d1f7")

        def finalizar_cadastro():
            if messagebox.askyesno("Finalizar", "Deseja finalizar o cadastro e fechar esta janela?", parent=janela_compra):
                janela_compra.destroy()

        # ========== BOTÕES ==========
        btn_registrar = Button(frame_cad, text="Registrar Compra", bg="#a8d5ba", command=registrar_ou_atualizar)
        btn_registrar.place(x=10, y=180)

        Button(frame_cad, text="Limpar/Cancelar Edição", bg="#f7c6a3", command=limpar_campos).place(x=150, y=180)

        # ========== LISTA DE COMPRAS ==========
        frame_lista = Frame(janela_compra, bd=2, bg="#e6f2f1", relief="groove") # Cria um frame (área) para exibir a lista de compras, com borda e cor de fundo
        frame_lista.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.40)

        lista_compras_tv = ttk.Treeview(frame_lista, columns=("id", "titulo", "autor", "genero", "data", "valor"), show='headings') # Cria o widget Treeview para exibir as compras em formato de tabela
        for col, txt, w in zip(("id", "titulo", "autor", "genero", "data", "valor"),
                               ["ID", "Título", "Autor", "Gênero", "Data", "Valor (R$)"],
                               [30, 250, 180, 100, 80, 80]): # Ajustei o último tamanho
            lista_compras_tv.heading(col, text=txt)
            lista_compras_tv.column(col, width=w, anchor="center" if col in ["id", "data", "valor"] else "w")
        
        # Adiciona a scrollbar à lista de compras
        scrollbar_compras = Scrollbar(frame_lista, orient="vertical", command=lista_compras_tv.yview) # Cria uma barra de rolagem vertical e a vincula ao Treeview
        lista_compras_tv.configure(yscrollcommand=scrollbar_compras.set)
        
        lista_compras_tv.place(relx=0.01, rely=0.01, relwidth=0.94, relheight=0.96)  # Posiciona a tabela e a scrollbar dentro do frame
        scrollbar_compras.place(relx=0.95, rely=0.01, relwidth=0.04, relheight=0.96)

        # Vincula o evento de duplo clique à função carregar_para_edicao
        # Isso permite editar um item da tabela ao dar dois cliques sobre ele
        lista_compras_tv.bind("<Double-1>", carregar_para_edicao)

        # ========== BOTÃO FINALIZAR ==========
        Button(janela_compra, text="Finalizar", bg="#c0e2ff", command=finalizar_cadastro).place(relx=0.85, rely=0.92, relwidth=0.13)

        carregar_compras_do_cliente()

    # --- 7. FUNÇÕES FINAIS (ZOOM, EXPORTAR, ETC) ---
    def exportar_para_csv(self): 
        # Abre uma janela para o usuário escolher onde salvar o arquivo:
        caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")], title="Salvar clientes como...")
        if not caminho_arquivo: return
        try:  # Abre o arquivo escolhido no modo de escrita com codificação UTF-8:
            with open(caminho_arquivo, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Nome", "Email", "Telefone", "Cidade", "Estado"])
                self.cursor.execute("SELECT id, nome, email, telefone, cidade, estado FROM clientes ORDER BY nome ASC")
                for row in self.cursor.fetchall(): writer.writerow(row)
            messagebox.showinfo("Sucesso", f"Clientes exportados com sucesso para:\n{caminho_arquivo}")
        except Exception as e: messagebox.showerror("Erro de Exportação", f"Ocorreu um erro ao salvar o arquivo:\n{e}")

    def atualizar_fontes(self):
        font_config = ("Arial", self.font_size); font_bold = ("Arial", self.font_size, "bold")
        for widget in self.widgets_para_zoom: widget.config(font=font_config)
        self.style.configure("Treeview.Heading", font=font_bold)
        self.style.configure("Treeview", font=font_config, rowheight=int(self.font_size * 2.5))
        self.style.configure("TCombobox", font=font_config)

    def aumentar_zoom(self, event=None):
        if self.font_size < 18: self.font_size += 1; self.atualizar_fontes()
    def diminuir_zoom(self, event=None):
        if self.font_size > 8: self.font_size -= 1; self.atualizar_fontes()
    def zoom_com_roda(self, event):
        if event.delta > 0: self.aumentar_zoom()
        else: self.diminuir_zoom()

# ===================================================
# 4. INICIANDO A APLICAÇÃO
# ===================================================
if __name__ == "__main__":
    Aplicacao()

