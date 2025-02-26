import random
import psycopg2
import time
from datetime import datetime
import json
import uuid

from confluent_kafka import SerializingProducer, KafkaError

LIBELLES_DEBIT = [
    "REGULARISATION_DEBIT_COMPTE_CLIENT",
    "RETRAIT_MOBILE_CLIENT",
    "VIREMENT EMIS INTERBANCAIRE AGENCE",
    "ACHAT_CARTE_PREPAYEE_PAR_DEBIT_COMPTE_CLIENT",
    "RETRAIT CHEQUE CLIENT",
    "REGLEMENT_FOURNISSEURS"
]

LIBELLES_CREDIT = [
    "VIREMENT RECU",
    "DEPOT_MOBILE_CLIENT",
    "VERSEMENT ESPECE GUICHET",
    "REMISE_CHEQUE_INTERBANCAIRE",
    "REGULARISATION_CREDIT_COMPTE_CLIENT",
    "POSITIONNEMENT_VIREMENT_RECU"
]

# Limite pour des montants considérés comme suspects
HIGH_AMOUNT_THRESHOLD = 5000000

# Dictionnaire pour simuler les transactions rapides pour certains comptes
SUSPICIOUS_ACCOUNTS = {str(random.randint(100000000, 999999999)): 0 for _ in range(3)}

def generate_transaction():
    # Détermine si cette transaction est normale ou suspecte
    is_fraud = random.choice([False, True])
    sign_number = random.choice([-1, 1])
    montant = round(random.uniform(1000, HIGH_AMOUNT_THRESHOLD * (10 if is_fraud else 1)), 2)
    account_number = "".join([str(random.randint(0, 9)) for _ in range(9)])

    # Si la fraude concerne une fréquence élevée
    if is_fraud and random.choice([True, False]):
        account_number = random.choice(list(SUSPICIOUS_ACCOUNTS.keys()) or [account_number])
        SUSPICIOUS_ACCOUNTS[account_number] = SUSPICIOUS_ACCOUNTS.get(account_number, 0) + 1

    if sign_number == -1:
        sign = "DEBIT"
        libelle = random.choice(LIBELLES_DEBIT)
    else:
        sign = "CREDIT"
        libelle = random.choice(LIBELLES_CREDIT)

    date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    transaction = {
        "id": str(uuid.uuid4()),
        "montant": montant,
        "sign": sign,
        "accountNumber": str(account_number),
        "libelle": libelle,
        "date": date,
        "is_fraud": is_fraud
    }
    return transaction


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed :{err}")
    else:
        print(f"Message delivered to the {msg.topic()}[{msg.partition()}] at offset {msg.offset()}")

def create_table(conn):
    cursor = conn.cursor()

    cursor.execute(
        """
       CREATE TABLE IF NOT EXISTS transactions (
            id UUID PRIMARY KEY,
            montant NUMERIC(20, 2),
            sign VARCHAR(10),
            account_number VARCHAR(9),
            libelle VARCHAR(255),
            date TIMESTAMP,
            is_fraud BOOLEAN
        );
        """)
    cursor.close()
    conn.commit()


def insert_transaction_to_db(connection, transaction):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO transactions (id, montant, sign, account_number, libelle, date, is_fraud)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            transaction["id"],
            transaction["montant"],
            transaction["sign"],
            transaction["accountNumber"],
            transaction["libelle"],
            datetime.fromisoformat(transaction["date"]).strftime('%Y-%m-%d %H:%M:%S'),
            transaction["is_fraud"]
        ))
        cursor.close()
        connection.commit()

def main():
    conn = psycopg2.connect(
        host='postgres_deb',
        database='bamboo_db',
        user='postgres',
        password='postgres',
        port=5432
    )
    topic = 'financials_operations'
    producer = SerializingProducer({
        'bootstrap.servers': 'broker:29092',
        'client.id': 'python-producer'
    })
    # try:
    #     create_table(conn)
    #     print("Creating table...")
    # except psycopg2.Error as e:
    #     print(f"Erreur lors de la connexion à PostgreSQL : {e}")

    # print("Connecting to Kafka...")
    try:
        while True:
            transaction = generate_transaction()
            print("Inserting transaction...")
            print(transaction)
            # try:
            #     insert_transaction_to_db(conn, transaction)
            # except Exception as e:
            #     print(f"Erreur lors de l'insertion : {e}")
            raw = json.dumps(transaction)
            print(raw)
            producer.produce(topic, on_delivery=delivery_report, value=raw)
            # Introduit des délais plus courts pour simuler les transactions rapides
            sleep_time = 0.1 if transaction["is_fraud"] and random.choice([True, False]) else 1
            time.sleep(sleep_time)
    except BufferError:
        print("Buffer Error! Waiting for Kafka...")
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n Génération interrompue!!!")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
    except KafkaError as e:
        print(f"Erreur Kafka : {e}")
        producer.flush()
        time.sleep(5)
    finally:
        producer.flush()


if __name__ == "__main__":
    main()
