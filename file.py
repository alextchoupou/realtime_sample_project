import random
from datetime import datetime

from faker import Faker
from confluent_kafka import SerializingProducer


faker =  Faker()


def generate_sales_transactions():
    user = faker.simple_profile()
    return {
        "transactionId": faker.uuid4(),
        "productId": random.choice(["product1", "product2", "product3", "product4", "product5", "product6"]),
        "productName": random.choice(['laptop', 'mobile', 'tablet', 'watch', 'headphone', 'speaker']),
        "productCategory": random.choice(['electronic', 'fashion', 'grocery', 'home', 'beauty', 'sports']),
        "productPrice": round(random.uniform(10, 1000), 2),
        "productQuantity": random.randint(1, 10),
        "productBrand": random.choice("Apple", "Samsung", "oneplus", "mi", "boat", "sony"),
        "currency": random.choice(['USD','GBP']),
        "customerId": user['username'],
        "transactionDate": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
        "paymentMethod": random.choice(['credit_card', 'debit_card', 'online_transfer'])
    }