from pygnmi.client import gNMIclient
from getpass import getpass
import json
from google.protobuf.json_format import MessageToDict, MessageToJson
import base64
import pandas as pd

def get_connection(router):
    # Connect to device

    user = "admin"
    passwd = getpass("Enter router password:")
    try:
        gc = gNMIclient(target=(router, 57400), username=user, password=passwd, insecure=True)
        print("Successfully connected to", router)
        
    except Exception as error:
        print("Failed to connect to", router, ":", error)
        pass
    return gc

def proto_to_dict(pb_msg):
    """
    Convert a protobuf message (the `resp` you printed) into a plain Python dict.
    """
    return MessageToDict(pb_msg, preserving_proto_field_name=True)


def get_stats(gc):
    with gc:
        # Subscribe to interface counters
        port = "1/1/c1/1"
        sub = {
            "subscription": [
                {
                    "path": "/state/port[port-id=1/1/c1/1]/ethernet/statistics/in-octets",
                    "mode": "sample",
                    "sample_interval": 1000000000  # 10 seconds
                }
            ]
        }

        print(
            "\nTime".ljust(25),
            "Port".ljust(20),
            "in-octects".ljust(20),
        )
        for resp in gc.subscribe(sub):
            #Convert protobuf → dict
            notif_dict = MessageToDict(resp)
            if notif_dict.keys() == {'update'}:
                #Get octects
                time_stamp = int(notif_dict["update"]["timestamp"])
                date_time = pd.to_datetime(time_stamp, unit='ns', utc=True).tz_convert('America/New_York').strftime('%Y-%m-%d %H:%M:%S')
                data_raw = notif_dict["update"]["update"][0]["val"]["jsonVal"]
                data_ascii = int(base64.b64decode(data_raw).decode('utf-8').strip('"'))
                print(date_time.ljust(24), port.ljust(20), str(data_ascii).ljust(19))

            

def main():
    routers = []
    routers.append("172.20.20.2")
    routers.append("172.20.20.3")

    print("Routers available:")
    for router in routers:
        print(router)
    mgmtip = input("Choose router (insert IP):")

    gc = get_connection(mgmtip)
    get_stats(gc)


if __name__ == "__main__":
    main()