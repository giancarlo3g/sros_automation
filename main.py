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

def get_interface(connections):
    config_path = '/nokia-conf:configure/router[router-name="Base"]/interface'
    state_path = '/nokia-state:state/router[router-name="Base"]/interface[interface-name="{0}"]/oper-ip-mtu'
    print(
        "Router".ljust(25),
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


def main():
    print("Hello from pysros-test!")
    routers = []

    router1 = "172.20.20.2"
    routers.append(router1)

    connections = get_connections(routers)
    print(connections)
    get_interface(connections)


if __name__ == "__main__":
    main()
