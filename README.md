# Real-Time Binance Data Pipeline with Kafka & PostgreSQL

This project implements a **real-time ETL pipeline** that streams live cryptocurrency data from the **Binance API**, pushes it into **Kafka (Confluent Cloud)**, and stores it in a **PostgreSQL database** for further analysis.

It’s a hands-on introduction to **data engineering with Kafka producers/consumers, APIs, and databases**.

---

## Features

* Extracts live 24-hour ticker data from **Binance**.
* Streams JSON messages to **Kafka (Confluent Cloud)**.
* Consumes Kafka messages and writes them into **PostgreSQL (Aiven Cloud)**.
* Automatically creates the `binance_24h` table if it doesn’t exist.
* Uses `.env` for **secure credential management** (excluded from Git).
* Structured **logging** for monitoring and debugging.

---

## Tech Stack

* **Python 3**
* **Kafka (Confluent Cloud)**
* **PostgreSQL (Aiven Cloud)**
* **Requests** (API calls)
* **confluent-kafka-python** (Kafka client)
* **psycopg2** (Postgres client)
* **dotenv** (environment variable management)

---

## Project Structure

```
.
├── producer.py         # Extracts Binance data and publishes to Kafka
├── consumer.py         # Consumes Kafka messages and stores them in Postgres
├── .env                # Environment variables (not tracked in Git)
├── .gitignore          # Excludes .env and other sensitive files
└── README.md           # Project documentation
```

---

## Setup & Installation

### 1. Clone the repo

```bash
git clone https://github.com/your-username/binance-kafka-pipeline.git
cd binance-kafka-pipeline
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

*(Create a `requirements.txt` with the following)*

```txt
confluent-kafka
requests
psycopg2-binary
python-dotenv
```

### 4. Configure environment variables

Create a **`.env`** file in the project root:

```ini
# Kafka
BOOTSTRAP_SERVER=pkc-xxxx.us-east1.gcp.confluent.cloud:9092
CONFLUENT_API_KEY=your_kafka_api_key
CONFLUENT_SECRET_KEY=your_kafka_secret
KAFKA_TOPIC=binance
KAFKA_GROUP=binance-group-id

# Postgres
DBNAME=your_db_name
USER=avnadmin
PASSWORD=your_password
HOST=your_postgres_host
DBPORT=your_port
```

### 5. Run the producer (Binance → Kafka)

```bash
python producer.py
```

### 6. Run the consumer (Kafka → Postgres)

```bash
python consumer.py
```

---

## Database Schema

The consumer automatically creates the following table in Postgres:

```sql
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
```

Each Kafka message inserts a new row into this table.

---

## Common Issues & Fixes

* **Password authentication failed** → Ensure you’re using the correct Postgres username (`avnadmin`) and password from Aiven.
* **Consumer “stuck”** → This usually means no new messages are available. Start the producer first so data begins flowing.

---

## Next Steps

* Add data validation before inserts.
* Stream more symbols or other Binance endpoints.
* Build a dashboard with **Power BI / Grafana**.
* Containerize with **Docker** or orchestrate with **Airflow**.

---

## License

This project is open-source and available under the [MIT License](LICENSE).

---
