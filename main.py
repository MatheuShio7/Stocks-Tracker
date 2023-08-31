from tkinter import *
from tkinter import ttk
from tkcalendar import * 
from PIL import ImageTk, Image
import sqlite3

window = Tk()

class Functions():
    #função para limpar os campos
    def clean_stocks_entries(self): 
        self.ticker_entry.delete(0, END)
        self.amount_entry.delete(0, END)
        self.amount_entry.insert(END, 0)
        self.comment_entry.delete(0, END)

        self.frame_comments.place_forget()
        self.earning_history_text.place_forget()
        self.date_text.place_forget()
        self.value_text.place_forget()
        self.rs_text.place_forget()
        self.date_entry.place_forget()
        self.value_entry.place_forget()
        self.new_earning_history_button.place_forget()
        self.clean_earning_history_button.place_forget()
        self.delete_earning_history_button.place_forget()
        self.update_earning_history_button.place_forget()

        self.show_eh_table()


    def clean_earnings_history_entries(self):
        self.date_entry.config(state="normal")
        self.date_entry.delete(0, END)
        self.value_entry.delete(0, END)
    

    #função para se conectar ao banco de dados
    def bd_connect(self): 
        self.connect = sqlite3.connect('stocks_tracker.db')
        self.cursor = self.connect.cursor()
    

    #função para se desconectar do banco de dados
    def bd_disconnect(self): 
        self.connect.close()


    #função para criar as tabelas
    def create_tables(self):
        self.bd_connect()
        self.cursor.execute("""
            create table if not exists ticker_amount (
                ticker text not null check (length(ticker) <= 6),
                amount int not null,
                primary key (ticker)
            );""")
        
        self.cursor.execute("""
            create table if not exists comments (
                ticker text not null,
                comment text,
                foreign key (ticker) references ticker_amount (ticker)
            );""")

        self.cursor.execute("""
            create table if not exists earning_history (
                ticker text no null,
                date date not null,
                value float not null,
                foreign key (ticker) references ticker_amount (ticker)  
            );""")
        
        self.connect.commit()  
        self.bd_disconnect()


    def register_stock(self):
        self.ticker = self.ticker_entry.get().upper().strip()
        self.amount = self.amount_entry.get()

        if not self.ticker: #verificar se algum ticker foi digitado, impossibilitando a criação de registros sem ticker
            return
        
        try: #verificar se o campo qauntidade está recebendo um valor inteiro
            int_amount = int(self.amount)
        except ValueError:
            return

        self.bd_connect()
        try:
            self.cursor.execute("""insert into ticker_amount (ticker, amount)
                values (?, ?)""", (self.ticker, self.amount))
            self.connect.commit()
        except Exception as e:
            self.connect.rollback()
            print(f'Erro ao inserir: {e}')
        finally:
            self.bd_disconnect()

        self.show_table1()


    def show_table1(self):
        self.ticker_amount_table.delete(*self.ticker_amount_table.get_children())
        self.bd_connect()
        table1 = self.cursor.execute(""" select ticker, amount from ticker_amount; """)
        for i in table1:
            self.ticker_amount_table.insert('', END, values=i)
        self.bd_disconnect()


    def show_comments_table(self):
        self.ticker = self.ticker_entry.get()
        self.comments_table.delete(*self.comments_table.get_children())
        self.bd_connect()
        table2 = self.cursor.execute(""" select comment from comments where ticker = ?""", (self.ticker,))
        for c in table2:
            self.comments_table.insert('', END, values=c)
        self.bd_disconnect()


    def register_comments(self):
        self.ticker = self.ticker_entry.get().upper()
        self.comment = self.comment_entry.get()

        self.bd_connect()
        self.cursor.execute(""" insert into comments (ticker, comment)
            values (?, ?)""", (self.ticker, self.comment))
        
        self.connect.commit()
        self.bd_disconnect()


    def combined_function(self):
        self.register_stock()
        self.register_comments()
        self.clean_stocks_entries()


    def on_double_click(self, event):
        self.clean_earnings_history_entries()
        self.clean_stocks_entries()
        self.amount_entry.delete(0, END)
        selected_stock = self.ticker_amount_table.selection()
        self.old_ticker = self.ticker_entry.get()

        if selected_stock:  
            col1, col2 = self.ticker_amount_table.item(selected_stock[0], 'values')
            self.ticker_entry.insert(END, col1)
            self.amount_entry.insert(END, col2)

            comment = self.fetch_comment_from_database(col1)  
            self.comment_entry.delete(0, END)
            self.comment_entry.insert(END, comment)

            self.bd_connect()

            self.frame_comments.place(relx=0.3, rely=0.6, relwidth=0.2, relheight=0.35)
            self.earning_history_text.place(relx=0.76,rely=0.61, relwidth=0.15, relheight=0.025)
            self.date_text.place(relx=0.76,rely=0.65, relwidth=0.05, relheight=0.025)
            self.value_text.place(relx=0.762,rely=0.715, relwidth=0.05, relheight=0.025)
            self.rs_text.place(relx=0.76, rely=0.74, relwidth=0.05, relheight=0.025)
            self.date_entry.place(relx=0.77555,rely=0.675,relwidth=0.05,relheight=0.025)
            self.value_entry.place(relx=0.792,rely=0.74,relwidth=0.05,relheight=0.025)
            self.new_earning_history_button.place(relx=0.76,rely=0.79,relwidth=0.05,relheight=0.03)
            self.clean_earning_history_button.place(relx=0.88,rely=0.79,relwidth=0.05,relheight=0.03)
            self.delete_earning_history_button.place(relx=0.82,rely=0.79,relwidth=0.05,relheight=0.03)
            self.update_earning_history_button.place(relx=0.94,rely=0.79,relwidth=0.05,relheight=0.03)
            
            self.show_comments_table()  

            self.earning_history_table.delete(*self.earning_history_table.get_children())
            
            self.bd_connect()
            selected_table = self.cursor.execute("""select ticker, date, value from earning_history where ticker = ? order by date desc""", (col1,))
            for s in selected_table:
                self.earning_history_table.insert('', END, values=s)
            self.bd_disconnect()


    def fetch_comment_from_database(self, ticker):
        self.bd_connect()
        query = "SELECT comment FROM comments WHERE ticker = ?"
        self.cursor.execute(query, (ticker,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return ""


    def delete_stock(self):
        self.ticker = self.ticker_entry.get().upper()
        self.amount = self.amount_entry.get()
        self.comment = self.comment_entry.get()

        self.bd_connect()
        self.cursor.execute(""" delete from comments where ticker = ?""", (self.ticker,))
        self.cursor.execute(""" delete from ticker_amount where ticker = ?""", (self.ticker,))
        self.connect.commit()

        self.frame_comments.place_forget()
        self.earning_history_text.place_forget()
        self.date_text.place_forget()
        self.value_text.place_forget()
        self.rs_text.place_forget()
        self.date_entry.place_forget()
        self.value_entry.place_forget()
        self.new_earning_history_button.place_forget()
        self.clean_earning_history_button.place_forget()
        self.delete_earning_history_button.place_forget()
        self.update_earning_history_button.place_forget()

        self.bd_disconnect()
        self.clean_stocks_entries()
        self.show_table1()
        self.show_eh_table()
    

    def update_info(self):
        self.ticker = self.ticker_entry.get()
        self.amount = self.amount_entry.get()
        self.comment = self.comment_entry.get()
        self.bd_connect()

        self.cursor.execute(""" update ticker_amount set ticker = ? where ticker = ?""", (self.ticker, self.old_ticker))
        self.cursor.execute(""" update ticker_amount set amount = ? where ticker = ?""", (self.amount, self.ticker))
        self.cursor.execute(""" update comments set ticker = ?, comment = ? where ticker = ?""", (self.ticker, self.comment, self.ticker))

        self.connect.commit()
        self.bd_disconnect()
        self.show_table1()
        self.show_comments_table()


    def add_eh(self):
        self.ticker = self.ticker_entry.get()
        self.date = self.date_entry.get()
        self.value = self.value_entry.get().strip()

        if not self.value:
            return  
        
        try:
            float_value = float(self.value)
        except ValueError:
            return

        self.bd_connect()
        self.cursor.execute(""" insert into earning_history (ticker, date, value) values (?, ?, ?)""", (self.ticker, self.date, self.value))

        self.connect.commit()
        self.bd_disconnect()

        self.earning_history_table.delete(*self.earning_history_table.get_children())  
        self.bd_connect()
        eh_table = self.cursor.execute(""" select ticker, date, value from earning_history where ticker = ? order by date desc; """, (self.ticker,))
        for e in eh_table:
            self.earning_history_table.insert('', END, values=e)
        self.bd_disconnect()
        self.clean_earnings_history_entries()


    def show_eh_table(self):
        self.earning_history_table.delete(*self.earning_history_table.get_children())  
        self.bd_connect()
        eh_table = self.cursor.execute(""" select ticker, date, value from earning_history order by date desc; """)
        for e in eh_table:
            self.earning_history_table.insert('', END, values=e)
        self.bd_disconnect()


    def double_click_eh(self, event):
        self.clean_earnings_history_entries()
        self.date_entry.delete(0, END)
        self.value_entry.delete(0, END)
        selected_eh = self.earning_history_table.selection()

        if selected_eh:
            col1, col2, col3 = self.earning_history_table.item(selected_eh[0], 'values')
            self.value_entry.insert(END, col3)
            self.date_entry.insert(END, col2)

        self.earning_history_text.place(relx=0.76,rely=0.61, relwidth=0.15, relheight=0.025)
        self.date_text.place(relx=0.76,rely=0.65, relwidth=0.05, relheight=0.025)
        self.value_text.place(relx=0.762,rely=0.715, relwidth=0.05, relheight=0.025)
        self.rs_text.place(relx=0.76, rely=0.74, relwidth=0.05, relheight=0.025)
        self.date_entry.place(relx=0.77555,rely=0.675,relwidth=0.05,relheight=0.025)
        self.value_entry.place(relx=0.792,rely=0.74,relwidth=0.05,relheight=0.025)
        self.new_earning_history_button.place(relx=0.76,rely=0.79,relwidth=0.05,relheight=0.03)
        self.clean_earning_history_button.place(relx=0.88,rely=0.79,relwidth=0.05,relheight=0.03)
        self.delete_earning_history_button.place(relx=0.82,rely=0.79,relwidth=0.05,relheight=0.03)
        self.update_earning_history_button.place(relx=0.94,rely=0.79,relwidth=0.05,relheight=0.03)

        self.old_date = self.date_entry.get()
        self.old_value = self.value_entry.get()


    def delete_eh(self):
        self.data = self.date_entry.get()
        self.value = self.value_entry.get()

        self.bd_connect()
        self.cursor.execute("""delete from earning_history where rowid in (select rowid from earning_history where date = ? and value = ? limit 1)""", (self.data, self.value))
        self.connect.commit()
        self.bd_disconnect()
        
        self.clean_earnings_history_entries()
        self.show_eh_table()


    def update_eh(self):
        self.data = self.date_entry.get()
        self.value = self.value_entry.get()

        self.bd_connect()
        self.cursor.execute("""update earning_history set date = ? where date = ? and value = ?""", (self.data, self.old_date, self.old_value))
        self.cursor.execute("""update earning_history set value = ? where date = ? and value = ?""", (self.value, self.old_date, self.old_value))
        self.connect.commit()
        self.bd_disconnect()

        self.show_eh_table()
        self.clean_earnings_history_entries() 


class Aplication(Functions):
    def __init__(self):
        self.window = window
        self.screen_settings()
        self.images()
        self.frames()
        self.buttons()
        self.texts()
        self.entries()
        self.ticker_aumont_table()
        self.comments_table()
        self.earning_history_table()
        self.create_tables()
        self.show_table1()
        self.show_eh_table()
        window.mainloop()
    

    def screen_settings(self):
        self.window.title('Stocks Tracker') 
        self.window.iconbitmap('lírio_icon.ico')
        self.window.configure(background= '#880808') #cor de fundo
        self.window.geometry('1920x1080') #dimensões da tela 
        self.window.state('zoomed')
        self.window.resizable(True, True) #possibilidade de redimensionar a tela


    def images(self):
        spider = Image.open("spider.png")
        self.spider_img = ImageTk.PhotoImage(spider)
        self.spider_label = Label(self.window, image=self.spider_img, highlightbackground='#880808')
        self.spider_label.place(relx=0.105, rely=0.15, relwidth=0.3, relheight=0.7)


    def frames(self):
        self.frame_tabela_ticker_amount = Frame(self.window, highlightbackground='black', highlightthickness=4)
        self.frame_tabela_ticker_amount.place(relx=0.3, rely=0.05, relwidth=0.2, relheight=0.5)

        self.frame_comments = Frame(self.window, highlightbackground='black', highlightthickness=4)
        self.frame_comments.place_forget()

        self.frame_graphic = Frame(self.window, highlightbackground='black', highlightthickness=4)
        self.frame_graphic.place(relx=0.527, rely=0.05, relwidth=0.45, relheight=0.5)

        self.frame_earning_history = Frame(self.window, highlightbackground='black', highlightthickness=4)
        self.frame_earning_history.place(relx=0.55,rely=0.6,relwidth=0.2,relheight=0.35)


    def buttons(self):
        #botões do cadastro das ações
        self.new_button = Button(self.window, text='+', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'), command = self.combined_function)
        self.new_button.place(relx=0.02,rely=0.46,relwidth=0.05,relheight=0.03)

        self.clean_button = Button(self.window, text='Limpar', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'), command = self.clean_stocks_entries)
        self.clean_button.place(relx=0.16,rely=0.46,relwidth=0.05,relheight=0.03)

        self.delete_button = Button(self.window, text='-', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'), command = self.delete_stock)
        self.delete_button.place(relx=0.09,rely=0.46,relwidth=0.05,relheight=0.03)

        self.update_button = Button(self.window, text='Atualizar', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'), command = self.update_info)
        self.update_button.place(relx=0.23,rely=0.46,relwidth=0.05,relheight=0.03)

        #botões do cadastro do histórico de proventos
        self.new_earning_history_button = Button(self.window, text='+', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'), command = self.add_eh)

        self.clean_earning_history_button = Button(self.window, text='Limpar', bg='#800020', fg='white', bd=3, 
                                   font=('garamond', 11, 'bold'), command=self.clean_earnings_history_entries)

        self.delete_earning_history_button = Button(self.window, text='-', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'), command=self.delete_eh)

        self.update_earning_history_button = Button(self.window, text='Atualizar', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'), command=self.update_eh)


    def texts(self):
        self.ticker_text = Label(self.window, text='Ticker', bg='#880808',fg='white', font=('garamond', 13, 'bold'))
        self.ticker_text.place(relx=0.008,rely=0.255, relwidth=0.05, relheight=0.025)

        self.amount_text = Label(self.window, text='Quantidade', bg='#880808',fg='white', font=('garamond', 13, 'bold'))
        self.amount_text.place(relx=0.018,rely=0.32, relwidth=0.05, relheight=0.025)

        self.comments_text = Label(self.window, text='Descrição', bg='#880808',fg='white', font=('garamond', 13, 'bold'))
        self.comments_text.place(relx=0.016,rely=0.385, relwidth=0.05, relheight=0.025)

        self.date_text = Label(self.window, text='Data', bg='#880808',fg='white', font=('garamond', 13, 'bold'))

        self.value_text = Label(self.window, text='Valor', bg='#880808',fg='white', font=('garamond', 13, 'bold'))

        self.rs_text = Label(self.window, text='R$', bg='#880808',fg='white', font=('garamond', 13, 'bold'))

        self.earning_history_text = Label(self.window, text='Histórico de Proventos', bg='#880808',fg='white', font=('garamond', 17, 'bold'))


    def entries(self):
        
        self.ticker_entry = Entry(self.window, font=('garamond', 13))
        self.ticker_entry.place(relx=0.02,rely=0.28,relwidth=0.05,relheight=0.025)


        self.amount_entry = Spinbox(self.window, from_=0, to=100000000000000, font=('garamond', 13))
        self.amount_entry.place(relx=0.02,rely=0.345,relwidth=0.05,relheight=0.025)

        self.comment_entry = Entry(self.window, font=('garamond', 13))
        self.comment_entry.place(relx=0.02,rely=0.41,relwidth=0.26,relheight=0.025)

        self.date_entry = Entry(self.window, font=('garamond', 13))
        self.date_entry.bind('<1>', self.pick_date)

        self.value_entry = Entry(self.window, font=('garamond', 13))


    def pick_date(self, event):
        self.date_window = Toplevel()
        self.date_window.grab_set()
        self.date_window.title('Choose The Date')
        self.date_window.geometry('250x220+590+370')
        self.calendar = Calendar(self.date_window, selectmode='day', date_pattern='y/mm/dd')
        self.calendar.place(x=0, y=0)
        
        self.submit_btn = Button(self.date_window, text='Selecionar', command=self.update_date)
        self.submit_btn.place(x=94, y=190)
        self.date_entry.config(fg='black')


    def update_date(self):
        selected_date = self.calendar.get_date()
        self.date_entry.config(state="normal")
        self.date_entry.delete(0, END)
        self.date_entry.insert(0, selected_date)
        self.date_entry.config(state="readonly")
        self.date_window.destroy()
        

    def ticker_aumont_table(self):
        self.ticker_amount_table = ttk.Treeview(self.frame_tabela_ticker_amount, height= 3, columns=('column1', 'column2'))
        self.ticker_amount_table.configure(height=5, show='headings')
        self.ticker_amount_table.heading('#1', text='Ticker')
        self.ticker_amount_table.heading('#2', text='Quantidade')

        self.ticker_amount_table.column('#1', width=10)
        self.ticker_amount_table.column('#2', width=10)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("garamond", 12, "bold"))
        style.configure('Treeview', font=('garamond', 12))
        self.ticker_amount_table.place(relx=0,rely=0,relwidth=0.95,relheight=1)

        self.scrool_ticker_amount_table = Scrollbar(self.frame_tabela_ticker_amount, orient='vertical')
        self.ticker_amount_table.configure(yscroll=self.scrool_ticker_amount_table.set)
        self.scrool_ticker_amount_table.place(relx=0.94, rely=0.001, relwidth=0.06, relheight=0.9999)

        self.ticker_amount_table.bind('<Double-1>', self.on_double_click)


    def comments_table(self):
        self.comments_table = ttk.Treeview(self.frame_comments, height=3, columns=('column1'))
        self.comments_table.configure(height=5, show='headings')
        self.comments_table.heading('#1', text='Descrição')

        self.comments_table.column('#1', width=10)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("garamond", 12, "bold"))
        self.comments_table.place(relx=0, rely=0, relwidth=0.95, relheight=1)

        self.scrool_comments_table = Scrollbar(self.frame_comments, orient='vertical')
        self.comments_table.configure(yscroll=self.scrool_comments_table.set)
        self.scrool_comments_table.place(relx=0.94, rely=0.001, relwidth=0.06, relheight=0.9999)


    def earning_history_table(self):
        self.earning_history_table = ttk.Treeview(self.frame_earning_history, height=3, columns=('column1', 'column2', 'column3'))
        self.earning_history_table.configure(height=5, show='headings')
        self.earning_history_table.heading('#1', text='Ticker')
        self.earning_history_table.heading('#2', text='Data')
        self.earning_history_table.heading('#3', text='Valor')

        self.earning_history_table.column('#1', width=10)
        self.earning_history_table.column('#2', width=10)
        self.earning_history_table.column('#3', width=10)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("garamond", 12, "bold"))
        self.earning_history_table.place(relx=0,rely=0,relwidth=0.95,relheight=1)

        self.scrool_earning_history_table = Scrollbar(self.frame_earning_history, orient='vertical')
        self.earning_history_table.configure(yscroll=self.scrool_earning_history_table.set)
        self.scrool_earning_history_table.place(relx=0.94, rely=0.001, relwidth=0.06, relheight=0.9999)

        self.earning_history_table.bind('<Double-1>', self.double_click_eh)

Aplication()