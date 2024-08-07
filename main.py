from tkinter import *
from tkinter import ttk
from PIL import ImageTk
import sqlite3
import base64
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import yfinance as yf
import matplotlib.dates as mdates
import numpy as np
import requests
from bs4 import BeautifulSoup

window = Tk()
canvas = None
data = None
fig = None

class Functions:
    def get_dolar(self): 
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'}
        requisicao = requests.get('https://www.google.com/search?q=dolar+real&oq=dolar+re', headers=headers)
        site = BeautifulSoup(requisicao.text, 'html.parser')

        dolar = site.find('span', class_='SwHCTb')
        return float(dolar['data-value'])

    def get_yuan(self):
        headers2 = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'}
        requisicao2 = requests.get('https://www.google.com/search?q=yuan+para+real', headers=headers2)
        site2 = BeautifulSoup(requisicao2.text, 'html.parser')

        yuan = site2.find('span', class_='SwHCTb')
        return float(yuan['data-value'])

    def get_yu_dol(self):
        headers2 = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'}
        requisicao2 = requests.get('https://www.google.com/search?q=dolar+para+yuan&oq=dolar+para+yuan', headers=headers2)
        site2 = BeautifulSoup(requisicao2.text, 'html.parser')

        yu_dol = site2.find('span', class_='SwHCTb')
        return float(yu_dol['data-value'])

    def clean_stocks_entries(self):
        self.ticker_entry.delete(0, END)
        self.amount_entry.delete(0, END)
        self.amount_entry.insert(END, 0)
        self.mag_glass_button.place_forget()

        self.create_graph()
        self.old_ticker = None
        self.create_div_graph()

        self.five_days_button.config(bg='black')
        self.thirty_days_button.config(bg='black')
        self.year_button.config(bg='black')

    def bd_connect(self):
        self.connect = sqlite3.connect('stocks_tracker.db')
        self.cursor = self.connect.cursor()

    def bd_disconnect(self):
        self.connect.close()

    def create_table(self):
        self.bd_connect()
        self.cursor.execute("""
            create table if not exists ticker_amount (
                ticker text not null,
                amount int not null,
                primary key (ticker)
            );""")
        self.connect.commit()
        self.bd_disconnect()

    def register_stock(self):
        self.ticker = self.ticker_entry.get().upper().strip()
        self.old_ticker = self.ticker
        self.amount = self.amount_entry.get()

        if not self.ticker:
            return

        try:
            int_amount = int(self.amount)
        except ValueError:
            return

        if self.old_ticker != 'A':
            try:
                acao = yf.Ticker(f'{self.old_ticker}')
                informations = acao.history(period='1d')

                if not informations.empty:
                    self.bd_connect()
                    self.cursor.execute("""insert into ticker_amount (ticker, amount)
                        values (?, ?)""", (self.ticker, self.amount))
                    self.connect.commit()
                    self.show_table1()
                    self.show_table2()
                    self.five_days()
                    self.five_days_button.config(bg='#92000a')
                    self.create_div_graph()
                    self.create_pie_graph()
                else:
                    acao = yf.Ticker(f'{self.old_ticker}.SA')
                    informations = acao.history(period='1d')

                    if not informations.empty:
                        self.old_ticker = f'{self.old_ticker}.SA'
                        self.bd_connect()
                        self.cursor.execute("""insert into ticker_amount (ticker, amount)
                            values (?, ?)""", (self.ticker, self.amount))
                        self.connect.commit()
                        self.show_table1()
                        self.show_table2()
                        self.five_days()
                        self.five_days_button.config(bg='#92000a')
                        self.create_div_graph()
                        self.create_pie_graph()
            
            except Exception:
                print('ERRO')

        else:
            self.clean_stocks_entries()

    def search_stock(self):
        self.ticker = self.ticker_entry.get().upper().strip()
        self.old_ticker = self.ticker

        if self.old_ticker != 'A':
            try:
                acao = yf.Ticker(f'{self.old_ticker}')
                informations = acao.history(period='1d')

                if not informations.empty:
                    self.five_days()
                    self.five_days_button.config(bg='#92000a')
                    self.create_div_graph()
                else:
                    acao = yf.Ticker(f'{self.old_ticker}.SA')
                    informations = acao.history(period='1d')

                    if not informations.empty:
                        self.old_ticker = f'{self.old_ticker}.SA'
                        self.five_days()
                        self.five_days_button.config(bg='#92000a')
                        self.create_div_graph()

                    else:
                        print(f'Não foi possivel encontrar {self.old_ticker}')
            
            except Exception:
                print('ERRO')

    def show_search_button(self, event):
        self.mag_glass_button.place(relx=0.08, rely=0.335, relwidth=0.02, relheight=0.025)

    def show_table1(self):
        self.ticker_amount_table.delete(*self.ticker_amount_table.get_children())

        self.bd_connect()
        table1 = self.cursor.execute(""" select ticker, amount from ticker_amount; """)
        for i in table1:
            self.ticker_amount_table.insert('', END, values=i)
        self.bd_disconnect()

    def show_table2(self):
        self.ticker_value_table.delete(*self.ticker_value_table.get_children())
        dolar = self.get_dolar()
        yuan = self.get_yuan()
        yu_dol = self.get_yu_dol()

        self.bd_connect()
        table2 = self.cursor.execute(""" select ticker, amount from ticker_amount; """)
        if self.language == 'pt':
            for e in table2:
                try: 
                    data = yf.Ticker(e[0])
                    info = data.history(period='1d')

                    if not info.empty:
                        price = info['Close'].values[-1]
                        price = round(price, 2)

                        valor_formatado = f'R$ {(float(e[1]) * price) * dolar:.2f}'
                        self.ticker_value_table.insert('', END, values=(e[0], valor_formatado))

                    else:
                        data = yf.Ticker(f'{e[0]}.SA')
                        info = data.history(period='1d')

                        if not info.empty:
                            price = info['Close'].values[-1]
                            price = round(price, 2)
                            
                            valor_formatado = f'R$ {float(e[1]) * price:.2f}'
                            self.ticker_value_table.insert('', END, values=(e[0], valor_formatado))

                except Exception:
                    print('Erro na tabela de ticker e valor total investido')
                    
        elif self.language == 'en':
            for e in table2:
                try: 
                    data = yf.Ticker(e[0])
                    info = data.history(period='1d')

                    if not info.empty:
                        price = info['Close'].values[-1]
                        price = round(price, 2)

                        valor_formatado = f'US {float(e[1]) * price:.2f}'
                        self.ticker_value_table.insert('', END, values=(e[0], valor_formatado))

                    else:
                        data = yf.Ticker(f'{e[0]}.SA')
                        info = data.history(period='1d')

                        if not info.empty:
                            price = info['Close'].values[-1]
                            price = round(price, 2)
                            
                            valor_formatado = f'US {(float(e[1]) * price) / dolar:.2f}'
                            self.ticker_value_table.insert('', END, values=(e[0], valor_formatado))

                except Exception:
                    print('Erro na tabela de ticker e valor total investido')
        else:
            for e in table2:
                try: 
                    data = yf.Ticker(e[0])
                    info = data.history(period='1d')

                    if not info.empty:
                        price = info['Close'].values[-1]
                        price = round(price, 2)

                        valor_formatado = f'{(float(e[1]) * price) * yu_dol:.2f}¥'
                        self.ticker_value_table.insert('', END, values=(e[0], valor_formatado))

                    else:
                        data = yf.Ticker(f'{e[0]}.SA')
                        info = data.history(period='1d')

                        if not info.empty:
                            price = info['Close'].values[-1]
                            price = round(price, 2)
                            
                            valor_formatado = f'{(float(e[1]) * price) / yuan:.2f}¥'
                            self.ticker_value_table.insert('', END, values=(e[0], valor_formatado))

                except Exception:
                    print('Erro na tabela de ticker e valor total investido')
        self.bd_disconnect()

    def on_double_click(self, event):
        self.clean_stocks_entries()
        self.amount_entry.delete(0, END)
        selected_stock = self.ticker_amount_table.selection()

        if selected_stock:
            col1, col2 = self.ticker_amount_table.item(selected_stock[0], 'values')
            self.old_ticker = col1

            try:
                acao = yf.Ticker(f'{self.old_ticker}')
                informations2 = acao.history(period='1d')

                if not informations2.empty:
                    self.ticker_entry.insert(END, col1)
                    self.amount_entry.insert(END, col2)
                    self.five_days_button.config(bg='#92000a')
                    self.five_days()
                    self.create_div_graph()
                else:
                    acao = yf.Ticker(f'{self.old_ticker}.SA')
                    informations2 = acao.history(period='1d')

                    if not informations2.empty:
                        self.old_ticker = f'{self.old_ticker}.SA'
                        self.ticker_entry.insert(END, col1)
                        self.amount_entry.insert(END, col2)
                        self.five_days_button.config(bg='#92000a')
                        self.five_days()
                        self.create_div_graph()

            except Exception:
                    print(f"ERRO.")

    def five_days(self):
        self.period = '5d'
        if self.old_ticker:
            ticker = self.old_ticker
            self.create_graph(ticker, "5d")

        self.thirty_days_button.config(bg='black')
        self.year_button.config(bg='black')

    def thirty_days(self):
        self.period = '30d'
        if self.old_ticker:
            ticker = self.old_ticker
            self.create_graph(ticker, "30d")

        self.five_days_button.config(bg='black')
        self.year_button.config(bg='black')

    def year(self):
        self.period = '1y'
        if self.old_ticker:
            ticker = self.old_ticker
            self.create_graph(ticker, "1y")

        self.five_days_button.config(bg='black')
        self.thirty_days_button.config(bg='black')

    def create_graph(self, ticker='', period=''): 
        def currency_formatter(x, pos):
            if self.language == 'pt':
                return f"R${x:.2f}"
            elif self.language == 'en': 
                return f"US{x:.2f}"
            else: 
                return f"{x:.2f}¥"

        fig, ax = plt.subplots()
        fig.subplots_adjust(left=0.1, right=0.99, top=1, bottom=0.07)

        if ticker != '':  # se alguma ação estiver selecionada
            data = yf.Ticker(ticker)
            df = data.history(period=period)
            
            if self.old_ticker.endswith('SA'):
                if self.language == 'pt':
                    ax.plot(df.index, df['Close'].values, color='k', linewidth=1)
                elif self.language == 'en':
                    dolar = self.get_dolar()
                    df['Close'] = df['Close'] / dolar
                    ax.plot(df.index, df['Close'].values, color='k', linewidth=1)
                else:
                    yuan = self.get_yuan()
                    df['Close'] = df['Close'] / yuan
                    ax.plot(df.index, df['Close'].values, color='k', linewidth=1)
                
                last_date = df.index[-1]
                last_price = df['Close'].iloc[-1]
                ax.plot(last_date, last_price, 'ko', markersize=3)

                if self.language == 'pt':
                    ax.annotate(f'R${last_price:.2f}', (last_date, last_price), textcoords="offset points", xytext=(0,5), ha='center')
                elif self.language == 'en':
                    ax.annotate(f'US{last_price:.2f}', (last_date, last_price), textcoords="offset points", xytext=(0,5), ha='center')
                else: 
                    ax.annotate(f'{last_price:.2f}¥', (last_date, last_price), textcoords="offset points", xytext=(0,5), ha='center')

                first_date = df.index[0]
                first_price = df['Close'].iloc[0]
                ax.plot(first_date, first_price, 'ko', markersize=3)  

                if self.language == 'pt':
                    ax.annotate(f'R${first_price:.2f}', (first_date, first_price), textcoords="offset points", xytext=(0,5), ha='center')
                elif self.language == 'en':
                    ax.annotate(f'US{first_price:.2f}', (first_date, first_price), textcoords="offset points", xytext=(0,5), ha='center')
                else: 
                    ax.annotate(f'{first_price:.2f}¥', (first_date, first_price), textcoords="offset points", xytext=(0,5), ha='center')
            else:
                if self.language == 'pt':
                    dolar = self.get_dolar()
                    df['Close'] = df['Close'] * dolar
                    ax.plot(df.index, df['Close'].values, color='k', linewidth=1)
                elif self.language == 'en':
                    ax.plot(df.index, df['Close'].values, color='k', linewidth=1)
                else:
                    yu_dol = self.get_yu_dol()
                    df['Close'] = df['Close'] * yu_dol
                    ax.plot(df.index, df['Close'].values, color='k', linewidth=1)
                
                last_date = df.index[-1]
                last_price = df['Close'].iloc[-1]
                ax.plot(last_date, last_price, 'ko', markersize=3)

                if self.language == 'pt':
                    ax.annotate(f'R${last_price:.2f}', (last_date, last_price), textcoords="offset points", xytext=(0,5), ha='center')
                elif self.language == 'en':
                    ax.annotate(f'US{last_price:.2f}', (last_date, last_price), textcoords="offset points", xytext=(0,5), ha='center')
                else: 
                    ax.annotate(f'{last_price:.2f}¥', (last_date, last_price), textcoords="offset points", xytext=(0,5), ha='center')

                first_date = df.index[0]
                first_price = df['Close'].iloc[0]
                ax.plot(first_date, first_price, 'ko', markersize=3)  

                if self.language == 'pt':
                    ax.annotate(f'R${first_price:.2f}', (first_date, first_price), textcoords="offset points", xytext=(0,5), ha='center')
                elif self.language == 'en':
                    ax.annotate(f'US{first_price:.2f}', (first_date, first_price), textcoords="offset points", xytext=(0,5), ha='center')
                else: 
                    ax.annotate(f'{first_price:.2f}¥', (first_date, first_price), textcoords="offset points", xytext=(0,5), ha='center')

        if period == '5d':
            date_format = mdates.DateFormatter('%d-%m-%Y')
            ax.xaxis.set_major_formatter(date_format)
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        elif period == '30d':
            date_format = mdates.DateFormatter('%d-%m-%Y')
            ax.xaxis.set_major_formatter(date_format)
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        elif period == '1y':
            date_format = mdates.DateFormatter('%m-%Y')
            ax.xaxis.set_major_formatter(date_format)
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

        if ticker == '':  # se nenhuma ação estiver selecionada
            if self.language == 'pt':
                text = 'SELECIONE OU REGISTRE \n           UMA AÇÃO'
                ax.text(0.171, 0.41, text, alpha=0.5, fontsize=27, color='white')
            elif self.language == 'en':
                text = 'SELECT OR REGISTER \n           A STOCK'
                ax.text(0.215, 0.42, text, alpha=0.5, fontsize=27, color='white')
            else:
                ax.bar([], [])

        ax.set_facecolor('#880808')
        ax.grid(True, linestyle='-', alpha=0.5)

        ax.yaxis.set_major_formatter(currency_formatter)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_graph)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.place(rely=0.1, relx=0, relheight=0.9, relwidth=1)
        canvas.draw()

        plt.close(fig)

    def create_div_graph(self):
        global dividends

        def currency_formatter(x, pos):
            if self.language == 'pt':
                return f"R${x:.2f}"
            elif self.language == 'en': 
                return f"US{x:.2f}"
            else: 
                return f"{x:.2f}¥"

        if self.old_ticker:  # se tiver alguma alguma ação selecionada
            ticker = self.old_ticker
            div_data = yf.Ticker(ticker)
            dividends = div_data.dividends
            dividends_last12 = dividends.tail(12)

            if not dividends.empty:  # se a ação selecionada tiver dividendos
                fig2, ax2 = plt.subplots()
                fig2.subplots_adjust(left=0.1, right=1, top=1, bottom=0.07)
                fig2.subplots_adjust(left=0.1, right=1, top=1, bottom=0.07)
                bar_width = 0.8

                positions = np.arange(len(dividends_last12))

                if self.old_ticker.endswith('.SA'):
                    if self.language == 'pt':
                        ax2.bar(positions, dividends_last12, width=bar_width, color='black')
                    elif self.language == 'en':
                        dolar = self.get_dolar()
                        dividends_last12 = dividends_last12 / dolar
                        ax2.bar(positions, dividends_last12, width=bar_width, color='black')
                    else: 
                        yuan = self.get_yuan()
                        dividends_last12 = dividends_last12 / yuan
                        ax2.bar(positions, dividends_last12, width=bar_width, color='black')
                else:
                    if self.language == 'pt':
                        dolar = self.get_dolar()
                        dividends_last12 = dividends_last12 * dolar
                        ax2.bar(positions, dividends_last12, width=bar_width, color='black')
                    elif self.language == 'en':
                        ax2.bar(positions, dividends_last12, width=bar_width, color='black')
                    else: 
                        yu_dol = self.get_yu_dol()
                        dividends_last12 = dividends_last12 * yu_dol
                        ax2.bar(positions, dividends_last12, width=bar_width, color='black')

                ax2.set_xticks(positions)
                ax2.set_xticklabels([d.strftime('%m-%y') for d in dividends_last12.index])

                ax2.set_facecolor('#880808')
                ax2.grid(True, linestyle='-', alpha=0.5)

                ax2.yaxis.set_major_formatter(currency_formatter)

                canvas = FigureCanvasTkAgg(fig2, master=self.dividends_graph)
                canvas_widget = canvas.get_tk_widget()
                canvas_widget.place(rely=0, relx=0, relheight=1, relwidth=1)
                canvas.draw()

                plt.close(fig2)

            else:  # se a ação selecionada não tiver dividendos
                fig2, ax2 = plt.subplots()
                fig2.subplots_adjust(left=0.1, right=0.99, top=1, bottom=0.07)
                ax2.set_facecolor('#880808')
                ax2.grid(True, linestyle='-', alpha=0.5)

                if self.language == 'pt':
                    text = 'DIVIDENDOS NÃO ENCONTRADOS'
                    ax2.text(0.045, 0.47, text, alpha=0.5, fontsize=25, color='white')
                elif self.language == 'en':
                    text = 'DIVIDENDS NOT FOUND'
                    ax2.text(0.175, 0.47, text, alpha=0.5, fontsize=25, color='white')
                else:
                    ax2.bar([], [])
                ax2.yaxis.set_major_formatter(currency_formatter)

                canvas = FigureCanvasTkAgg(fig2, master=self.dividends_graph)
                canvas_widget = canvas.get_tk_widget()
                canvas_widget.place(rely=0, relx=0, relheight=1, relwidth=1)
                canvas.draw()

                plt.close(fig2)

        else:  # se nenhuma ação está selecionada
            fig2, ax2 = plt.subplots()
            fig2.subplots_adjust(left=0.1, right=0.99, top=1, bottom=0.07)
            ax2.set_facecolor('#880808')
            ax2.grid(True, linestyle='-', alpha=0.5)

            if self.language == 'pt':
                text = 'SELECIONE OU REGISTRE \n           UMA AÇÃO'
                ax2.text(0.155, 0.4, text, alpha=0.5, fontsize=25, color='white')
            elif self.language == 'en':
                text = 'SELECT OR REGISTER \n           A STOCK'
                ax2.text(0.205, 0.41, text, alpha=0.5, fontsize=25, color='white')
            else:
                ax2.bar([], [])
            ax2.yaxis.set_major_formatter(currency_formatter)

            canvas = FigureCanvasTkAgg(fig2, master=self.dividends_graph)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(rely=0, relx=0, relheight=1, relwidth=1)
            canvas.draw()

            plt.close(fig2)

    def create_pie_graph(self):
        self.bd_connect()
        self.cursor.execute("SELECT COUNT(*) FROM ticker_amount")
        count = self.cursor.fetchone()[0]
        self.bd_disconnect()

        if count != 0:
            self.bd_connect()
            self.cursor.execute("SELECT ticker FROM ticker_amount ORDER BY rowid")
            tickers = [record[0] for record in self.cursor.fetchall()]
            self.bd_disconnect()

            self.bd_connect()
            self.cursor.execute("SELECT amount FROM ticker_amount")
            amounts = [record[0] for record in self.cursor.fetchall()]
            self.bd_disconnect()

            dol = self.get_dolar()

            stock_list = tickers #ações
            amount_list = amounts #quantidade
            prices_list = []
            
            for stock in stock_list:
                try: 
                    data = yf.Ticker(stock)
                    info = data.history(period='1d')

                    if not info.empty:
                        price = info['Close'].values[-1]
                        price = round(price, 2)
                        price = price * dol
                        prices_list.append(price)
                    else:
                        data = yf.Ticker(f'{stock}.SA')
                        info = data.history(period='1d')

                        if not info.empty:
                            price = info['Close'].values[-1]
                            price = round(price, 2)
                            prices_list.append(price)

                except Exception:
                    print('Erro no gráfico de pedaço')

            price_amount_list = []

            for p, a in zip(prices_list, amount_list):
                price_amount_list.append(p * a)   

            text = '\n'.join(stock_list)        

            n = len(stock_list)
            explode = tuple(0.015 * n for _ in range(n))

            fig3, ax3 = plt.subplots()  
            ax3.pie(price_amount_list, labels=stock_list, explode=explode, autopct='%1.1f%%', colors=['red'] * len(price_amount_list), shadow=True)

            fig3.patch.set_facecolor('#880808')

            canvas = FigureCanvasTkAgg(fig3, master=self.pie_graph)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(rely=0, relx=0.5, relheight=1, relwidth=0.5)
            canvas.draw()

            plt.close(fig3)
        
        else:
            fig3, ax3 = plt.subplots()  
            ax3.pie([1], colors=['red'] * len([1]), shadow=True)

            fig3.patch.set_facecolor('#880808')

            canvas = FigureCanvasTkAgg(fig3, master=self.pie_graph)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(rely=0, relx=0.5, relheight=1, relwidth=0.5)
            canvas.draw()

            plt.close(fig3)

    def delete_stock(self):
        self.ticker = self.ticker_entry.get().upper()

        if self.ticker:
            self.amount = self.amount_entry.get()

            self.bd_connect()
            self.cursor.execute(""" delete from ticker_amount where ticker = ?""", (self.ticker,))
            self.connect.commit()

            self.bd_disconnect()
            self.clean_stocks_entries()
            self.show_table1()
            self.show_table2()
            self.create_pie_graph()
            self.old_ticker = None
            self.create_div_graph()
            self.five_days_button.config(bg='black')
            self.thirty_days_button.config(bg='black')
            self.year_button.config(bg='black')

    def update_info(self):
        self.ticker = self.ticker_entry.get().upper().strip()
        self.amount = self.amount_entry.get()

        if not self.ticker or not self.amount:
            return

        self.bd_connect()
        if self.old_ticker.endswith('.SA'):
            ticker_no_sa = self.old_ticker[:-3]
            self.cursor.execute(""" update ticker_amount set ticker = ?, amount = ? where ticker = ?""",
                                (self.ticker, self.amount, ticker_no_sa))
        else:
            self.cursor.execute(""" update ticker_amount set ticker = ?, amount = ? where ticker = ?""",
                                (self.ticker, self.amount, self.old_ticker))
        self.connect.commit()
        self.bd_disconnect()

        self.show_table1()
        self.show_table2()
        self.create_pie_graph()

    def images_64(self):
        self.mag_glass = '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAXABcDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDhtOsdI8PeHbLWNdsv7Uv9R3tZWDyNHEkSsVMspUhjlgQqgj7pJPQVa0mXQvGt2mkSaNZ6Hq9x8lldWLyCF5f4Y5Y3ZuGPG5SCCRkEUTabP418J6M+hobrV9Ht2srmwTmV4RI7pLGvVx85VgMkEA4wa1PhT8OtfuvF+m3uoabc2NpZzi5Aul8h52j+cRxh8FiSvJ6AZJNeYk20ktD7ipUhGEpzlaSv1+7T+rnl8sbxSvHKpWRGKsp6gjqKKu6+t2muagNSt3tr0zu00Lrgo5YkjFFYs9CLukylFI8UiyROyOpyrKcEH2NXU1nU01C3vxf3Rvbdg0U7SsXQjpgk0UUXBxT3R2/xA8aaP428NWN5f2Mlv4ygcQzzwqBDcxAfeb/a6cfXtgAoopyk5O7M6VKNGPJDY//Z'

        self.china = '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAARABkDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwCKZ9POl2a2Uc/9ph8yEnIOemOOeg/PvWfdY83+HO0bsZ645znvmoaWvj4U+XqfrsYcvUSiiirLCiiigAooooA//9k='

        self.usa = '/9j/4AAQSkZJRgABAQEBLAEsAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAANABkDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDnIfDGtjOdB1XPvZSZ6+uOvXn1yf4q6zw54dmTSYheaVLHNk5WXS3ZgM8dbCXAx0G84HHHQcz/AMJhpf8A0Ah/37sP/kOk/wCEw0v/AKAQ/wC/dh/8h0YnMfrEOVqx9rguHMRhKjqJ30t0/wAzuf7AT/oHD/wUt/8AKuj+wE/6Bw/8FLf/ACrrhv8AhMNL/wCgEP8Av3Yf/IdH/CYaX/0Ah/37sP8A5Drh54nq/wBn4nt+KP/Z'

        self.pt_br = '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAASABkDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD5t+EXwW+JPx28T2/hb4beG77Xr8EnVr1v9C0LSdP4xqWsasfl0YKAOT9DwADofEnxL+zL8DbzWPhx8VvAn7V5m0/xR/wi2vftV6L8MPsPwG8N+IMnR8aTpOtf8T/xn4Iyf+Rg/wCKY8U+Kv7HJ8H+Es/8jR7z+yl+2141/ZilHht9PsfFvwv1HU/tep+Hdp0/XrPUP+gnpWqnuMnI8Qsw96+AYv8Agnlr1r8S9e+MvwQ/ah+GPgf9nvUNeN1deLdb8T+J9D+LfhDw/rOp6vq//CCeLfhONCz401v+wx/YA8P+HT4n8K/FI6MSOpr+IfD2OQZv4ieIuXePudvgTg3KOHMql4dZ3w/HOZPP+IFFvNo5xm39lp/2s5rK45blX9mLLsw2vjOn+Z3gRwZ4B5twV/abrribjaUs4XEeSZ/KGTf2FkbUbyyZ81qkre9/ai5ngGl/uT1X0f8AGH9nr4ifBK406bxZYQar4P8AE9rp2q+DfiB4Zu/7b8CeMdO1Yf2tpGpaVqvQFvvHQiCQ3ODXhWU/uH/vv/7Gv0C/aG/be1L4h/D/AEj4DfCrSYPBvwb8P6B4e8G2Y1PStM/t7xPYeEtMGj6QP7L0X/in/BWi40rcPD/h75SM/MMg18C/Y7v/AJ5P/wB9D/4qvD8Ms448x/Dyr8eZZj8Lm31ipHALLcJ/aGKqcPxlbJ6mb4f3f7LzF4fmdXAJJU9HZN2P5v8AGXKPC7JuNsfgPCviDOcdw5Ts+fP8QsHCniJO0qeU4qMZPNMuTuqWOm71LK2lmVKKKK+9zH4V/wBf6P8A6VTPyXLf4tf/AK8V/wAohTt7/wB5vzP+NFFelR+OfpS/Q8yrvT/69x/9KR//2Q=='

        self.spider64 = 'iVBORw0KGgoAAAANSUhEUgAAA34AAAN+CAYAAABKKdkUAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAP+lSURBVHhe7N0HnCRHeTf+6tmdzTnnvbwCJBOMTDTBCBmDwQEbm2BsvxgbY2zsl//diSDABEl3Mg6AMfEFYzBgwCaYYCSiyAIEFgjt5duccw5T/+dXW7XqnZvZdDO70z2/7+czNzM9s3Mdqqufp6u7yrutoEArIiIiIiIiCq2IfSYiIiIiIqKQYuJHREREREQUckz8iIiIiIiIQo6JHxERERERUcgx8SMiIiIiIgo5Jn5EREREREQhx8SPiIiIiIgo5Jj4ERERERERhRwTPyIiIiIiopBj4kdERERERBRyTPyIiIiIiIhCjokfERERERFRyDHxIyIiIiIiCjkmfkRERERERCHHxI+IiIiIiCjkmPgRERERERGFHBM/IiIiIiKikGPiR0REREREFHJM/IiIiIiIiEKOiR8REREREVHIMfEjIiIiIiIKOSZ+REREREREIcfEj4iIiIiIKOSY+BEREREREYUcEz8iIiIiIqKQY+JHREREREQUckz8iIiIiIiIQo6JHxERERERUcgx8SMiIiIiIgo5Jn5EREREREQhx8SPiIiIiIgo5Jj4ERERERERhRwTPyIiIiIiopBj4kdERERERBRyTPyIiIiIiIhCjokfERERERFRyDHxIyIiIiIiCjkmfkRERERERCHHxI+IiIiIiCjkmPgRERERERGFHBM/IiIiIiKikGPiR0REREREFHJM/IiIiIiIiEKOiR8REREREVHIMfEjIiIiIiIKOSZ+REREREREIcfEj4iIiIiIKOSY+BEREREREYUcEz8iIiIiIqKQY+JHREREREQUckz8iIiIiIiIQo6JHxERERERUcgx8SMiIiIiIgo5Jn5EREREREQhx8SPiIiIiIgo5Jj4ERERERERhRwTPyIiIiIiopBj4kdERERERBRyTPyIiIiIiIhCjokfERERERFRyDHxIyIiIiIiCjkmfkRERERERCHHxI+IiIiIiCjkmPgRERERERGFHBM/IiIiIiKikGPiR0REREREFHJM/IiIiIiIiEKOiR8REREREVHIMfEjIiIiIiIKOSZ+REREREREIcfEj4iIiIiIKOSY+BEREREREYUcEz8iIiIiIqKQY+JHREREREQUckz8iIiIiIiIQo6JHxERERERUcgx8SMiIiIiIgo5Jn5EREREREQhx8SPiIiIiIgo5Jj4ERERERERhRwTPyIiIiIiopBj4kdERERERBRyTPyIiIiIiIhCjokfERERERFRyDHxIyIiIiIiCjkmfkRERERERCHHxI+IiIiIiCjkmPgRERERERGFHBM/IiIiIiKikGPiR0REREREFHJM/IiIiIiIiEKOiR8REREREVHIMfEjIiIiIiIKOSZ+REREREREIcfEj4iIiIiIKOSY+BEREREREYUcEz8iIiIiIqKQY+JHREREREQUckz8iIiIiIiIQo6JHxERERERUcgx8SMiIiIiIgo5Jn5EREREREQhx8SPiIiIiIgo5Jj4ERERERERhRwTPyIiIiIiopBj4kdERERERBRyTPyIiIiIiIhCjokfERERERFRyDHxIyIiIiIiCjkmfkRERERERCHHxI+IiIiIiCjkmPgRERERERGFHBM/IiIiIiKikGPiR0REREREFHJM/IiIiIiIiEKOiR8REREREVHIMfEjIiIiIiIKOSZ+REREREREIcfEj4iIiIiIKOSY+BEREREREYUcEz8iIiIiIqKQY+JHREREREQUckz8iIiIiIiIQo6JHxERERERUcgx8SMiIiIiIgo5Jn5EREREREQhx8SPiIiIiIgo5Jj4ERERERERhRwTPyIiIiIiopBj4kdERERERBRyTPyIiIiIiIhCjokfERERERFRyDHxIyIiIiIiCjkmfkRERERERCHHxI+IiIiIiCjkmPgRERERERGFHBM/IiIiIiKikGPiR0REREREFHJM/IiIiIiIiEKOiR8REREREVHIMfEjIiIiIiIKOSZ+REREREREIcfEj4iIiIiIKOSY+BEREREREYUcEz8iIiIiIqKQY+JHREREREQUckz8iIiIiIiIQo6JHxERERERUcgx8SMioi3llJWpqfZ29aOmJvW3S0vqZy0t2n5Ee+zHzc36jcvLZltgm2DbEBERbcW7raCAB28iIrqCF4mouZYW9fmJCX330JBnJ6snVVbqp3mep+bm7BTaS15trfrQ3Jy+d3R0fZs8sq5OP6Oiwivq6VE6FrNTiYiIHsDEj4iINogUFqrLdXXqnefO6dXVVZNcRCQJfPmBA6phaEjplRXzPdpf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8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAijuAHAAAAABFH8AMAAACAiCP4AQAAAEDEEfwAAAAAIOIIfgAAAAAQcQQ/AAAAAIg4gh8AAAAARBzBDwAAAAAiTan/D8StY9KlopRlAAAAAElFTkSuQmCC'

    def pt_language(self):
        self.language = 'pt'

        if not self.old_ticker:
            self.create_graph()
            self.create_div_graph()
        else:
            self.create_graph(self.old_ticker, self.period)
            self.create_div_graph()

        self.language_line.place(relx=0.003, rely=0.039, relwidth=0.02, relheight=0.002)

        self.new_button.config(text='Adicionar')
        self.clean_button.config(text='Limpar')
        self.delete_button.config(text='Deletar')
        self.update_button.config(text='Atualizar')
        self.five_days_button.config(text='5 DIAS')
        self.thirty_days_button.config(text='30 DIAS')
        self.year_button.config(text='1 ANO')

        self.texts()
        self.ticker_amount_table.heading('#1', text='Ticker')
        self.ticker_amount_table.heading('#2', text='Quantidade')

        self.ticker_value_table.heading('#1', text='Ticker')
        self.ticker_value_table.heading('#2', text='Valor Total Investido')

        self.show_table2()

    def usa_language(self):
        self.language = 'en'

        if not self.old_ticker:
            self.create_graph()
            self.create_div_graph()
        else:
            self.create_graph(self.old_ticker, self.period)
            self.create_div_graph()

        self.language_line.place(relx=0.028, rely=0.039, relwidth=0.02, relheight=0.002)

        self.ticker_text.config(text='Symbol')
        self.ticker_text.place(relx=0.01, rely=0.31, relwidth=0.05, relheight=0.025)

        self.amount_text.config(text='Amount')
        self.amount_text.place(relx=0.011, rely=0.375, relwidth=0.05, relheight=0.025)

        self.ticker_amount_table.heading('#1', text='Symbol')
        self.ticker_amount_table.heading('#2', text='Aumont')
        
        self.ticker_value_table.heading('#1', text='Symbol')
        self.ticker_value_table.heading('#2', text='Total Amount Invested')

        self.new_button.config(text='Add')
        self.clean_button.config(text='Clean')
        self.delete_button.config(text='Delete')
        self.update_button.config(text='Update')
        self.five_days_button.config(text='5 DAYS')
        self.thirty_days_button.config(text='30 DAYS')
        self.year_button.config(text='1 YEAR')

        self.show_table2()

    def china_language(self):
        self.language = 'ch'

        if not self.old_ticker:
            self.create_graph()
            self.create_div_graph()
        else:
            self.create_graph(self.old_ticker, self.period)
            self.create_div_graph()

        self.language_line.place(relx=0.053, rely=0.039, relwidth=0.02, relheight=0.002)

        self.ticker_text.config(text='象徵')
        self.ticker_text.place(relx=0.005, rely=0.31, relwidth=0.05, relheight=0.025)

        self.amount_text.config(text='數量')
        self.amount_text.place(relx=0.005, rely=0.375, relwidth=0.05, relheight=0.025)

        self.ticker_amount_table.heading('#1', text='象徵')
        self.ticker_amount_table.heading('#2', text='數量')

        self.ticker_value_table.heading('#1', text='象徵')
        self.ticker_value_table.heading('#2', text='投資總額')

        self.new_button.config(text='加上')
        self.clean_button.config(text='清潔')
        self.delete_button.config(text='刪除')
        self.update_button.config(text='更新')
        self.five_days_button.config(text='5天')
        self.thirty_days_button.config(text='30天')
        self.year_button.config(text='1年')
        
        self.show_table2()

class Aplication(Functions):
    def __init__(self):
        self.window = window
        self.old_ticker = None
        self.language = 'pt'
        self.images_64()
        self.screen_settings()
        self.create_table()
        self.images()
        self.frames()
        self.buttons()
        self.texts()
        self.entries()
        self.ticker_aumont_table()
        self.ticker_value_table()
        self.show_table1()
        self.show_table2()
        self.create_pie_graph()
        self.create_table()
        self.create_graph()
        self.create_div_graph()
        window.mainloop()

        self.selected_button = None

    def screen_settings(self):
        self.window.title('Stocks Tracker')

        # bakcground color
        self.window.configure(background='#880808')  

        # screen dimensions
        self.window.geometry('1920x1080')  
        self.window.state('zoomed')

        # possibility of resizing the screen 
        self.window.resizable(True, True)  

    def images(self):
        self.spider_img = ImageTk.PhotoImage(data=base64.b64decode(self.spider64))
        self.spider_label = Label(self.window, image=self.spider_img, highlightbackground='#880808')
        self.spider_label.place(relx=0.105, rely=0.15, relwidth=0.3, relheight=0.7)

        self.pt_br_img = ImageTk.PhotoImage(data=base64.b64decode(self.pt_br))

        self.usa_img = ImageTk.PhotoImage(data=base64.b64decode(self.usa))

        self.china_img = ImageTk.PhotoImage(data=base64.b64decode(self.china))

        self.mag_glass_img = ImageTk.PhotoImage(data=base64.b64decode(self.mag_glass))

    def frames(self):
        self.frame_tabela_ticker_amount = Frame(self.window, highlightbackground='black', highlightthickness=4)
        self.frame_tabela_ticker_amount.place(relx=0.3, rely=0.05, relwidth=0.2, relheight=0.5)

        self.frame_graph = Frame(self.window, highlightbackground='black', highlightthickness=4)
        self.frame_graph.place(relx=0.537, rely=0.05, relwidth=0.43, relheight=0.5)

        self.frame_graph_buttons = Frame(self.frame_graph, background='black')
        self.frame_graph_buttons.place(relx=0.0, rely=0.0, relheight=0.1, relwidth=1)

        self.dividends_graph = Frame(self.window, highlightbackground='black', highlightthickness=4)
        self.dividends_graph.place(relx=0.561, rely=0.575, relwidth=0.38, relheight=0.4)

        self.language_line = Frame(self.window, highlightbackground='white')
        self.language_line.place(relx=0.003, rely=0.039, relwidth=0.02, relheight=0.002)

        self.separation_line = Frame(self.window, background='black')
        self.separation_line.place(relx=0.025, rely=0.005, relwidth=0.0008, relheight=0.04)

        self.separation_line2 = Frame(self.window, background='black')
        self.separation_line2.place(relx=0.05, rely=0.005, relwidth=0.0008, relheight=0.04)

        self.pie_graph = Frame(self.window, highlightbackground='black', highlightthickness=4, bg='#880808')
        self.pie_graph.place(relx=0.12, rely=0.575, relwidth=0.4, relheight=0.4)

    def buttons(self):
        self.new_button = Button(self.window, text='Adicionar', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'), command=self.register_stock,     activebackground='#92000a',activeforeground='white')
        self.new_button.bind("<Enter>", lambda event, button=self.new_button: button.config(bg='#92000a', fg='white'))
        self.new_button.bind("<Leave>", lambda event, button=self.new_button: button.config(bg='#800020', fg='white'))
        self.new_button.place(relx=0.02, rely=0.46, relwidth=0.05, relheight=0.03)

        self.clean_button = Button(self.window, text='Limpar', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'), command=self.clean_stocks_entries,
        activebackground='#92000a', activeforeground='white')
        self.clean_button.bind("<Enter>", lambda event, button=self.clean_button: button.config(bg='#92000a', fg='white'))
        self.clean_button.bind("<Leave>", lambda event, button=self.clean_button: button.config(bg='#800020', fg='white'))
        self.clean_button.place(relx=0.16, rely=0.46, relwidth=0.05, relheight=0.03)

        self.delete_button = Button(self.window, text='Deletar', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'), command=self.delete_stock,
        activebackground='#92000a', activeforeground='white')
        self.delete_button.bind("<Enter>", lambda event, button=self.delete_button: button.config(bg='#92000a', fg='white'))
        self.delete_button.bind("<Leave>", lambda event, button=self.delete_button: button.config(bg='#800020', fg='white'))
        self.delete_button.place(relx=0.09, rely=0.46, relwidth=0.05, relheight=0.03)

        self.update_button = Button(self.window, text='Atualizar', bg='#800020', fg='white', bd=3, font=('garamond', 11, 'bold'), command=self.update_info, activebackground='#92000a', activeforeground='white')
        self.update_button.bind("<Enter>", lambda event, button=self.update_button: button.config(bg='#92000a', fg='white'))
        self.update_button.bind("<Leave>", lambda event, button=self.update_button: button.config(bg='#800020', fg='white'))
        self.update_button.place(relx=0.23, rely=0.46, relwidth=0.05, relheight=0.03)

        self.five_days_button = Button(self.frame_graph_buttons, text='5 DIAS', bg='black', fg='white', bd=3, font=('garamond', 11, 'bold'), activebackground='#92000a',
        activeforeground='white', command=self.five_days)
        self.five_days_button.bind("<1>", lambda event, button=self.five_days_button: button.config(bg='#92000a'))
        self.five_days_button.place(relx=0.15, rely=0.16, relheight=0.6, relwidth=0.1)

        self.thirty_days_button = Button(self.frame_graph_buttons, text='30 DIAS', bg='black', fg='white', bd=3, font=('garamond', 11, 'bold'), activebackground='#92000a',
        activeforeground='white', command=self.thirty_days)
        self.thirty_days_button.bind("<1>", lambda event, button=self.thirty_days_button: button.config(bg='#92000a'))
        self.thirty_days_button.place(relx=0.45, rely=0.16, relheight=0.6, relwidth=0.1, )

        self.year_button = Button(self.frame_graph_buttons, text='1 ANO', bg='black', fg='white', bd=3, font=('garamond', 11, 'bold'), activebackground='#92000a', activeforeground='white', command=self.year)
        self.year_button.bind("<1>", lambda event, button=self.year_button: button.config(bg='#92000a'))
        self.year_button.place(relx=0.75, rely=0.16, relheight=0.6, relwidth=0.1)

        self.pt_language_button = Button(self.window, image=self.pt_br_img, bg='#800020', activebackground='#92000a',
                                         command=self.pt_language)
        self.pt_language_button.place(relx=0.003, rely=0.01, relwidth=0.02, relheight=0.025)
        self.pt_language_button.bind("<Enter>", lambda event, button=self.pt_language_button: button.config(bg='#92000a', fg='white'))
        self.pt_language_button.bind("<Leave>", lambda event, button=self.pt_language_button: button.config(bg='#800020', fg='white'))

        self.usa_language_button = Button(self.window, image=self.usa_img, bg='#800020', activebackground='#92000a', command=self.usa_language)
        self.usa_language_button.place(relx=0.028, rely=0.01, relwidth=0.02, relheight=0.025)
        self.usa_language_button.bind("<Enter>", lambda event, button=self.usa_language_button: button.config(bg='#92000a', fg='white'))
        self.usa_language_button.bind("<Leave>", lambda event, button=self.usa_language_button: button.config(bg='#800020', fg='white'))

        self.china_language_button = Button(self.window, image=self.china_img, bg='#800020', activebackground='#92000a', command=self.china_language)
        self.china_language_button.place(relx=0.053, rely=0.01, relwidth=0.02, relheight=0.025)
        self.china_language_button.bind("<Enter>", lambda event, button=self.china_language_button: button.config(bg='#92000a', fg='white'))
        self.china_language_button.bind("<Leave>", lambda event, button=self.china_language_button: button.config(bg='#800020', fg='white'))

        self.mag_glass_button = Button(self.window, image=self.mag_glass_img, bg='#800020', activebackground='#92000a', command=self.search_stock)
        self.mag_glass_button.bind("<Enter>", lambda event, button=self.mag_glass_button: button.config(bg='#92000a', fg='white'))
        self.mag_glass_button.bind("<Leave>", lambda event, button=self.mag_glass_button: button.config(bg='#800020', fg='white'))

    def texts(self):
        self.ticker_text = Label(self.window, text='Ticker', bg='#880808', fg='white', font=('garamond', 13, 'bold'))
        self.ticker_text.place(relx=0.008, rely=0.31, relwidth=0.05, relheight=0.025)

        self.amount_text = Label(self.window, text='Quantidade', bg='#880808', fg='white', font=('garamond', 13, 'bold'))
        self.amount_text.place(relx=0.018, rely=0.375, relwidth=0.05, relheight=0.025)

        self.me = Label(self.window, text='@matheushio7', bg='#880808', fg='black', font=('garamond', 10, 'bold'))
        self.me.place(relx=0, rely=0.977, relwidth=0.05, relheight=0.025)

    def entries(self):
        self.ticker_entry = Entry(self.window, font=('garamond', 13))
        self.ticker_entry.place(relx=0.02, rely=0.335, relwidth=0.05, relheight=0.025)
        self.ticker_entry.bind('<KeyRelease>', self.show_search_button)

        self.amount_entry = Spinbox(self.window, from_=0, to=100000000000000, font=('garamond', 13))
        self.amount_entry.place(relx=0.02, rely=0.4, relwidth=0.05, relheight=0.025)

    def ticker_aumont_table(self):
        self.ticker_amount_table = ttk.Treeview(self.frame_tabela_ticker_amount, height=3, columns=('column1', 'column2'))
        self.ticker_amount_table.configure(height=5, show='headings')
        self.ticker_amount_table.heading('#1', text='Ticker')
        self.ticker_amount_table.heading('#2', text='Quantidade')

        self.ticker_amount_table.column('#1', width=10)
        self.ticker_amount_table.column('#2', width=10)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("garamond", 12, "bold"))
        style.configure('Treeview', font=('garamond', 12))
        self.ticker_amount_table.place(relx=0, rely=0, relwidth=0.95, relheight=1)

        self.scrool_ticker_amount_table = Scrollbar(self.frame_tabela_ticker_amount, orient='vertical', command=self.ticker_amount_table.yview)
        self.ticker_amount_table.configure(yscroll=self.scrool_ticker_amount_table.set)
        self.scrool_ticker_amount_table.place(relx=0.94, rely=0.001, relwidth=0.06, relheight=0.9999)

        self.ticker_amount_table.bind('<Double-1>', self.on_double_click)

    def ticker_value_table(self):
        self.ticker_value_table = ttk.Treeview(self.pie_graph, height=3, columns=('column1', 'column2'))
        self.ticker_value_table.configure(height=5, show='headings')
        self.ticker_value_table.heading('#1', text='Ticker')
        self.ticker_value_table.heading('#2', text='Valor Total Investido')

        self.ticker_value_table.column('#1', width=1)
        self.ticker_value_table.column('#2', width=50)
        self.ticker_value_table.place(relx=0, rely=0, relwidth=0.42, relheight=1)

        style2 = ttk.Style()
        style2.theme_use('clam')
        style2.configure('Treeview', font=('garamond', 12), rowheight=30)
        style2.configure("Treeview.Heading", font=("garamond", 12, "bold"))
        style2.map('Treeview', background=[('selected', '#880808')])
        
        self.scrool_ticker_value_table = Scrollbar(self.pie_graph, orient='vertical', command=self.ticker_value_table.yview)
        self.ticker_value_table.configure(yscroll=self.scrool_ticker_value_table.set)
        self.scrool_ticker_value_table.place(relx=0.42, rely=0.001, relwidth=0.03, relheight=0.9999)

Aplication()