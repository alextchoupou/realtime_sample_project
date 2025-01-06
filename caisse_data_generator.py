import random
from datetime import datetime, timedelta
import json
import time

# Constants
NUM_CAISSES = 15
MAX_AMOUNT = 10000

# Possible geographical locations (latitude, longitude)
LOCATIONS = [
    {"lat": 48.8566, "lon": 2.3522},  # Paris
    {"lat": 40.7128, "lon": -74.0060},  # New York
    {"lat": 51.5074, "lon": -0.1278},  # London
    {"lat": 35.6895, "lon": 139.6917},  # Tokyo
    {"lat": 34.0522, "lon": -118.2437},  # Los Angeles
    {"lat": 37.7749, "lon": -122.4194},  # San Francisco
    {"lat": 41.8781, "lon": -87.6298},  # Chicago
    {"lat": -33.8688, "lon": 151.2093},  # Sydney
    {"lat": 55.7558, "lon": 37.6173},  # Moscow
    {"lat": -23.5505, "lon": -46.6333},  # São Paulo
    {"lat": 19.0760, "lon": 72.8777},  # Mumbai
    {"lat": 39.9042, "lon": 116.4074},  # Beijing
    {"lat": 52.5200, "lon": 13.4050},  # Berlin
    {"lat": 28.6139, "lon": 77.2090},  # New Delhi
    {"lat": 1.3521, "lon": 103.8198},  # Singapore
    {"lat": 45.4642, "lon": 9.1900}  # Milan
]

# Possible libellés for operations
LIBELLES_DEBIT = [
    "REGULARISATION_DEBIT_COMPTE_CLIENT",
    "RETRAIT_MOBILE_CLIENT",
    "VIREMENT EMIS INTERBANCAIRE AGENCE",
    "ACHAT_CARTE_PREPAYEE_PAR_DEBIT_COMPTE_CLIENT",
    "RETRAIT CHEQUE CLIENT",
    "REGLEMENT_FOURNISSEURS",
    "PAIEMENT_FACTURE",
    "ACHAT_MATERIEL_BUREAU"
]

LIBELLES_CREDIT = [
    "VIREMENT RECU",
    "DEPOT_MOBILE_CLIENT",
    "VERSEMENT ESPECE GUICHET",
    "REMISE_CHEQUE_INTERBANCAIRE",
    "REGULARISATION_CREDIT_COMPTE_CLIENT",
    "POSITIONNEMENT_VIREMENT_RECU",
    "REMBOURSEMENT_PRET",
    "GAIN_LOTTERIE"
]


# Generate random caisses

def generate_caisses(num_caisses):
    unique_locations = random.sample(LOCATIONS, num_caisses)
    return [
        {
            "code": f"C{i:03}",
            "location": unique_locations[i - 1],
            "open": True
        }
        for i in range(1, num_caisses + 1)
    ]


# Generate a single operation for a random caisse
def generate_operation(caisses):
    caisse = random.choice(caisses)
    date = datetime.now()
    sign = random.choice(["Debit", "Credit"])
    libelle = random.choice(LIBELLES_DEBIT if sign == "Debit" else LIBELLES_CREDIT)
    operation = {
        "caisse": caisse["code"],
        "amount": round(random.uniform(10, MAX_AMOUNT), 2),
        "sign": sign,
        "libelle": libelle,
        "date": date.isoformat()
    }
    return operation


# Generate a closure or fermeture for a random caisse
def generate_closure_or_fermeture(caisses):
    caisse = random.choice(caisses)
    date = datetime.now().isoformat()
    state = random.choice(["Cloture", "Fermeture"])
    balance = round(random.uniform(-5000, 20000), 2)
    caisse["open"] = state == "Cloture"  # Update open status based on state
    closure = {
        "caisse": caisse["code"],
        "state": state,
        "date": date,
        "balance": balance
    }
    return closure


# Generate continuous data
def generate_continuous_data(caisses):
    while True:
        if random.random() < 0.8:  # 80% chance to generate an operation
            data = generate_operation(caisses)
        else:  # 20% chance to generate a closure or fermeture
            data = generate_closure_or_fermeture(caisses)
        print(json.dumps(data, indent=2))  # Simulate sending to Kafka
        time.sleep(1)  # Wait for 1 second before generating the next data point


# Main execution
if __name__ == "__main__":
    caisses = generate_caisses(NUM_CAISSES)
    generate_continuous_data(caisses)
