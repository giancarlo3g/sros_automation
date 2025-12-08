import argparse
from getpass import getpass
from pysros.management import connect

# def get_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("operation", choices=["setup", "teardown"])
#     parser.add_argument(
#         "--configure-all", action="store_true", help=argparse.SUPPRESS
#     )
#     args = parser.parse_args()
#     return args

#get connections for an array of routers using IP address
def get_connections(routers):
    connections = []
    # args = get_args()
    user = "admin"
    passwd = getpass("Enter router password:")
    
    for router in routers:
        try:
            connections.append (
                connect(
                    host=router, username=user, password=passwd, hostkey_verify=False
                )
            )
            print("Successfully connected to", router)
            
        except Exception as error:
            print("Failed to connect to", router, ":", error)
            pass
    return connections

def close_connections(connections):
    for connection in connections:
        connection.disconnect()
    print("\n Sessions closed.")

def get_interface(connections):
    config_path = '/nokia-conf:configure/router[router-name="Base"]/interface'
    state_path = '/nokia-state:state/router[router-name="Base"]/interface[interface-name="{0}"]/oper-ip-mtu'
    print(
        "\nRouter".ljust(25),
        "Interface Name".ljust(30),
        "Port".ljust(15),
        "IP MTU".ljust(6),
    )
    for connection in connections:
        data = connection.running.get(config_path)
        for interface in data.keys():
            try:
                port = str(data[interface]["port"])
            except:
                port = "N/A"
            if port:
                mtu = str(connection.running.get(state_path.format(interface)))
            else:
                mtu = "N/A"
            print(
                connection.running.get(
                    "/nokia-conf:configure/system/name"
                ).ljust(25),
                interface.ljust(30),
                port.ljust(15),
                mtu.ljust(6),
            )

def get_transceivers(connections):
    f = open('transceiver-serial-number.csv','w')
    wrdata = "hostname,port,transceiver-serial-number\n"
    for connection in connections:
        hostname = connection.running.get("/nokia-conf:configure/system/name")
        data = connection.running.get('/nokia-state:state/port',filter={'transceiver':{'vendor-serial-number':{}}})
        for key, value in data.items():
            wrdata += f"{hostname},{key},{value['transceiver']['vendor-serial-number'].data}\n"
    f.write(wrdata + '\n')
    print(wrdata)
    f.close()

def get_chassis(connections):
    for connection in connections:
        data = connection.running.get(
            '/nokia-state:state/system'
        )
        chassis = str(data["platform"])
        hostname = str(data["oper-name"])
        version = str(data["version"]["version-number"])
        print(f"  {hostname}:")
        print(f"\tchassis: {chassis}")
        print(f"\tversion: {version}")

def main():
    routers = []
    routers.append("172.20.20.2")
    routers.append("172.20.20.3")

    connections = get_connections(routers)


    while True:
        
        print("\nWelcome to pySROS test environment\n")
        print("\nSelect an option:")
        print("1. Get Interfaces")
        print("2. Get Chassis")
        print("3. Get Transceivers")
        print("Type 'exit' to quit")
        choice = input("Enter choice (1/2/3 or name): ").strip()
        match choice.lower():
            case "1" | "interface":
                get_interface(connections)
            case "2" | "chassis":
                get_chassis(connections)
            case "3" | "transceivers":
                get_transceivers(connections)
            case "exit":
                break
            case _:
                print("Invalid choice")

    close_connections(connections)

if __name__ == "__main__":
    main()
