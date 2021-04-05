import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, time

def plot():
    plt.style.use('fivethirtyeight')
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(14, 7))

    # Load Data

    chunksize = 10 ** 6 # chunksize for loading large csv
    pd.set_option('mode.chained_assignment', None) # dataframe option for access
    result = pd.DataFrame()
    for chunk in pd.read_csv('file name here', chunksize=chunksize): # read data
        result = pd.concat([result, chunk])


    trade_data = result.loc[result['Type'].isin([
        'TRADE AGRESSOR ON SELL',
        'TRADE AGRESSOR ON BUY'])
    ] # loc type needed data to dataframe

    UTCTime = []

    ################################## Format Time ##################################
    for index, row in trade_data.iterrows():
        try:
            row_dt = str(row['UTCDate']) + ' ' + format_UTC_time(row['UTCTime'])
            UTCTime.append(datetime.strptime(row_dt, '%Y%m%d %H%M%S.%f'))
        except:
            print(row)
            print('Invalid data format or fields missing..')
            exit(1)

    trade_data.loc[:, 'UTC'] = UTCTime # Add UTC column to existing dataframe
    ###################################### End ######################################

    #################################### Price ######################################
    for Price, data in trade_data.groupby('Type'):
        # axs[0].plot(data['UTC'], data['Price'], label=Price)
        ax1.plot(data['UTC'], data['Price'], label=Price)
        ax1.grid(True)
        ax1.set_title('Daily Prices')
        ax1.legend()
    ###################################  End  #######################################

    ################################ Accumulative ###################################
    for name, data in trade_data.groupby('Type'): # Process SELL / BUY type seperately
        acc_sum = []
        data = data.reset_index()
        for index, row in data.iterrows(): # Calculate cumulative sum for last 5 data
            quantity_sum = 0
            if index > 3:
                quarter_prices = get_quarters(row['Price'])
                target_data = data[index-4:index+1] # Last 5 data
                for tindex, trow in target_data.iterrows():
                    if trow['Price'] in quarter_prices:
                        quantity_sum += trow['Quantity'] # Accumulate quantity if price in range
            acc_sum.append(quantity_sum)
        data['Cumsum'] = acc_sum # Add cumulative sum to existing dataframe
        ax2.plot(data['UTC'], data['Cumsum'], label=name) # Plotting
        ax2.grid(True)
        ax2.set_title('Traded Volume')
        ax2.legend()
    #################################### End ######################################

    #################################### Plot #####################################
    ax1.set_ylabel('Price')
    ax2.set_ylabel('Quantity')
    plt.tight_layout()
    plt.xlabel('Dates')
    plt.gcf().autofmt_xdate()
    plt.show()

# Get Available Quarter Price
def get_quarters(price):
    offset = 0.25
    range = offset * 9
    quarter_prices = []
    while range != 0:
        quarter_prices.append(price + offset * 5 - range)
        range -= 0.25
    return quarter_prices

# Format time
def format_UTC_time(time):
    if len(str(time)) < 9:
        time = '%0*d' % (9, time)
    else:
        time = str(time)
    return time[:6] + '.' + time[6:]

if __name__ == "__main__":
    plot()