from faker import Faker
from kafka import KafkaProducer
import json
import time

from dotenv import load_dotenv
import os 

env = load_dotenv(dotenv_path='.env')
SERVER = os.getenv('SERVER')

fake = Faker()

def get_location():
    loc = fake.local_latlng()
    return {
        "location": {
            "lat": float(loc[0]),
            "lon": float(loc[1])
        },
        "city": loc[2],
        'country': loc[3],
        "region": loc[4],
        "aircraft": "AH-64",
        "rad_alt": fake.random_int(min=30000, max=35000)
    }

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

producer = KafkaProducer(bootstrap_servers=[SERVER + ':9092'],
                         value_serializer=json_serializer)

if __name__ == "__main__":
    
    while True:
        location = get_location()
        print(location)
        producer.send("location", location)
        # time.sleep(1)