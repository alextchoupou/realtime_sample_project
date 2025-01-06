import random
import time
from datetime import datetime
import json
import uuid

from confluent_kafka import SerializingProducer

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


def generate_transaction():
    sign_number = random.choice([-1, 1])
    montant = round(random.uniform(1000, 10000000), 2)

    if sign_number == -1:
        sign = "DEBIT"
        libelle = random.choice(LIBELLES_DEBIT)
    else:
        sign = "CREDIT"
        libelle = random.choice(LIBELLES_CREDIT)

    account_number = "".join([str(random.randint(0, 9)) for _ in range(9)])
    date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    transaction = {
        "id": str(uuid.uuid4()),
        "montant": montant,
        "sign": sign,
        "accountNumber": account_number,
        "libelle": libelle,
        "date": date
    }
    return transaction


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed :{err}")
    else:
        print(f"Message delivered to the {msg.topic()}[{msg.partition()}] at offset {msg.offset()}")


def main():
    topic = 'financials_operations'
    producer = SerializingProducer({
        'bootstrap.servers': 'broker:29092',
        'client.id': 'python-producer'
    })
    print("Connecting to Kafka...")
    try:
        while True:
            transaction = generate_transaction()
            raw = json.dumps(transaction)
            print(raw)
            producer.produce(topic,
                             on_delivery=delivery_report,
                             value=raw
                             )
            time.sleep(1)
    except BufferError:
        print("Buffer Error! Waiting for Kafka...")
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n Génération interrompue!!!")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
    finally:
        producer.flush()


if __name__ == "__main__":
    main()
