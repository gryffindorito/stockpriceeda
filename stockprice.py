import numpy as np
import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import yfinance as yf

st.set_option('deprecation.showPyplotGlobalUse', False)

st.set_page_config(layout = "wide")

st.title('Stock Prices of S&P 500 companies')

expand_bar = st.beta_expander("About")
expand_bar.markdown("""
This webapp performs simple web scrapping of S&P 500 Companies and displays the price graphs according to the apropriate selection.
* **Python Libraries:** base64, pandas, streamlit
* **Data Source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies)
""")

st.sidebar.header('User Selection')


@st.cache
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header = 0)
    df = html[0]
    return df

df = load_data()
sector = df.groupby('GICS Sector')

sorted_sector_unique = sorted(df['GICS Sector'].unique())
selected_sector = st.sidebar.selectbox('Sector', sorted_sector_unique)

selected_list = [selected_sector]

df_selected_sector = df[(df['GICS Sector'].isin(selected_list))]

selected_sector_list = df_selected_sector.Symbol.tolist()

st.header('Display Companies in the Selected Sector')
st.write('Data Dimention : ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
st.dataframe(df_selected_sector)

def filedownload(df):
    csv = df.to_csv(index = False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href = "data:file/csv;base64,{b64}" download="SP500.csv">Download CSV</a>'
    return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html = True)

stock_data = yf.download(
    tickers = list(df_selected_sector.Symbol),
    period = "ytd",
    interval = "1d",
    group_by = 'ticker',
    auto_adjust = True,
    prepost = True,
    threads = True,
    proxy = None
)

def price_plot(symbol):
    df = pd.DataFrame(stock_data[symbol].Close)
    df['Date'] = df.index
    plt.fill_between(df.Date, df.Close, color = '#f42069', alpha = 0.3)
    plt.xticks(rotation = 90)
    plt.title(symbol, fontweight = 'bold')
    plt.xlabel('Date')
    plt.ylabel('Closing Price in USD')
    #plt.figure(figsize = (8,5), dpi = 150)
    return st.pyplot()

select_company = st.sidebar.multiselect('Companies', selected_sector_list, selected_sector_list)

if st.button('Show Plots'):
    st.header('Stock Closing Price')
    for i in list(select_company):
        price_plot(i)