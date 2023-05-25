from kafka import KafkaProducer
import json
import time
import requests

url = "https://opensky-network.org/api/states/all"

def get_ac_info(time, state):
    return {
        'icao24': state[0],
        'callsign': state[1],
        'origin_country': state[2],
        'time_position': state[3],
        'last_contact': state[4],
        'longitude': state[5],
        'latitude': state[6],
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

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

producer = KafkaProducer(bootstrap_servers=['192.168.86.103:9092'],
                         value_serializer=json_serializer)

if __name__ == "__main__":
    while True:
        response = requests.get(url)

        time = response.json()['time']
        for data in response.json()['states']:
            print(get_ac_info(time, data))

            producer.send("adsb", get_ac_info(time, data))
        time.sleep(30)