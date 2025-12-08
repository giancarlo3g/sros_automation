from pygnmi.client import gNMIclient
from getpass import getpass
import json

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

def get_stats(gc):
    with gc:
        # Subscribe to interface counters
        sub = {
            "subscription": [
                {
                    "path": "/state/port[port-id=1/1/c1/1]/ethernet/statistics/in-octets",
                    "mode": "sample",
                    "sample_interval": 1000000000  # 10 seconds
                }
            ]
        }

        # print(
        #     "\nTime".ljust(20),
        #     "Port".ljust(20),
        #     "in-octects".ljust(20),
        # )
        for resp in gc.subscribe(sub):
            print (resp)
            

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