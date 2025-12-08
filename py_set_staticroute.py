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

def set_staticroute(connection):

    config_path = '/nokia-conf:configure/router[router-name="Base"]/static-routes'
    print(
        "\nCurrent static routes:",
        connection.running.get(config_path),
    )
    payload = {
        "route": {
            ('8.8.8.1/32', 'unicast'): {
                "ip-prefix": "8.8.8.1/32",
                "route-type": "unicast",
                "next-hop": {
                    "10.1.1.1": {
                        "ip-address": "10.1.1.1",
                        "admin-state": "enable"
                    }
                }
            },
            ('8.8.8.2/32', 'unicast'): {
                "ip-prefix": "8.8.8.2/32",
                "route-type": "unicast",
                "next-hop": {
                    "10.1.1.1": {
                        "ip-address": "10.1.1.1",
                        "admin-state": "enable"
                    }
                }
            }
        }
    }
    connection.candidate.set(config_path, payload, commit=False)
    print(connection.candidate.compare(output_format='md-cli'))
    connection.candidate.commit()

    print(
        "New static routes:",
        connection.running.get(config_path),
    )

    choice = input("Do you want to remove static routes? (y/n): ").strip()
    match choice.lower():
        case "y" | "yes":
            remote_staticroute(connection)
            print("Final static routes:",connection.running.get(config_path))
        case "n" | "no":
            print("Static routes retained.")
        case _:
            print("Invalid choice")

def remote_staticroute(connection):
    route1 = '/nokia-conf:configure/router[router-name="Base"]/static-routes/route[ip-prefix="8.8.8.1/32"][route-type="unicast"]'
    route2 = '/nokia-conf:configure/router[router-name="Base"]/static-routes/route[ip-prefix="8.8.8.2/32"][route-type="unicast"]'
    connection.candidate.delete(route1)
    connection.candidate.delete(route2)

def main():
    routers = []
    routers.append("172.20.20.2")
    routers.append("172.20.20.3")

    print("Routers available:")
    for router in routers:
        print(router)
    mgmtip = input("Choose router (insert IP):")

    connection = get_connection(mgmtip)
    set_staticroute(connection)
    connection.disconnect()

if __name__ == "__main__":
    main()