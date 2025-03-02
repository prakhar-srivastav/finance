import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from nse_ticker_code_fetcher import get_nse_symbols

# Create the ticker object for Britannia Industries

def find_pair_wise_data_for_two_point(dfs):
    from collections import defaultdict
    dataset = defaultdict(list)
    for df in dfs:
        refined_data = []
        for time, row in df.iterrows():
            min = time.hour * 60 + time.minute
            refined_data.append([min, float(row['Close'])])
        for i in range(len(refined_data)):
            for j in range(i+1, len(refined_data)):
                key = (refined_data[i][0], refined_data[j][0])
                value = refined_data[j][1] - refined_data[i][1]
                dataset[key].append(value)
    return dataset
    

def plot(daily_dfs, custom_day, to_plot = []):
    # Plot the minute-level closing price data
    df_custom = daily_dfs[custom_day]
    plt.figure(figsize=(14, 7))
    plt.plot(df_custom.index, df_custom['Close'], label='Close Price')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title(f'Britannia Industries ({ticker}.NS) Minute-Level Data for {custom_day}')
    plt.legend()
    plt.grid(True)
    for x in to_plot:
        for _, row in df_custom.iterrows():
            date = _
            break
        minutes = x.hour * 60 + x.minute
        plt.axvline(x=date.replace(hour=minutes//60, minute=minutes%60), color='r', linestyle='--')
    plt.show()

def save():
    # Save the minute-level data to a CSV file
    df_custom.to_csv(f'britannia_custom_day_{custom_day}.csv')


def get_profit_time(gap_needed, daily_dfs_list):
    dataset = find_pair_wise_data_for_two_point(daily_dfs_list)
    metadata = {}

    total = 0
    for k, data in dataset.items():
        total = len(data)
        break

    for k,data in dataset.items():
        count = 0
        for item in data:
            if item >= gap_needed:
                count += 1
        metadata[k] = count

    max_value = max(metadata.values())
    max_key = max(metadata.items(), key=lambda x: x[1])[0]

    def get_time(minute):
        hour = minute//60
        minute = minute%60
        return datetime.time(hour, minute)

    buy = get_time(max_key[0])
    sell = get_time(max_key[1])
    print(f"Max value: {max_value}, Buy: {buy}, Sell: {sell}, Confidence: {max_value/total}")
    return buy, sell, max_value/total

def get_ideal_point_for_ticker(ticker, gap_needed):
    stock = yf.Ticker("{}.NS".format(ticker))
    df_custom = stock.history(period="1mo", interval="2m")
    df_custom.index = pd.to_datetime(df_custom.index)
    dates = df_custom.index.strftime('%Y-%m-%d').unique()

    daily_dfs = {}

    for date in dates:
        daily_dfs[date] = df_custom[df_custom.index.strftime('%Y-%m-%d') == date]

    daily_dfs_list = list(daily_dfs.values())
    buy, sell, score = get_profit_time(gap_needed, daily_dfs_list)
    return buy, sell, score


def get_and_plot_ideal_point_for_ticker(ticker, gap_needed, date):
    stock = yf.Ticker("{}.NS".format(ticker))
    df_custom = stock.history(period="1mo", interval="2m")
    df_custom.index = pd.to_datetime(df_custom.index)
    dates = df_custom.index.strftime('%Y-%m-%d').unique()

    daily_dfs = {}

    for date in dates:
        daily_dfs[date] = df_custom[df_custom.index.strftime('%Y-%m-%d') == date]

    daily_dfs_list = list(daily_dfs.values())
    buy, sell, score = get_profit_time(gap_needed, daily_dfs_list)
    plot(daily_dfs, date, [buy, sell])
    return buy, sell, score


def get_and_plot_gradient_for_score(ticker):
    scores = []
    for gap_needed in range(0, 20):
        print(f"Gap Needed: {gap_needed}")
        buy, sell, score = get_ideal_point_for_ticker(ticker, gap_needed)
        scores.append(score)

    plt.figure(figsize=(10, 6))
    plt.plot(range(0, 20), scores)
    plt.xlabel('Gap Needed')
    plt.ylabel('Confidence Score')
    plt.title(f'Confidence Score vs Gap Needed for {ticker}')
    plt.grid(True)
    plt.show()


def get_gradient_for_score(ticker):
    info = []
    for gap_needed in range(0, 20):
        print(f"Gap Needed: {gap_needed}")
        buy, sell, score = get_ideal_point_for_ticker(ticker, gap_needed)
        info.append([buy, sell, score, gap_needed])
    return info
    

def get_ticker_wise_confidence():
    tickers = get_nse_symbols()
    tickers = tickers[:3]
    data = {'ticker': [], 'buy': [], 'sell': [], 'score': [], 'gap': []}
    for i in range(len(tickers)):
        ticker = tickers[i]
        print(ticker, i , '/' , len(tickers))
        try:
            info = get_gradient_for_score(ticker)
            for item in info:
                data['ticker'].append(ticker)
                data['buy'].append(item[0])
                data['sell'].append(item[1])
                data['score'].append(item[2])
                data['gap'].append(item[3])
        except Exception as e:
            print("Error processing ticker: ", ticker)
            continue
    return pd.DataFrame(data)

"""
Usecase 1
get all the sticker
for all the sticker : 
    get the confidence to gap ratio  
    
see which sticker has the highest confidence for a given gap

"""

df = get_ticker_wise_confidence()
df.to_csv("confidence.csv")