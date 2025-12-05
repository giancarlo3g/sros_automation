import argparse
from getpass import getpass
from pysros.management import connect

#get connection for a single node
def get_connection(router):
    user = "admin"
    passwd = getpass("Enter router password:")
    try:
        connection = connect(
                host=router, username=user, password=passwd, hostkey_verify=False
            )
        print("Successfully connected to", router)
        
    except Exception as error:
        print("Failed to connect to", router, ":", error)
        pass
    return connection

def set_hostname(connection):
    print(
        "\nCurrent hostname:",
        connection.running.get("/nokia-conf:configure/system/name"),
    )

    new_hostname = input("Enter new hostname:").strip()
    connection.candidate.set("/nokia-conf:configure/system/name", new_hostname)
    
    print(
        "New hostname:",
        connection.running.get("/nokia-conf:configure/system/name"),
    )

def main():
    routers = []
    routers.append("172.20.20.2")
    routers.append("172.20.20.3")

    print("Routers available:")
    for router in routers:
        print(router)
    mgmtip = input("Choose router to set hostname:")

    connection = get_connection(mgmtip)
    set_hostname(connection)
    connection.disconnect()

if __name__ == "__main__":
    main()