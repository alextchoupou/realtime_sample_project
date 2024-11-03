import random
import json
import time
from datetime import datetime

from faker import Faker
from confluent_kafka import SerializingProducer

faker = Faker()


def generate_sales_transactions():
    user = faker.simple_profile()
    return {
        "transactionId": faker.uuid4(),
        "productId": random.choice(["product1", "product2", "product3", "product4", "product5", "product6"]),
        "productName": random.choice(['laptop', 'mobile', 'tablet', 'watch', 'headphone', 'speaker']),
        "productCategory": random.choice(['electronic', 'fashion', 'grocery', 'home', 'beauty', 'sports']),
        "productPrice": round(random.uniform(10, 1000), 2),
        "productQuantity": random.randint(1, 10),
        "productBrand": random.choice(["Apple", "Samsung", "oneplus", "mi", "boat", "sony"]),
        "currency": random.choice(['USD', 'GBP']),
        "customerId": user['username'],
        "transactionDate": datetime.utcnow().isoformat() + "Z",
        "paymentMethod": random.choice(['credit_card', 'debit_card', 'online_transfer'])
    }


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed :{err}")
    else:
        print(f"Message delivered to the {msg.topic()}[{msg.partition()}] at offset {msg.offset()}")


def main():
    topic = 'financial_transaction'
    producer = SerializingProducer({
        'bootstrap.servers': 'localhost:9092',
        'key.serializer': lambda v, ctx: str(v).encode('utf-8'),
        'value.serializer': lambda v, ctx: json.dumps(v).encode('utf-8')
    })
    current_time = datetime.now()

    while (datetime.now() - current_time).seconds < 120:
        try:
            transaction = generate_sales_transactions()
            transaction['totalAmount'] = transaction['productPrice'] * transaction['productQuantity']
            print(transaction)

            producer.produce(topic,
                             key=transaction['transactionId'],
                             value=json.dumps(transaction),
                             on_delivery=delivery_report
                             )
            producer.poll(0)

            time.sleep(1)

        except BufferError:
            print("Buffer Error! Waiting...")
            time.sleep(0.5)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
