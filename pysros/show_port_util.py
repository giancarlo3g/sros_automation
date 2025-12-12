#Show port utilization

from getpass import getpass
from pysros.management import connect
from pysros.pprint import Table

# Fuction definition to output a SR OS style table to the screen
def print_table(rows):
    """Setup and print the SR OS style table"""
    # Define the columns that will be used in the table.  Each list item
    # is a tuple of (column width, heading).
    cols = [
        (20, "Port"),
        (20, "In Utilization %"),
        (20, "Out Utilization %"),
    ]
    # Initalize the Table object with the heading and columns.
    table = Table("Ports and their current utilization", cols, showCount="Ports")
    # Print the output passing the data for the rows as an argument to the function.
    table.print(rows)

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

def get_data(connection):
    port_info = []
    port_state = connection.running.get('/nokia-state:state/port')

    for PortID in sorted(port_state):
        port_class = port_state[PortID]['port-class'].data
        if port_class == 'connector' or port_class == 'anchor' or port_class == 'xcm-e' or port_class == 'gnss': 
            continue
        else:
            if 'pxc' in PortID:
                continue
            else:
                if port_state[PortID].get('ethernet'):
                    in_utils = port_state[PortID]['ethernet']['statistics']['in-octets'].data
                    out_utils = port_state[PortID]['ethernet']['statistics']['out-octets'].data
                    port_info.append([PortID, in_utils, out_utils])
    print_table(port_info)


def main():
    routers = []
    routers.append("172.20.20.2")
    routers.append("172.20.20.3")

    print("Routers available:")
    for router in routers:
        print(router)
    mgmtip = input("Choose router (insert IP):")

    connection = get_connection(mgmtip)
    get_data(connection)
    connection.disconnect()   

if __name__ == "__main__":
    main()
