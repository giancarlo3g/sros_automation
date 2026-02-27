#Show port transceiver part and serial number with port status

from getpass import getpass
from pysros.management import connect
from pysros.pprint import Table, printTree

# Fuction definition to output a SR OS style table to the screen
def print_table(rows):
    """Setup and print the SR OS style table"""
    # Define the columns that will be used in the table.  Each list item
    # is a tuple of (column width, heading).
    cols = [(10, "Port"),
            (10, "Adm"),
            (10, "Opr"),
            (20, "Part-Number"),
            (15, "Serial-Number"),]
    # Initalize the Table object with the heading and columns.
    table = Table("Port Transceiver Status with Serial Number", cols, showCount="Port")
    # Print the output passing the data for the rows as an argument to the function.
    table.print(rows)

#get connection for a single node
def get_connection(router):
    user = "admin"
    # passwd = getpass("Enter router password:")
    try:
        connection = connect(
                host=router, username=user, password="NokiaSros1!", hostkey_verify=False
            )
        print("Successfully connected to", router)
        
    except Exception as error:
        print("Failed to connect to", router, ":", error)
        pass
    return connection

def get_data(connection):
    path = '/nokia-oper-global:global-operations/traceroute'
    input_data = {'destination': '10.10.10.1'}
    output = connection.action(path, input_data)
    printTree(output)
    print(output)

def main():
    # routers = []
    # routers.append("172.20.20.2")
    # routers.append("172.20.20.3")

    # print("Routers available:")
    # for router in routers:
    #     print(router)
    # mgmtip = input("Choose router (insert IP):")

    # connection = get_connection(mgmtip)
    connection = get_connection("172.20.20.2")
    get_data(connection)
    connection.disconnect()

if __name__ == "__main__":
    main()
