# Get physical port information from Nokia SROS router

from getpass import getpass
from pysros.management import connect
from pysros.pprint import Table


def get_connection(router):
    """Get connection for a single router."""
    user = "admin"
    passwd = getpass("Enter router password:")
    try:
        connection = connect(
            host=router, username=user, password=passwd, hostkey_verify=False
        )
        print("Successfully connected to", router)
    except Exception as error:
        print("Failed to connect to", router, ":", error)
        return None
    return connection


def print_port_summary(rows):
    """Print port summary table."""
    cols = [
        (18, "Port"),
        (12, "Admin"),
        (12, "Oper"),
        (12, "Speed(Mbps)"),
        (30, "Description"),
    ]
    table = Table("Port Summary", cols, showCount="Ports")
    table.print(rows)


def print_port_statistics(rows):
    """Print port statistics table."""
    cols = [
        (18, "Port"),
        (15, "In Octets"),
        (15, "Out Octets"),
        (15, "In Packets"),
        (15, "Out Packets"),
        (12, "In Errors"),
        (12, "Out Errors"),
    ]
    table = Table("Port Statistics", cols, showCount="Ports")
    table.print(rows)


def print_transceiver_info(rows):
    """Print transceiver information table."""
    cols = [
        (18, "Port"),
        (25, "Vendor Part Number"),
        (25, "Serial Number"),
        (12, "Oper State"),
    ]
    table = Table("Transceiver Information", cols, showCount="Transceivers")
    table.print(rows)


def is_physical_port(port_id, port_data):
    """Check if port is a physical ethernet port (not connector, anchor, etc)."""
    port_class = port_data.get('port-class')
    if port_class:
        port_class_val = port_class.data if hasattr(port_class, 'data') else str(port_class)
        if port_class_val in ['connector', 'anchor', 'xcm-e', 'gnss']:
            return False
    if 'pxc' in port_id:
        return False
    return True


def get_port_summary(connection):
    """Get port summary with admin/oper state, speed, and description."""
    port_info = []

    # Get state data
    port_state = connection.running.get('/nokia-state:state/port')
    # Get config data for admin-state and description
    port_config = connection.running.get('/nokia-conf:configure/port')

    for port_id in sorted(port_state):
        if not is_physical_port(port_id, port_state[port_id]):
            continue

        # Get oper-state
        oper_state = port_state[port_id].get('oper-state')
        oper_state_val = oper_state.data if oper_state and hasattr(oper_state, 'data') else str(oper_state) if oper_state else "N/A"

        # Get speed from ethernet container
        speed = "N/A"
        if port_state[port_id].get('ethernet'):
            oper_speed = port_state[port_id]['ethernet'].get('oper-speed')
            if oper_speed:
                speed = oper_speed.data if hasattr(oper_speed, 'data') else str(oper_speed)

        # Get admin-state and description from config
        admin_state = "N/A"
        description = ""
        if port_config and port_id in port_config:
            admin = port_config[port_id].get('admin-state')
            if admin:
                admin_state = admin.data if hasattr(admin, 'data') else str(admin)
            desc = port_config[port_id].get('description')
            if desc:
                description = desc.data if hasattr(desc, 'data') else str(desc)

        port_info.append([port_id, admin_state, oper_state_val, speed, description])

    print_port_summary(port_info)


def get_port_statistics(connection):
    """Get port statistics (octets, packets, errors)."""
    port_info = []
    port_state = connection.running.get('/nokia-state:state/port')

    for port_id in sorted(port_state):
        if not is_physical_port(port_id, port_state[port_id]):
            continue

        if port_state[port_id].get('ethernet'):
            stats = port_state[port_id]['ethernet'].get('statistics', {})

            in_octets = stats.get('in-octets')
            in_octets_val = in_octets.data if in_octets and hasattr(in_octets, 'data') else "0"

            out_octets = stats.get('out-octets')
            out_octets_val = out_octets.data if out_octets and hasattr(out_octets, 'data') else "0"

            in_packets = stats.get('in-packets')
            in_packets_val = in_packets.data if in_packets and hasattr(in_packets, 'data') else "0"

            out_packets = stats.get('out-packets')
            out_packets_val = out_packets.data if out_packets and hasattr(out_packets, 'data') else "0"

            in_errors = stats.get('in-errors')
            in_errors_val = in_errors.data if in_errors and hasattr(in_errors, 'data') else "0"

            out_errors = stats.get('out-errors')
            out_errors_val = out_errors.data if out_errors and hasattr(out_errors, 'data') else "0"

            port_info.append([
                port_id,
                in_octets_val,
                out_octets_val,
                in_packets_val,
                out_packets_val,
                in_errors_val,
                out_errors_val
            ])

    print_port_statistics(port_info)


def get_transceiver_info(connection):
    """Get transceiver information for ports."""
    port_info = []
    port_state = connection.running.get('/nokia-state:state/port')

    for port_id in sorted(port_state):
        if not is_physical_port(port_id, port_state[port_id]):
            continue

        transceiver = port_state[port_id].get('transceiver')
        if transceiver:
            vendor_pn = transceiver.get('vendor-part-number')
            vendor_pn_val = vendor_pn.data if vendor_pn and hasattr(vendor_pn, 'data') else "N/A"

            serial = transceiver.get('vendor-serial-number')
            serial_val = serial.data if serial and hasattr(serial, 'data') else "N/A"

            oper_state = transceiver.get('oper-state')
            oper_state_val = oper_state.data if oper_state and hasattr(oper_state, 'data') else "N/A"

            if vendor_pn_val != "N/A" or serial_val != "N/A":
                port_info.append([port_id, vendor_pn_val, serial_val, oper_state_val])

    print_transceiver_info(port_info)


def get_port_detail(connection, port_id):
    """Get detailed information for a specific port."""
    try:
        port_state = connection.running.get(f'/nokia-state:state/port[port-id="{port_id}"]')
        port_config = connection.running.get(f'/nokia-conf:configure/port[port-id="{port_id}"]')
    except Exception as e:
        print(f"Error retrieving port {port_id}: {e}")
        return

    print(f"\n{'='*60}")
    print(f"Port Details: {port_id}")
    print(f"{'='*60}")

    # Admin and Oper state
    if port_config:
        admin = port_config.get('admin-state')
        print(f"Admin State    : {admin.data if admin and hasattr(admin, 'data') else 'N/A'}")
        desc = port_config.get('description')
        print(f"Description    : {desc.data if desc and hasattr(desc, 'data') else ''}")

    if port_state:
        oper = port_state.get('oper-state')
        print(f"Oper State     : {oper.data if oper and hasattr(oper, 'data') else 'N/A'}")

        # Ethernet specific info
        if port_state.get('ethernet'):
            eth = port_state['ethernet']
            speed = eth.get('oper-speed')
            print(f"Oper Speed     : {speed.data if speed and hasattr(speed, 'data') else 'N/A'} Mbps")

            duplex = eth.get('oper-duplex')
            print(f"Oper Duplex    : {duplex.data if duplex and hasattr(duplex, 'data') else 'N/A'}")

            mtu = eth.get('oper-mtu')
            print(f"Oper MTU       : {mtu.data if mtu and hasattr(mtu, 'data') else 'N/A'}")

            # Statistics
            stats = eth.get('statistics', {})
            print(f"\nStatistics:")
            print(f"  In Octets    : {stats.get('in-octets', {}).data if stats.get('in-octets') else 0}")
            print(f"  Out Octets   : {stats.get('out-octets', {}).data if stats.get('out-octets') else 0}")
            print(f"  In Packets   : {stats.get('in-packets', {}).data if stats.get('in-packets') else 0}")
            print(f"  Out Packets  : {stats.get('out-packets', {}).data if stats.get('out-packets') else 0}")
            print(f"  In Errors    : {stats.get('in-errors', {}).data if stats.get('in-errors') else 0}")
            print(f"  Out Errors   : {stats.get('out-errors', {}).data if stats.get('out-errors') else 0}")

        # Transceiver info
        transceiver = port_state.get('transceiver')
        if transceiver:
            print(f"\nTransceiver:")
            vendor_pn = transceiver.get('vendor-part-number')
            print(f"  Part Number  : {vendor_pn.data if vendor_pn and hasattr(vendor_pn, 'data') else 'N/A'}")
            serial = transceiver.get('vendor-serial-number')
            print(f"  Serial Number: {serial.data if serial and hasattr(serial, 'data') else 'N/A'}")


def main():
    routers = ["172.20.20.2", "172.20.20.3"]

    print("Available routers:")
    for i, router in enumerate(routers, 1):
        print(f"  {i}. {router}")

    mgmt_ip = input("Enter router IP: ").strip()
    connection = get_connection(mgmt_ip)

    if not connection:
        return

    while True:
        print("\n" + "="*40)
        print("Physical Port Information")
        print("="*40)
        print("1. Port Summary (admin/oper state, speed)")
        print("2. Port Statistics (octets, packets, errors)")
        print("3. Transceiver Information")
        print("4. Port Detail (single port)")
        print("5. Exit")

        choice = input("\nSelect option: ").strip()

        match choice:
            case "1":
                get_port_summary(connection)
            case "2":
                get_port_statistics(connection)
            case "3":
                get_transceiver_info(connection)
            case "4":
                port_id = input("Enter port ID (e.g., 1/1/c1/1): ").strip()
                get_port_detail(connection, port_id)
            case "5":
                break
            case _:
                print("Invalid option")

    connection.disconnect()
    print("\nSession closed.")


if __name__ == "__main__":
    main()
