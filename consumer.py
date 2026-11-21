from kafka import KafkaConsumer
from influxdb import InfluxDBClient
import json
import os
from kafka.errors import NoBrokersAvailable
import time

print("📥 Consumer started: listening to Kafka, running calculations, writing to InfluxDB...")

consumer = None
while consumer is None:
    try:
        consumer = KafkaConsumer(
            'finance_prices',
            bootstrap_servers=[os.getenv('KAFKA_BOOTSTRAP', 'kafka:9092')],
            # With a consumer group, offsets are committed: after a restart
            # the consumer resumes where it left off and no message is lost.
            group_id=os.getenv('KAFKA_GROUP_ID', 'influx-writer'),
            auto_offset_reset='latest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        print("✅ Connected to Kafka!")
    except NoBrokersAvailable:
        print("⏳ Kafka not ready yet, retrying in 5 seconds...")
        time.sleep(5)

db_client = InfluxDBClient(host=os.getenv('INFLUX_HOST', 'influxdb'), port=8086, database='finance_data')

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