from tkinter import *
from tkinter import ttk
import sqlite3

window = Tk()

class Functions():
    #função para limpar os campos
    def clean_entries(self): 
        self.ticker_entry.delete(0, END)
        self.amount_entry.delete(0, END)
        self.comments_entry.delete(0, END)
    
    #função para se conectar ao banco de dado
    '''
    def bd_connect(self): 
        self.connect = sqlite3.connect('stocks.bd')
        self.cursor = self.connect.cursor()
    
    #função para se desconectar do banco de dado
    def bd_disconnect(self): 
        self.connect.close()

    #função para criar as tabelas
    def create_table(self):
        self.bd_connect()
        self.cursor.execute("""
            create table if not exists tracker_amount (
                            ticker not null varchar(6),
                            aumont int,
                            primary key (ticker)
            ) default charset utf8mb4;""")
    '''


class Aplication(Functions):
    def __init__(self):
        self.window = window
        self.screen_settings()
        self.frames()
        self.buttons()
        self.texts()
        self.entries()
        self.ticker_aumont_table()
        window.mainloop()
    
    def screen_settings(self):
        self.window.title('Stocks Tracker') 
        self.window.configure(background= '#880808') #cor de fundo
        self.window.geometry('1080x700') #dimensões da tela 
        self.window.resizable(True, True) #possibilidade de redimensionar a tela

    def frames(self):
        self.frame_tabela_ticker_amount = Frame(self.window, highlightbackground='black', highlightthickness=4)
        self.frame_tabela_ticker_amount.place(relx=0.3, rely=0.05, relwidth=0.2, relheight=0.5)

        self.frame_comments = Frame(self.window, highlightbackground='black', highlightthickness=4)
        self.frame_comments.place(relx=0.3, rely=0.6, relwidth=0.2, relheight=0.35)

        self.frame_graphic = Frame(self.window, highlightbackground='black', highlightthickness=4)
        self.frame_graphic.place(relx=0.527, rely=0.05, relwidth=0.45, relheight=0.5)

        self.frame_earning_history = Frame(self.window, highlightbackground='black', highlightthickness=4)
        self.frame_earning_history.place(relx=0.65,rely=0.6,relwidth=0.2,relheight=0.35)

    def buttons(self):
        self.new_button = Button(self.window, text='Add', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'))
        self.new_button.place(relx=0.02,rely=0.46,relwidth=0.05,relheight=0.03)

        self.clean_button = Button(self.window, text='Clean', bg='#800020', fg='white', bd=3, 
                                   font=('garamond', 11, 'bold'), command=self.clean_entries)
        self.clean_button.place(relx=0.09,rely=0.46,relwidth=0.05,relheight=0.03)

        self.delete_button = Button(self.window, text='Delete', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'))
        self.delete_button.place(relx=0.16,rely=0.46,relwidth=0.05,relheight=0.03)

        self.update_button = Button(self.window, text='Update', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'))
        self.update_button.place(relx=0.23,rely=0.46,relwidth=0.05,relheight=0.03)

    def texts(self):
        self.ticker_text = Label(self.window, text='Ticker', bg='#880808',fg='white', font=('garamond', 13, 'bold'))
        self.ticker_text.place(relx=0.008,rely=0.255, relwidth=0.05, relheight=0.025)

        self.amount_text = Label(self.window, text='Amount', bg='#880808',fg='white', font=('garamond', 13, 'bold'))
        self.amount_text.place(relx=0.012,rely=0.32, relwidth=0.05, relheight=0.025)

        self.comments_text = Label(self.window, text='Comments', bg='#880808',fg='white', font=('garamond', 13, 'bold'))
        self.comments_text.place(relx=0.017,rely=0.385, relwidth=0.05, relheight=0.025)

    def entries(self):
        self.ticker_entry = Entry(self.window, font=('garamond', 13))
        self.ticker_entry.place(relx=0.02,rely=0.28,relwidth=0.05,relheight=0.025)

        self.amount_entry = Spinbox(self.window, from_=0, to=100000000000000, font=('garamond', 13))
        self.amount_entry.place(relx=0.02,rely=0.345,relwidth=0.05,relheight=0.025)

        self.comments_entry = Entry(self.window, font=('garamond', 13))
        self.comments_entry.place(relx=0.02,rely=0.41,relwidth=0.26,relheight=0.025)

    def ticker_aumont_table(self):
        self.ticker_amount_table = ttk.Treeview(self.frame_tabela_ticker_amount, height= 3, columns=('column1', 'column2'))
        self.ticker_amount_table.configure(height=5, show='headings')
        self.ticker_amount_table.heading('#1', text='Ticker')
        self.ticker_amount_table.heading('#2', text='Aumont')

        self.ticker_amount_table.column('#1', width=10)
        self.ticker_amount_table.column('#2', width=10)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("garamond", 12, "bold"))
        self.ticker_amount_table.place(relx=0,rely=0,relwidth=0.95,relheight=1)

        self.scrool_ticker_amount_table = Scrollbar(self.frame_tabela_ticker_amount, orient='vertical')
        self.ticker_amount_table.configure(yscroll=self.scrool_ticker_amount_table.set)
        self.scrool_ticker_amount_table.place(relx=0.94, rely=0.001, relwidth=0.06, relheight=0.9999)

        
Aplication()