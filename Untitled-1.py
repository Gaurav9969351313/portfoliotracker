
import pandas as pd
import requests
from nselib import capital_market

# del_data = capital_market.price_volume_and_deliverable_position_data(symbol='SBIN', period='1W')
# del_data[["Symbol", "Date", "ClosePrice", "%DlyQttoTradedQty"]]


# nifty_50_list = capital_market.nifty50_equity_list()
# nifty_50_list.tail(5)

vix_data = capital_market.india_vix_data(period='1W')
vix_data[["TIMESTAMP", "INDEX_NAME", "VIX_PTS_CHG", "VIX_PERC_CHG" ]]



indices_data = capital_market.market_watch_all_indices()
indices_data[["index", "last", "variation", "percentChange", "advances", "declines", "perChange30d","oneWeekAgo", "oneMonthAgo"]]


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

def fii_dii_trading_activity():
    """
    FII and DII trading activity of the day in data frame
    :return: pd.DataFrame
    """
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    data_json = nse_urlfetch(url).json()
    data_df = pd.DataFrame(data_json)
    return data_df

fii_dii_data = fii_dii_trading_activity()


bhav_del = capital_market.bhav_copy_with_delivery('12-01-2024')
NIFTY_500_df = pd.read_csv("https://archives.nseindia.com/content/indices/ind_nifty500list.csv")
NIFTY_500_data_df = NIFTY_500_df[['Company Name', 'Industry', 'Symbol']]

NIFTY_500_data_df.columns = NIFTY_500_data_df.columns.str.upper()

merged_df = pd.merge(NIFTY_500_data_df, bhav_del, on='SYMBOL', how='left')
merged_df['DELIV_PER'] = pd.to_numeric(merged_df['DELIV_PER'], errors='coerce')

df_sorted = merged_df.sort_values(by='DELIV_PER', ascending=False)
filtered_df = df_sorted[df_sorted['SERIES'] == 'EQ']

filtered_df = filtered_df[["SYMBOL", "CLOSE_PRICE", "PREV_CLOSE", "DELIV_PER"]]





