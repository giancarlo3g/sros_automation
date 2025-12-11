from pysros.exceptions import InvalidPathError,SrosMgmtError
from pysros.wrappers import Leaf,LeafList
from pysros.management import connect
from pysros.ehs import get_event
from pysros.pprint import Table
from utime import localtime,mktime,strftime,struct_time
import time
from datetime import datetime


def print_log(event_object):
    time = localtime()
    time_str = "%g/%g/%g %g:%g:%g %s" % (time.tm_year,time.tm_mon,time.tm_mday,time.tm_hour,time.tm_min,time.tm_sec,"TODO>TZ")
    time_str = strftime("%Y/%m/%d %H:%M:%S",time)
    format_str = "At time %s: received a linkDown event for interface:\n\t%s,\n" % (time_str, event_object.subject)+\
        "All interfaces are required for this service.\nTo force switchover, shutting down all other interfaces now!"
    print(format_str)


def router_timestamp_to_datetime(router_timestamp_string):
    day, time = router_timestamp_string.split('T')
    year,month,day = day.split('-')
    hour,minute,second = time.split('.')[0].split(':')
    # could do something with TZ and DST here
    # ignore week-day and year-day
    # datetime!
    return datetime.fromisoformat(router_timestamp_string.data.split('.')[0])
    # return struct_time((int(year),int(month),int(day),int(hour),int(minute),int(second),0,0,0))


def to_rows(active_interfaces):
    for key,value in active_interfaces.items():
        now = datetime.now()
        last= router_timestamp_to_datetime(value["last-oper-change"])
        yield key,last,now-last


def print_table(rows, info):
    # This example does 3 equal columns...
    cols = [
        (20, "Interface"),
        (40, "Last oper change"),
        (18, "%s since" % info),
    ]

    # Initalize the Table object with the heading and columns.
    table = Table("Interfaces modified by script (up -> down) %s" % ("[BEFORE]" if info == "Up" else "[AFTER]"), cols, showCount="Interfaces")

    # The rows are added as a list of lists. Each list item having
    # 3 items as that is how many columns we have in our table.
    table.print(rows)


def find_interfaces(connection, linkDownInterface, operStatusFilter=""):
        base_router_state     = connection.running.get('/nokia-state:state/router[router-name="Base"]') #mustn't end with '/'
        if linkDownInterface:
            del base_router_state["interface"][linkDownInterface]
        del base_router_state["interface"]["system"]

        active_interfaces = {}
        for interface,state in base_router_state["interface"].items():
            if state["oper-state"] == Leaf(operStatusFilter):
                active_interfaces[interface] = state
        return active_interfaces


def disable_active_interfaces(connection, active_interfaces):
    print("Interfaces to be brought down:\n\t%s\n" % "\n\t".join([intf for intf in active_interfaces.keys()]))

    cfg_path = '/nokia-conf:configure/router[router-name="Base"]'
    cfg_payload = {"nokia-conf:interface":[]}
    for interface in active_interfaces:
        # SEE MAIN REF - this is what I would like to put here: cfg_payload["nokia-conf:interface"].append(            
        # and this is what I have to put here (for now):
        cfg_payload["nokia-conf:interface"] = {
                    "interface-name":interface,
                    "admin-state":"disable",
                }

        if cfg_payload:
            try:
                connection.candidate.set(cfg_path,cfg_payload)
            except SrosMgmtError as e:
                print("Disabling the active interfaces failed due to an error:\n\t%s" % e.args)
            except TypeError as e:
                print(e)
                print(cfg_payload)
            except Exception as e:
                print(e,dir(e),type(e))
    return True


def main():
    c = connect(host="127.0.0.1", username="admin", port="830", password="admin")

# this seems like it shoudl reasonably work but it doesn't, re docs (leaflist) TODO
#    cfg_path = '/nokia-conf:configure'
#    cfg_payload = { 'router':{} }
#    active_interfaces = find_interfaces(c, "router1", operStatusFilter="up")
#    cfg_payload['router'] = [{"router-name":"Base"}]
#    for interface in active_interfaces:
#        continue
#        cfg_payload['router'].append(            
#                {
#                    "interface-name":interface,
#                    "admin-state":"disable",
#                }
#            )
#
#
#    x = c.candidate.get(cfg_path).keys()
#    print(x)
#    print(cfg_payload)
#    c.candidate.set(cfg_path,cfg_payload)

    trigger_event = get_event()
    if not trigger_event or trigger_event.subject[0].isdigit():
        c.disconnect()
        return
    print_log(trigger_event)
    if active_interfaces := find_interfaces(c, trigger_event.subject, operStatusFilter="up"):
        print_table(to_rows(active_interfaces), "Up")
        time.sleep(1)
        disable_active_interfaces(c,active_interfaces)
        time.sleep(1)
        if inactive_interfaces := find_interfaces(c, "", operStatusFilter="down"):
            print_table(to_rows(inactive_interfaces), "Down")
    c.disconnect()


if __name__ == "__main__":
    main()
