from kafka import KafkaProducer
import json
import time
import requests

import asyncio
import json

from signalr_async.net import Hub
from signalr_async.net.client import SignalRClient

import zlib
import base64
import json

def parse_data(text, zipped=True):
    """Parse json and jsonStream as returned by livetiming.formula1.com

    This function can only pass one data entry at a time, not a whole response.
    Timestamps and data need to be separated before and only the data must be passed as a string to be parsed.

    Args:
        text (str): The string which should be parsed
        zipped (bool): Whether or not the text is compressed. This is the case for '.z' data (e.g. position data=)

    Returns:
        Depending on data of which page is parsed:
            - a dictionary created as a result of loading json data
            - a string
    """
    if text[0] == '{':
        return json.loads(text)
    if text[0] == '"':
        text = text.strip('"')
    if zipped:
        text = zlib.decompress(base64.b64decode(text), -zlib.MAX_WBITS)
        return parse_data(text.decode('utf-8-sig'))
    logging.warning("Couldn't parse text")
    return text

def merge(destination, source):
    if isinstance(destination, list):
        for key, value in source.items():
            if isinstance(value, dict):
                ik = int(key)
                while len(destination) <= ik:
                    destination.append({})
                merge(destination[int(key)], value)
            else:
                destination[int(key)] = value
    elif isinstance(destination, dict):
        for key, value in source.items():
            if isinstance(value, dict):
                merge(destination.setdefault(key, {}), value)
            else:
                destination[key] = value

    return destination

class F1SignalRClient(SignalRClient):
    driver_list = {}
    timing_data = {}
    session_data = {}
    session_info = {}

    def LapCount(self, lc):
        pass

    def SessionData(self, session_data):
        print('SessionData')
        producer.send("SessionData", session_data)
        # merge(self.session_data, session_data)

    def SessionInfo(self, session_info):
        print('SessionInfo')
        producer.send("SessionInfo", session_info)
        # merge(self.session_info, session_info)

    def DriverList(self, drivers):
        print('DriverList')
        producer.send("DriverList", drivers)
        # merge(self.driver_list, drivers)

    def TimingData(self, timing):
        print('TimingData')
        producer.send("TimingData", timing)





        # merge(self.timing_data, timing)

        # for driver_number in timing["Lines"]:
        #     driver = self.driver_list[driver_number]
        #     driver_timing = self.timing_data["Lines"][driver_number]
        #     gap = ''
        #     color = driver['TeamColour']
        #     pos = driver_timing['Position']
        #     if not color:
        #         color = 'ffffff'

        #     if self.session_info['Type'] == "Qualifying":
        #         current_part = int(self.timing_data['SessionPart'])
        #         current_entries = self.timing_data['NoEntries'][current_part - 1]
        #         if driver_timing['Position'] == '1':
        #             gap = driver_timing['BestLapTimes'][current_part - 1]['Value']
        #         elif int(driver_timing['Position']) > current_entries:
        #             gap = 'KO'
        #         else:
        #             gap = driver_timing['Stats'][current_part - 1]['TimeDiffToFastest']
        #     elif self.session_info['Type'] == "Practice":
        #         if 'TimeDiffToFastest' in driver_timing:
        #             gap = driver_timing['TimeDiffToFastest']
        #         if driver_timing['Position'] == '1':
        #             gap = driver_timing['BestLapTime']['Value']
        #     elif self.session_info['Type'] == "Race":
        #         if 'GapToLeader' in driver_timing:  # race
        #             print("GapToLeader")
        #             gap = driver_timing['GapToLeader']

    # def CarData(self, data):
    #     data = parse_data(data)
    #     print('test')
    #     producer.send("F1", data)
    #     print('test')
    #     # print('CarData')
    #     # merge(self.driver_list, drivers)

    def Position(self, data):
        data = parse_data(data)
        producer.send("Position", parse_data(data))
        # print('Position')
        # merge(self.driver_list, drivers)

    async def _process_message(self, message):

        # TODO: Parse the .z messages
        # print(message)
        if hasattr(message, "result"):
            for k in message.result:
                # print(k)
                if hasattr(self, k):
                    getattr(self, k)(message.result[k])
                elif hasattr(self, k[:-2]):
                    getattr(self, k[:-2])(message.result[k])
                # else:
                    # producer.send("F1", {k: message.result[k]})
        # elif hasattr(message, "arguments"):
        #     k, v, t = message.arguments
        #     if hasattr(self, k):
        #         getattr(self, k)(v)
        #     else:
        #         producer.send("F1", {k: v})
        #         # print(k, v)


_connection_url = 'https://livetiming.formula1.com/signalr'
hub = Hub("streaming")


async def run_client():
    async with F1SignalRClient(
            _connection_url,
            [hub],
            keepalive_interval=5,
    ) as client:
        await hub.invoke("Subscribe", ["Heartbeat", "CarData.z", "Position.z",
                       "ExtrapolatedClock", "TopThree", "RcmSeries",
                       "TimingStats", "TimingAppData",
                       "WeatherData", "TrackStatus", "DriverList",
                       "RaceControlMessages", "SessionInfo",
                       "SessionData", "LapCount", "TimingData"])
        await client.wait(timeout=5)
        
        #commented after
    #     await asyncio.gather(
    #     run_client()
    # )
    



def json_serializer(data):
    return json.dumps(data).encode("utf-8")

producer = KafkaProducer(bootstrap_servers=['192.168.86.103:9092'],
                         value_serializer=json_serializer)

if __name__ == "__main__":
    asyncio.run(
        run_client()
    )
    
    