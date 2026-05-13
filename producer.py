import yfinance as yf
from kafka import KafkaProducer
import json
import time
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')
print("🚀 Producer started: fetching data and sending to Kafka...")

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

while True:
    try:
        gold_price = yf.Ticker("GC=F").fast_info['last_price']
        silver_price = yf.Ticker("SI=F").fast_info['last_price']
        btc_price = yf.Ticker("BTC-USD").fast_info['last_price']
        dxy_price = yf.Ticker("DX-Y.NYB").fast_info['last_price']

        data = {
            "gold": gold_price,
            "silver": silver_price,
            "btc": btc_price,
            "dxy": dxy_price,
            "timestamp": datetime.utcnow().isoformat() 
        }

        producer.send('finance_prices', data)
        
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] 📤 [PRODUCER] Gold, Silver, BTC, and DXY data sent to Kafka.")

        time.sleep(10)

    except Exception as e:
        print(f"❌ [PRODUCER] Error: {e}")
        time.sleep(10)