import os
from dotenv import load_dotenv
from confluent_kafka import Consumer, KafkaException
from json import loads
import psycopg2
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
conf = {
	'bootstrap.servers': os.getenv('BOOTSTRAP_SERVER'),
	'security.protocol': 'SASL_SSL',
	'sasl.mechanisms': 'PLAIN',
	'sasl.username': os.getenv('CONFLUENT_API_KEY'),
	'sasl.password': os.getenv('CONFLUENT_SECRET_KEY'),
	'group.id': os.getenv('KAFKA_GROUP', 'binance-group-id'),
	'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
topic = os.getenv('KAFKA_TOPIC')
consumer.subscribe([topic])
logger.info(f"Consumer subscribed to topic {topic}")

# Postgres Setup
dbname =  os.getenv('DBNAME')
user = 'avnadmin'
port = os.getenv('DBPORT')
password = os.getenv('PASSWORD')
host = os.getenv('HOST')
schema = 'public'

conn = None
cur = None

try:
	conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
	logger.info("Connected to Postgres")
	
	conn.autocommit = True
	cur = conn.cursor()
	
	cur.execute("""
    CREATE TABLE IF NOT EXISTS public.binance_24h (
        symbol                  TEXT    NOT NULL,
        pricechange             NUMERIC NOT NULL,
        pricechangepercentage   NUMERIC NOT NULL,
        openprice               NUMERIC NOT NULL,
        closeprice              NUMERIC NOT NULL,
        highprice               NUMERIC NOT NULL,
        lowprice                NUMERIC NOT NULL,
        volume                  NUMERIC NOT NULL
    );
""")	

	logger.info("PostgreSQL table ready")
except Exception as e:
	logger.error(f"PostgreSQL setup error: {e}")
	cur=None

try:
	while True:
		msg = consumer.poll(1.0)
		if msg is None:
			continue
		if msg.error():
			raise KafkaException(msg.error())
		
		try:
			data = loads(msg.value().decode('utf-8'))
			cur.execute(
				"""
                INSERT INTO public.binance_24h
                (symbol, pricechange, pricechangepercentage, openprice, closeprice, highprice, lowprice, volume)
                VALUES (%(symbol)s, %(priceChange)s, %(priceChangePercent)s, %(openPrice)s, %(prevClosePrice)s,
                        %(highPrice)s, %(lowPrice)s, %(volume)s)
				""",
				data
			)
		except Exception as e:
			logger.error(f"Error processing message: {e}")

except KeyboardInterrupt:
	pass
finally:
	consumer.close()
	if cur:
		cur.close()
	if conn:
		conn.close()