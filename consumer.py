from kafka import KafkaConsumer
from influxdb import InfluxDBClient
import json

print("📥 Consumer started: listening to Kafka, running calculations, writing to InfluxDB...")

consumer = KafkaConsumer(
    'finance_prices',
    bootstrap_servers=['kafka:29092'],
    auto_offset_reset='latest', 
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

db_client = InfluxDBClient(host='influxdb', port=8086, database='finance_data')

for message in consumer:
    try:
        data = message.value
        
        gold = data['gold']
        silver = data['silver']
        btc = data['btc']
        dxy = data['dxy']
        
        # Only basic ratio calculation
        gs_ratio = gold / silver
        
        json_body = [
            {
                "measurement": "market_metrics",
                "time": data['timestamp'],
                "fields": {
                    "gold": float(gold),
                    "silver": float(silver),
                    "btc": float(btc),
                    "dxy": float(dxy),
                    "gs_ratio": float(gs_ratio)
                }
            }
        ]
        
        db_client.write_points(json_body)
        
        hour = data['timestamp'][11:19]
        print(f"[{hour}] 💾 [CONSUMER] Written to database -> Gold/Silver Ratio: {gs_ratio:.2f}")
        
    except Exception as e:
        print(f"❌ [CONSUMER] Error: {e}")