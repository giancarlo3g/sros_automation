import re
import sys
from pysros.management import connect #type: ignore


def simpleString(inputstring):
    if type(inputstring) == str:
        return inputstring
    else:
        return inputstring.__repr__()


ARGS_MAP = {
    "-s" : ("ehs",  simpleString),
}


def poor_argparse():
    #Funtion used to parse provided args as argparse is not available
    #NB : Return error = False in the dict if arg parsing fails
    arg_list = sys.argv
    # cause the if to short-circuit before second member of 'or' is evaluated to prevent IndexError
    # https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not
    if len(arg_list) == 0:
        return {}
    elif len(arg_list) == 1 or arg_list[1] == '-h': 
        print(
'''Command options :
show latest-ehs-output <argument>
''')
        sys.exit()
    else :
        args = {}
        for index, value in enumerate(arg_list):
            if index % 2 == 1 and len(arg_list) != 2:
                assert '-' in value, "This is not a valid CLI flag/option."
                args[ARGS_MAP[value][0]] = ARGS_MAP[value][1](arg_list[index+1]) # this may throw a IndexError if there is no ind+1
            elif len(arg_list) == 2:
                args["ehs"] = arg_list[1]
        return args


def get_script_results_location(connection, ehs):
    cfg_path = '/nokia-conf:configure/system/script-control'
    all_ehs_cfg = connection.running.get(cfg_path)['script-policy']
    for policy_name, policy in all_ehs_cfg.items():
        if policy_name[0] == ehs or ( "*" in ehs and re.match(ehs.replace('.*', '*').replace('*', '.*'), policy_name[0])) and policy_name[1] == "admin": 
            return policy["results"].data
    return {}


def main():
    c = connect(host="127.0.0.1", username="admin", port="830", password="admin")
    args = poor_argparse()
    path_to_results = get_script_results_location(c, args["ehs"])
    ehs_result_files = c.cli("/file list %s" % path_to_results )
    individual_files = [('_' + x.split('\n')[0]) for x in ehs_result_files.split(' _')[1:]]
    print() # create some space
    if individual_files:
        print()
        print(c.cli("/file show %s " % (path_to_results+individual_files[-1])))
    c.disconnect()


if __name__ == "__main__":
    main()