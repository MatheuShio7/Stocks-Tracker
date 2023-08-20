from tkinter import *

window = Tk()

class Aplication():
    def __init__(self):
        self.window = window
        self.screen_settings()
        self.frames()
        self.buttons()
        self.texts()
        self.entries()
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

        self.clean_button = Button(self.window, text='Clean', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'))
        self.clean_button.place(relx=0.09,rely=0.46,relwidth=0.05,relheight=0.03)

        self.delete_button = Button(self.window, text='Delete', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'))
        self.delete_button.place(relx=0.16,rely=0.46,relwidth=0.05,relheight=0.03)

        self.update_button = Button(self.window, text='Update', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'))
        self.update_button.place(relx=0.23,rely=0.46,relwidth=0.05,relheight=0.03)

    def texts(self):
        self.ticker_text = Label(self.window, text='Ticker', bg='#880808',fg='white', font=('garamond', 13, 'bold'))
        self.ticker_text.place(relx=0.008,rely=0.245, relwidth=0.05, relheight=0.025)

        self.amount_text = Label(self.window, text='Amount', bg='#880808',fg='white', font=('garamond', 13, 'bold'))
        self.amount_text.place(relx=0.012,rely=0.32, relwidth=0.05, relheight=0.025)

        self.comments_text = Label(self.window, text='Comments', bg='#880808',fg='white', font=('garamond', 13, 'bold'))
        self.comments_text.place(relx=0.017,rely=0.385, relwidth=0.05, relheight=0.025)

    def entries(self):
        self.ticker_entry = Entry(self.window)
        self.ticker_entry.place(relx=0.02,rely=0.28,relwidth=0.05,relheight=0.025)

        self.amount_entry = Entry(self.window)
        self.amount_entry.place(relx=0.02,rely=0.345,relwidth=0.05,relheight=0.025)

        self.amount_entry = Entry(self.window)
        self.amount_entry.place(relx=0.02,rely=0.41,relwidth=0.26,relheight=0.025)
        
Aplication()