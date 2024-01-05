import time
from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st
import yfinance as yf

st.set_page_config(layout="wide")

def getHistoricalMFNavData(schemeCode):
    AVERAGE_FACTOR = 10
    url = "https://api.mfapi.in/mf/"+str(schemeCode)
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        data = response.json()
        df = pd.DataFrame(data['data'])
        dfToConsider = df.head(AVERAGE_FACTOR)
        return dfToConsider
    else:
        return None

def get_stock_data_and_percentage_difference(symbol):
    # end_date = datetime.today().strftime('%Y-%m-%d')
    # start_date = (datetime.today() - timedelta(days=3)).strftime('%Y-%m-%d')
    stock_data = yf.download(symbol, period='7d', interval='1d')
    close_prices = stock_data['Close']
    percentage_difference = (close_prices.pct_change() * 100).dropna()
    return percentage_difference

def yfinancestocktracker(heading, symbols_list):
    
    result_df = pd.DataFrame()
    for symbol in symbols_list:
        percentage_difference = get_stock_data_and_percentage_difference(symbol)
        result_df[symbol] = percentage_difference
    
    result_df.loc['% Change (5 Days)'] = result_df.sum()
    st.markdown("### " + heading)
    st.dataframe(result_df)

def main():
    tab1, tab2 = st.tabs(["Stocks", "Mutual Funds"])
    with tab1:
        list = {
            "ETF": ['SILVERBEES.NS', 'BANKBEES.NS', 'BANKETF.NS', 'ITBEES.NS', 'MON100.NS', 'ICICIB22.NS', 'GOLDBEES.NS'],
            "Indices": ['^NSEI', '^NSEBANK', '^BSESN', '^NSEMDCP50', '^CNXIT', '^DJI' ], # '^CNXMID', '^CNXSMALL', 'NIFTYSMLCAP250.NS'
            "Monopoly": ['BSE.NS', 'HAL.NS', 'MCX.NS', 'POLYCAB.NS', 'CAMS.NS', 'CDSL.NS', 'ASIANPAINT.NS', 'PIDILITIND.NS',  'DMART.NS', 'IRCTC.NS', 'IRFC.NS' ],
            "Monopoly Small and Midcap": ['SULA.NS', 'ASAHIINDIA.NS', 'MAZDOCK.NS', 'PRAJIND.NS', 'BALKRISIND.NS', 'HINDZINC.NS', 'HINDCOPPER.NS'],
            "Monopoly Others": ['SUPREMEIND.NS', 'ANGELONE.NS', 'CENTURYPLY.NS', 'ASTRAL.NS'],
            "EV": ['BHEL.NS', 'JBMA.NS', 'OLECTRA.NS', 'M&M.NS', 'TATAMTRDVR.NS', 'DIXON.NS'],
            "IT": ['WIPRO.NS', 'HCLTECH.NS', 'LTIM.NS','TATAELXSI.NS', 'INFY.NS', 'TCS.NS'],
            "Hospitals": ['NH.NS', 'FORTIS.NS'],
            "Speciality Chemicals": ['GALAXYSURF.NS','NAVINFLUOR.NS', 'RADICO.NS', 'FLUOROCHEM.NS', 'NAVINFLUOR.NS', 'ALKYLAMINE.NS', 'BALAMINES.NS', 'PIIND.NS' ],
            "Consumer": ['NESTLEIND.NS', 'VBL.NS', 'POLYCAB.NS', 'ITC.NS', 'TATACONSUM.NS', 'GODREJCP.NS', 'HINDUNILVR.NS', 'TITAN.NS', 'AMBER.NS'],
            "Bank": ['SBIN.NS', 'PNB.NS', 'HDFCBANK.NS'],
            "PSU" : ['GAIL.NS', 'MGL.NS', 'IGL.NS', 'HINDCOPPER.NS', 'NATIONALUM.NS', 'COALINDIA.NS'],
            "Defence": ['PARAS.NS', 'HAL.NS', 'MAZDOCK.NS'],
            "NBFC": ['BAJFINANCE.NS', 'BAJAJFINSV.NS']
        }
    
        for key,value in list.items():
            yfinancestocktracker(key, symbols_list=value)
            time.sleep(7)
            
    with tab2:
        

        MF_SCHEME_CODE = [
            {"schemecode": 122639, "name": "Parag Parekh Flexi Cap Regular"},
            {"schemecode": 125350, "name": "Axis Small Cap Fund - Regular Plan - Growth"},
            {"schemecode": 102875, "name": "Kotak-Small Cap Fund - Growth"},
            {"schemecode": 135799, "name": "TATA Digital India Fund Regular Plan"},
            {"schemecode": 112090, "name": "Kotak Flexicap Fund Regular"},
            {"schemecode": 120841, "name": "quant Mid Cap Fund - Growth Option - Direct"},
            {"schemecode": 113177, "name": "Nippon India Small Cap Fund - Growth Plan - Growth Option"},
            {"schemecode": 146127, "name": "CANARA ROBECO SMALL CAP FUND - REGULAR PLAN - GROWTH OPTION"},
            {"schemecode": 146193, "name": "Edelweiss Small Cap Fund - Regular Plan - Growth" },
            {"schemecode": 102594, "name": "ICICI Prudential Value Discovery Fund - Growth" }
            
        ]
        for x in MF_SCHEME_CODE:
            dfC = getHistoricalMFNavData(x["schemecode"])
            dfC['nav'] = dfC['nav'].astype(float)
            st.markdown("### " + x["name"] + " [" + str(dfC["nav"].mean())+ "]")
            st.table(dfC)
            time.sleep(10)
    
if __name__ == "__main__":
    main()
