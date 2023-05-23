from faker import Faker
from kafka import KafkaProducer
import json
import time

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
        "region": loc[4]
    }

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

producer = KafkaProducer(bootstrap_servers=['192.168.86.103:9092'],
                         value_serializer=json_serializer)

if __name__ == "__main__":
    while True:
        location = get_location()
        print(location)
        producer.send("location", location)
        # time.sleep(1)