import time
from datetime import datetime, timedelta

import nselib
import pandas as pd
import requests
import streamlit as st
import yfinance as yf
from nselib import capital_market, derivatives

st.set_page_config(layout="wide")

header = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/111.0.0.0 Safari/537.36",
    "Sec-Fetch-User": "?1", "Accept": "*/*", "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate",
    "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
    }

def nse_urlfetch(url):
    r_session = requests.session()
    nse_live = r_session.get("http://nseindia.com", headers=header)
    return r_session.get(url, headers=header)

def get_previous_working_day():
    today = datetime.now()

    one_day = timedelta(days=1)
    previous_day = today - one_day

    while previous_day.weekday() in [5, 6]:  # 5 is Saturday, 6 is Sunday
        previous_day -= one_day

    formatted_date = previous_day.strftime("%d-%m-%Y")
    
    return formatted_date

def fii_dii_trading_activity():
    """
    FII and DII trading activity of the day in data frame
    :return: pd.DataFrame
    """
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    data_json = nse_urlfetch(url).json()
    data_df = pd.DataFrame(data_json)
    return data_df

def getNifty500DelPerc():
    bhav_del = capital_market.bhav_copy_with_delivery(get_previous_working_day())
    NIFTY_500_df = pd.read_csv("https://archives.nseindia.com/content/indices/ind_nifty500list.csv")
    NIFTY_500_data_df = NIFTY_500_df[['Company Name', 'Industry', 'Symbol']]

    NIFTY_500_data_df.columns = NIFTY_500_data_df.columns.str.upper()

    merged_df = pd.merge(NIFTY_500_data_df, bhav_del, on='SYMBOL', how='left')
    merged_df['DELIV_PER'] = pd.to_numeric(merged_df['DELIV_PER'], errors='coerce')

    df_sorted = merged_df.sort_values(by='DELIV_PER', ascending=False)
    filtered_df = df_sorted[df_sorted['SERIES'] == 'EQ']

    filtered_df = filtered_df[["SYMBOL", "CLOSE_PRICE", "PREV_CLOSE", "DELIV_PER"]]
    return filtered_df

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
    
def getAvgVolume(symbol_list, noofdays):
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=noofdays)).strftime('%Y-%m-%d')
    stock_data = yf.download(symbol_list, start=start_date, end=end_date)
    volume_df = stock_data["Volume"]
    average_volume_df = volume_df.mean().to_frame()
    average_volume_df.columns = [f"{noofdays}_Days_Avg_volume"]
    average_volume_df = average_volume_df.rename_axis('Symbol').reset_index()
    return average_volume_df

def main():
    tab1, tab2, tab3 = st.tabs(["Stocks",  "Reports", "Mutual Funds"])
    with tab1:
        symbol_list = {
            "Priority ETF": ['ALPHA.NS', 'MON100.NS', 'MAFANG.NS', 'MOVALUE.NS', 'ITBEES.NS', 'MOM100.NS', 'MIDSMALL.NS', 'ICICIB22.NS', 'SETFNN50.NS', 'MID150BEES.NS' ],
            "ETF": ['SILVERBEES.NS', 'BANKBEES.NS', 'BANKETF.NS', 'GOLDBEES.NS'],
            "Indices": ['^NSEI', '^NSEBANK', '^BSESN', '^NSEMDCP50', '^CNXIT', '^DJI' ], # '^CNXMID', '^CNXSMALL', 'NIFTYSMLCAP250.NS'
            "Monopoly": ['BSE.NS', 'HAL.NS', 'MCX.NS', 'POLYCAB.NS', 'CAMS.NS', 'CDSL.NS', 'ASIANPAINT.NS', 'PIDILITIND.NS',  'DMART.NS', 'IRCTC.NS', 'IRFC.NS' ],
            "Monopoly Small and Midcap": ['SULA.NS', 'ASAHIINDIA.NS', 'MAZDOCK.NS', 'PRAJIND.NS', 'BALKRISIND.NS', 'HINDZINC.NS', 'HINDCOPPER.NS'],
            "Monopoly Others": ['SUPREMEIND.NS', 'ANGELONE.NS', 'CENTURYPLY.NS', 'ASTRAL.NS'],
            "EV": ['BHEL.NS', 'JBMA.NS', 'OLECTRA.NS', 'M&M.NS', 'TATAMTRDVR.NS', 'DIXON.NS'],
            "IT": ['WIPRO.NS', 'HCLTECH.NS', 'LTIM.NS','TATAELXSI.NS', 'INFY.NS', 'TCS.NS'],
            "Hospitals": ['NH.NS', 'FORTIS.NS'],
            "Speciality Chemicals": ['SRF.NS', 'GALAXYSURF.NS','NAVINFLUOR.NS', 'RADICO.NS', 'FLUOROCHEM.NS', 'NAVINFLUOR.NS', 'ALKYLAMINE.NS', 'BALAMINES.NS', 'PIIND.NS' ],
            "Consumer": ['NESTLEIND.NS', 'VBL.NS', 'POLYCAB.NS', 'ITC.NS', 'TATACONSUM.NS', 'GODREJCP.NS', 'HINDUNILVR.NS', 'TITAN.NS', 'AMBER.NS'],
            "Bank": ['SBIN.NS', 'PNB.NS', 'HDFCBANK.NS'],
            "PSU" : ['GAIL.NS', 'MGL.NS', 'IGL.NS', 'HINDCOPPER.NS', 'NATIONALUM.NS', 'COALINDIA.NS'],
            "Defence": ['PARAS.NS', 'HAL.NS', 'MAZDOCK.NS'],
            "NBFC": ['BAJFINANCE.NS', 'BAJAJFINSV.NS']
        }
    
        # for key,value in list.items():
        #     yfinancestocktracker(key, symbols_list=value)
        #     time.sleep(3)
        
        for key, value in symbol_list.items():
            stock_data_all = yf.download(value, period='7d', interval='1d')
            close_prices = stock_data_all['Close']
            close_prices = close_prices.reset_index()
            percentage_difference = (close_prices.iloc[:, 1:].pct_change() * 100).dropna()
            percentage_difference.loc['% Change (5 Days)'] = percentage_difference.sum()
            percentage_difference["Date"] = close_prices["Date"]
            date_column = percentage_difference.pop('Date')
            percentage_difference.insert(0, 'Date', date_column)
            st.markdown("### " + key)
            st.dataframe(percentage_difference)
            time.sleep(2)
            
        signals = []
        for key, value in symbol_list.items():
            volume_15_day_avg_df = getAvgVolume(value, 15)
            volume_today_df = getAvgVolume(value, 1)

            volume_df = pd.merge(volume_today_df, volume_15_day_avg_df, on='Symbol')

            volume_df.loc[volume_df['1_Days_Avg_volume'] < volume_df['15_Days_Avg_volume'], 'signal'] = ''
            volume_df.loc[volume_df['1_Days_Avg_volume'] > volume_df['15_Days_Avg_volume'], 'signal'] = 'BUY'

            volume_df = volume_df[volume_df["signal"] == "BUY"]
            volume_df['PERC_CHANGE'] = ((volume_df['1_Days_Avg_volume'] - volume_df['15_Days_Avg_volume'])/volume_df['1_Days_Avg_volume'])*100
            
            signals.append(volume_df.to_dict(orient='records'))

        signals = [item for sublist in signals for item in sublist]
        signals_df = pd.DataFrame(signals)
        signals_df = signals_df.sort_values(by='PERC_CHANGE', ascending=False)
        
        st.markdown("#### BUY Signals (Comapred last 15 days Volume With Todays Volume)")
        st.dataframe(signals_df)
        
                            
    with tab2:
        print("Inside reports")
        col1,col2,col3 = st.columns(3)
        with col1:
            st.markdown("#### India VIX")
            vix_data = capital_market.india_vix_data(period='1W')
            vix_data = vix_data[["TIMESTAMP", "INDEX_NAME", "VIX_PTS_CHG", "VIX_PERC_CHG" ]]
            st.dataframe(vix_data)
        with col2:
            st.markdown("#### FII / DII Activity")
            fii_dii_data = fii_dii_trading_activity()
            st.dataframe(fii_dii_data)
        with col3:
            st.markdown("#### Nifty 500 EQ Series Percentage Delivery")
            nifty_50_perc_del = getNifty500DelPerc()
            st.dataframe(nifty_50_perc_del)
        
        
        st.markdown("#### FII Stats")
        derivatives_fii_stats = derivatives.fii_derivatives_statistics(get_previous_working_day())
        derivatives_fii_stats = derivatives_fii_stats[["fii_derivatives", "buy_value_in_Cr" ,"sell_value_in_Cr"]]
        st.dataframe(derivatives_fii_stats)

        st.markdown("#### Participant Wise Trading Volume")
        part_trade_volume = derivatives.participant_wise_trading_volume(get_previous_working_day())
        st.dataframe(part_trade_volume)

        st.markdown("#### Participant Wise Open Interest")
        part_open_interest = derivatives.participant_wise_open_interest(get_previous_working_day())
        st.dataframe(part_open_interest)
        
    with tab3:
        
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
            time.sleep(3)
            
    
        
    
if __name__ == "__main__":
    main()
