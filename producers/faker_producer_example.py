'''Module for creating a new Kafka producer and generating fake data'''
import json
import time
import os

from faker import Faker
from kafka import KafkaProducer

from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')
SERVER = os.getenv('SERVER')

fake = Faker()

def get_location() -> dict:
    '''Method which returns a fake location, and other relevant information'''
    loc = fake.local_latlng()
    return {
        "geo_point": {
            "lat": float(loc[0]),
            "lon": float(loc[1])
        },
        "city": loc[2],
        'country': loc[3],
        "region": loc[4],
        "aircraft": fake.random.choices(["AH-64", "CH-47F", "UH-60"]),
        "rad_alt": fake.random_int(min=30000, max=35000)
    }

def json_serializer(data: list) -> json:
    '''Takes the state list and returns a dictionary containing the information'''
    return json.dumps(data).encode("utf-8")

producer = KafkaProducer(bootstrap_servers=[SERVER + ':9092'],
                         value_serializer=json_serializer)

if __name__ == "__main__":

    while True:
        location = get_location()
        print(location)
        producer.send("location", location)
        time.sleep(1)
        