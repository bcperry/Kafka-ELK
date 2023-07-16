'''Module for creating a Kafka procuder for ADSB information'''
import json
import time
import os
from kafka import KafkaProducer
import requests

from dotenv import load_dotenv


load_dotenv(dotenv_path='.env')
SERVER = os.getenv('SERVER')

URL = "https://opensky-network.org/api/states/all"

def get_ac_info(state: list):
    '''Takes the state list and returns a dictionary containing the information'''
    return {
        'icao24': state[0],
        'callsign': state[1],
        'origin_country': state[2],
        'time_position': state[3],
        'last_contact': state[4],
        'geo_point':{
            'lon': state[5],
            'lat': state[6]
            },
        'baro_altitude': state[7],
        'on_ground': state[8],
        'velocity': state[9],
        'true_track': state[10],
        'vertical_rate': state[11],
        'sensors': state[12],
        'geo_altitude': state[13],
        'squawk': state[14],
        'spi': state[15],

    }


def json_serializer(data_dict: dict) -> dict:
    '''takes a dictionary and returns a a json serializer'''
    return json.dumps(data_dict).encode("utf-8")

producer = KafkaProducer(bootstrap_servers=[SERVER + ':9092'],
                         value_serializer=json_serializer)

if __name__ == "__main__":
    while True:
        response = requests.get(URL, timeout=10)

        for data in response.json()['states']:
            producer.send("adsb", get_ac_info(data))
        print('data received')
        time.sleep(30)
