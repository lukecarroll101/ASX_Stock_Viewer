import pandas as pd
import datetime as dt
from pandas_datareader import data as pdr
import yfinance as yf

def StockGrapher(stocksInput, startDateInput,endDateInput):
    startDateTemp = startDateInput.split("/")
    endDateTemp = endDateInput.split("/")

    endDate = dt.datetime(int(endDateTemp[2]), int(endDateTemp[1]), int(endDateTemp[0]))
    startDate = dt.datetime(int(startDateTemp[2]), int(startDateTemp[1]), int(startDateTemp[0]))

    stocksInputL = stocksInput.split(",")
    stocks = [i.upper().strip() + ".AX" for i in stocksInputL]

    yf.pdr_override()
    df = pdr.get_data_yahoo(stocks, startDate, endDate)
    # pg = yf.Ticker(stocksInput)
    current = df.Close.iloc[-1]
    previous = df.Close.iloc[-2]
    daily_change = current - previous
    daily_change_percentage = round(daily_change / previous * 100, 2)

    return df.Close, daily_change_percentage
