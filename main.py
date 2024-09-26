import yfinance as yf
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import plotly.graph_objs as go

# global variable to store tickers in the list
selected_tickers = []

# fetches tickers using yfinance
def get_ticker(company_name):
    try:
        ticker = yf.Ticker(company_name)  # creates obj for selected ticker
        if ticker.history(period="1d").empty:  # validation to check if it exists & isn't private etc
            raise ValueError(f"No data found for {company_name}")
        return company_name
    except Exception:
        messagebox.showerror("Error", f"Could not find a valid ticker for '{company_name}'")
        return None

# retrieves stock data for the selected tickers
def get_data(tickers, period):
    combined_df = pd.DataFrame()  # empty dataframe is made to store stock data
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)  # Create a ticker object
            hist = stock.history(period=period)  
            hist['Company'] = ticker  
            hist.reset_index(inplace=True)  
            combined_df = pd.concat([combined_df, hist], ignore_index=True)  
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while fetching data for {ticker}: {e}")
    return combined_df

# plot stock prices in the graph for the selected company
def show_graph(period):
    if not selected_tickers:
        messagebox.showerror("Error", "Please add at least one stock/company.")
        return

    combined_df = get_data(selected_tickers, period)  # fetches data for all of the tickers entered

    if combined_df.empty:
        messagebox.showerror("Error", "No valid data found for the selected stocks.")
        return

    fig = go.Figure()  # new plotly figure graph

    for ticker in selected_tickers:
        stock_data = combined_df[combined_df['Company'] == ticker]  
        fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['High'], mode='lines', name=ticker))

    # layout customisation
    fig.update_layout(
        title="Stock Price Comparison",
        xaxis_title="Date",
        yaxis_title="High Value",
        legend_title="Company",
        legend=dict(x=1, y=1, traceorder="normal", bordercolor="Black", borderwidth=1),
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        hovermode='x unified',  # allows to see info of the plotted points when hovering over them at any point on the graph
    )
    fig.show()


def compare_all():
    combined_df = pd.DataFrame()  
    periods = ['3mo', '6mo', '1y', '5y', '10y', 'max']  

    # fetching period data and creates columns for it
    for period in periods:
        period_data = get_data(selected_tickers, period)  
        period_data['Period'] = period  
        combined_df = pd.concat([combined_df, period_data], ignore_index=True)  

    if combined_df.empty:
        messagebox.showerror("Error", "No valid data found for the selected stocks.")
        return

    fig = go.Figure()  # new figure using plotly

    for ticker in selected_tickers:
        for period in periods:
            stock_data = combined_df[(combined_df['Company'] == ticker) & (combined_df['Period'] == period)]
            fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['High'], mode='lines', name=f"{ticker} - {period}"))

    # graph layout 
    fig.update_layout(
        title="Stock Price Comparison Across Periods",
        xaxis_title="Date",
        yaxis_title="High Value",
        legend_title="Company/Period",
        legend=dict(x=1, y=1, traceorder="normal", bordercolor="Black", borderwidth=1),
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )
    fig.show()

# adds tickers to the ticker list w/yfinance
def add_ticker():
    company_name = file_var.get().strip()  
    if company_name:
        ticker = get_ticker(company_name)  
        if ticker and ticker not in selected_tickers:
            selected_tickers.append(ticker) 
            messagebox.showinfo("Success", f"{ticker} added to the list.")
        else:
            messagebox.showerror("Error", f"{ticker} is already in the list or invalid.")
    else:
        messagebox.showerror("Error", "Please enter a company name or ticker.")

# displays the list of tickers in a user friendly format
def view_tickers():
    if selected_tickers:
        ticker_list = "\n".join(selected_tickers)
        messagebox.showinfo("Selected Tickers", f"Current tickers:\n{ticker_list}")
    else:
        messagebox.showinfo("Selected Tickers", "No tickers selected yet.")

# clears tickets from the list 
def clear_tickers():
    selected_tickers.clear()
    messagebox.showinfo("Success", "Ticker list cleared.")

# tkinter ui initilisation
root = tk.Tk()
root.title("Stock Market Data")

# setting window size and position
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.8)
window_height = int(screen_height * 0.8)
window_x = (screen_width - window_width) // 2
window_y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
root.configure(bg="black")

# UI that tells the user what to enter in the text field
file_label = tk.Label(root, text="Enter Company Name or Ticker:", bg="black", fg="blue", font=("Titillium Web", 16))
file_label.pack(pady=10)

# text field to enter the tickers
file_var = tk.StringVar(root)
file_menu = ttk.Entry(root, textvariable=file_var, font=("Titillium Web", 14), width=50)
file_menu.pack(pady=10)

# creating a frame for the buttons
button_frame = tk.Frame(root, bg="black")
button_frame.pack(pady=10)

# defining the button style
style = ttk.Style()
style.configure('RoundedButton.TButton', padding=6, font=("Titillium Web", 14), relief="raised")

# buttons to add, clear and display current tickers
btn_add_ticker = ttk.Button(button_frame, text="Add Ticker", command=add_ticker, style="RoundedButton.TButton")
btn_add_ticker.grid(row=0, column=0, padx=10, pady=10)

btn_view_tickers = ttk.Button(button_frame, text="View Selected Tickers", command=view_tickers, style="RoundedButton.TButton")
btn_view_tickers.grid(row=0, column=1, padx=10, pady=10)

btn_clear_tickers = ttk.Button(button_frame, text="Clear Tickers", command=clear_tickers, style="RoundedButton.TButton")
btn_clear_tickers.grid(row=0, column=2, padx=10, pady=10)

# separate frame for period selection buttons
period_frame = tk.Frame(root, bg="black")
period_frame.pack(pady=10)

# actual period selection buttons
btn_3mo = ttk.Button(period_frame, text="Show 3 Month", command=lambda: show_graph('3mo'), style="RoundedButton.TButton")
btn_3mo.grid(row=1, column=0, padx=10, pady=10)

btn_6mo = ttk.Button(period_frame, text="Show 6 Month", command=lambda: show_graph('6mo'), style="RoundedButton.TButton")
btn_6mo.grid(row=1, column=1, padx=10, pady=10)

btn_1y = ttk.Button(period_frame, text="Show 1 Year", command=lambda: show_graph('1y'), style="RoundedButton.TButton")
btn_1y.grid(row=1, column=2, padx=10, pady=10)

btn_5y = ttk.Button(period_frame, text="Show 5 Year", command=lambda: show_graph('5y'), style="RoundedButton.TButton")
btn_5y.grid(row=1, column=3, padx=10, pady=10)

btn_10y = ttk.Button(period_frame, text="Show 10 Year", command=lambda: show_graph('10y'), style="RoundedButton.TButton")
btn_10y.grid(row=1, column=4, padx=10, pady=10)

btn_max = ttk.Button(period_frame, text="Show Max", command=lambda: show_graph('max'), style="RoundedButton.TButton")
btn_max.grid(row=1, column=5, padx=10, pady=10)

# begins the main loop
root.mainloop()
