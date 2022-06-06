# ---------------- CONDA BASE 3.7.11   ----------------------------
# 

import time
from matplotlib import ticker
import pyupbit
import datetime
import schedule
from fbprophet import Prophet
import requests


# ------------------ UPBIT SECRET KEY ------------------
access = "DG5thHnveYstkVpxYzVUTeNKCbiwxiLkkoya"
secret = "oJVASua4brJxyvqr0NeQyYwO19x5UWNzUMOZ"




# # ------------------ EVERY HOUR Wallet alram ------------------





# ------------------------------------------------------


# ------------------ send slack message setting ------------------
myToken = "xoxb-3004810144421-3007757608883-xZrhOMzCQF2uEJYkV2Mn"


def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
 

def dbgout(message):
    """인자로 받은 문자열을 파이썬 셸과 슬랙으로 동시에 출력한다."""    # dbGOUT 정의    strbuf 정의 ㅇㄷㄹ
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message)
    strbuf = datetime.now().strftime('[%m/%d %H:%M:%S] ') + message
    post_message(myToken,"#coinat", strbuf)

# ----------------------------------------------------------





# ------------------ 변동성 돌파전략 ------------------

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수목표가 조회"""    
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price 
  

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


# ------------------------------------------------------------------------------------------





# ------------------ GUESS END PRICE ------------------

predicted_close_price = 0
def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue
   
    print("Geuss_end_price :" , closeValue)
predict_price("KRW-BCH")
schedule.every().hour.do(lambda: predict_price("KRW-BCH"))


# ------------------------------------------------------





# ------------------ 로그인 ------------------

upbit = pyupbit.Upbit(access, secret)
print("autotrade start")


# ------------------ 시작 메세지 슬랙 전송 ------------------
post_message(myToken,"#coinat", "Start:AT_BCH_AI")


# ---------------------------------------------------------


# ------------------ 비트코인캐시 (BCH)자동매매 시작 ------------------
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BCH")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BCH", 0.5)
            current_price = get_current_price("KRW-BCH")
            if target_price < current_price and current_price < predicted_close_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BCH", krw*0.9995)
        else:
            BCH = get_balance("BCH")
            if BCH > 0.0001076:
                upbit.sell_market_order("KRW-BCH", BCH*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
# ------------------------------------------------------