import requests, os, json, time, logging
from dotenv import load_dotenv
from confluent_kafka import Producer

load_dotenv()

binance_url = "https://api.binance.com/api/v3/ticker/24hr"
symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

kafka_config = {
    "bootstrap.servers": os.getenv("BOOTSTRAP_SERVER"),
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": os.getenv("CONFLUENT_API_KEY"),
    "sasl.password": os.getenv("CONFLUENT_SECRET_KEY"),
    "broker.address.family": "v4",
    "message.send.max.retries": 5,
    "retry.backoff.ms": 500,
}

producer = Producer(kafka_config)
topic = os.getenv("KAFKA_TOPIC")

def binance_extract(symbol: str):
    params = {"symbol": symbol}
    response = requests.get(binance_url, params=params)
    response.raise_for_status()
    data = response.json()

    return data

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Delivery failed: {err}")
    else:
        logger.info(f"Delivered to {msg.topic()}[{msg.partition()}] offset {msg.offset()}")

def produce_binance_data():
    while True:
        for symbol in symbols:
            data = binance_extract(symbol)
            if data:
                producer.produce(topic, key=symbol, value=json.dumps(data), callback=delivery_report)
                producer.poll(0)
            else:
                logger.error(f"Failed to fetch data for {symbol}")
        producer.flush()
        time.sleep(5)

if __name__ == "__main__": #runner function
    produce_binance_data()
    time.sleep(10)


