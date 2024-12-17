import pandas as pd
import json
import time

from faker import Faker
from confluent_kafka import SerializingProducer

faker = Faker()


def generate_sales_transactions():
    # user = faker.simple_profile()
    # return {
    #     "transactionId": faker.uuid4(),
    #     "productId": random.choice(["product1", "product2", "product3", "product4", "product5", "product6"]),
    #     "productName": random.choice(['laptop', 'mobile', 'tablet', 'watch', 'headphone', 'speaker']),
    #     "productCategory": random.choice(['electronic', 'fashion', 'grocery', 'home', 'beauty', 'sports']),
    #     "productPrice": round(random.uniform(10, 1000), 2),
    #     "productQuantity": random.randint(1, 10),
    #     "productBrand": random.choice(["Apple", "Samsung", "oneplus", "mi", "boat", "sony"]),
    #     "currency": random.choice(['USD', 'GBP']),
    #     "customerId": user['username'],
    #     "transactionDate": datetime.utcnow().isoformat() + "Z",
    #     "paymentMethod": random.choice(['credit_card', 'debit_card', 'online_transfer'])
    # }
    pass


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed :{err}")
    else:
        print(f"Message delivered to the {msg.topic()}[{msg.partition()}] at offset {msg.offset()}")


def normalize_data(boolean_columns, date_columns, str_colums, df):
    for col in boolean_columns:
        if col in df.columns:
            df[col] = df[col].astype(int)
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    for col in str_colums:
        if col in df.columns:
            df[col] = df[col].astype(str)
    for column in df.select_dtypes(include=['datetime64[ns]', 'datetime64', 'object']):
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            df[column] = df[column].dt.strftime('%Y-%m-%dT%H:%M:%S')  # Format ISO 8601
    return df


def main():
    topic = 'financial_operation'
    file_path = 'data/data_op.xlsx'
    producer = SerializingProducer({
        'bootstrap.servers': 'broker:29092',
        'client.id': 'python-producer'
    })
    print("Connecting to Kafka...")

    try:
        column_types = {
            "pk": str,
            "cdate": str,
            "accountcode": str,
            "accountnumber": str,
            "accountpk": str,
            "closed": bool,
            "code": str,
            "creditamount": float,
            "currencycode": str,
            "currencypk": str,
            "debitamount": float,
            "differed": bool,
            "differedcondition": str,
            "extreference": str,
            "filtrereport": bool,
            "fxrate": float,
            "globalreference": str,
            "grossamount": float,
            "grossamountacccur": float,
            "lockoperationreference": str,
            "netamount": float,
            "netamountacccur": float,
            "opeinfo": str,
            "operationtypecode": str,
            "operationtypepk": int,
            "originopecode": str,
            "originopepk": str,
            "originopetype": str,
            "paymentmeanref": str,
            "processed": bool,
            "reference": str,
            "relatedoperation": str,
            "reservationreference": str,
            "reversed": bool,
            "reversedfinancialopecode": str,
            "reversedfinancialopepk": str,
            "sign": str,
            "totalcomission": float,
            "totalcommissionacccur": float,
            "totalfracccur": int,
            "totalfiscalretention": float,
            "totalstamp": int,
            "totaltaf": int,
            "totalvat": int,
            "totalvatacccur": int,
            "tradedate": str,
            "unitcode": str,
            "unitpk": str,
            "udate": str,
            "valuedate": str,
            "versionnum": int,
            "totalcss": int,
            "totalcssacccur": int,
            "mailsent": int,
            "smssent": int,
            "whatsappsent": int,
            "force": int
        }
        df = pd.read_excel(file_path, dtype=column_types)
        df = df.drop(columns=["differed", "differedcondition", "extreference", "globalreference", "paymentmeanref"])
        if df.empty:
            print("Le fichier Excel est vide.")
        else:
            boolean_columns = ["closed", "processed", "reversed",
                               "mailsent", "smssent", "filtrereport", "whatsappsent", "force"]
            date_columns = ["cdate", "udate", "valuedate", "tradedate"]
            str_columns = ["lockoperationreference", "opeinfo", "operationtypecode", "originopepk",
                           "reversedfinancialopecode", "reversedfinancialopepk"]
            df = normalize_data(boolean_columns, date_columns, str_columns, df)
            df = df.fillna("")
            df = df.replace({None: "", "nan": ""})
            df = df.where(pd.notnull(df), None)
            for index, row in df.iterrows():

                # Convertir la ligne en JSON
                raw = json.dumps(row.to_dict(), ensure_ascii=False, indent=4)
                print(f"Ligne {index + 1} :\n{raw}")
                producer.produce(topic,
                                 key=row.get('pk'),
                                 value=raw,
                                 on_delivery=delivery_report
                                 )
                producer.poll(0)
                time.sleep(3)

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{file_path}' est introuvable.")
    except BufferError:
        print("Buffer Error! Waiting...")
        time.sleep(0.5)
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        # transaction['totalAmount'] = transaction['productPrice'] * transaction['productQuantity']

    finally:
        producer.flush()

        producer.flush(0)


if __name__ == "__main__":
    main()
