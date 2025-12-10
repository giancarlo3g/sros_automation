from pysros.wrappers import Leaf, Container
from pysros.management import connect,sros
from pysros.pprint import printTree
import sys
#import argparse
import re
import time

def get_connection():
	try:
		c = connect(host='127.0.0.1',
					username="admin",
					password="NokiaSros1!")
	except RuntimeError as e1:
		print("Failed to connect.  Error:", e1)
		sys.exit(-1)
	return c


def simpleBoolean(inputstring):
    # "Simple" function that returns True if it is ever called
    # only called when the parameter is there, kind of like action=store_true
    return True


def simpleString(inputstring):
    if type(inputstring) == str:
        return inputstring
    else:
        return inputstring.__repr__()


def simpleInteger(inputstring):
	return int(inputstring)


class Argument():
	def __init__(self, _name, _parsing_function, _help_text, _parameter_modifier, _default_value):
		self.name = _name
		self.parsing_function = _parsing_function
		self.help_text = _help_text
		self.parameter_modifier = _parameter_modifier
		self.default_value = _default_value
		self.value = _default_value
	
	def setValue(self,_value):
		if type(_value) == list and len(_value) == 1:
			_value = _value[0]
		self.value = self.parsing_function(_value)

	def __str__(self):
		return "%*s" % (20, self.help_text)


class ArgumentHelper():
	def __init__(self):
		self.command_example = "watch.py <command to execute/monitor> [-e|-i #|-r #|-a]"	# could learn this from Arguments
		self.command_help = "watch help/-h"
		self.arg_list_pointer = 0
		self.args = {}

	def addArgument(self, key, arg):
		self.args[key] = arg

	def sendHelp(self):
		help_message = "\nExample: %-*s\nCommand options:\n" % (20, self.command_example)
		for flag, arg in self.args.items():
			help_message += " %-*s%s\n" % (10 + len(flag), flag, arg)
		help_message += " %-*s%s" % (10 + len('-h'), '-h', 'Display this message.')
		return help_message

	def handleArgument(self, index, arg_list_skip_path):
		argument_flag = arg_list_skip_path[index]
		self.arg_list_pointer += self.args[argument_flag].parameter_modifier
		self.args[argument_flag].setValue(arg_list_skip_path[index +1 :self.arg_list_pointer+1])
		self.arg_list_pointer += 1

	def parseArgv(self, _arg_list):
		arg_list = _arg_list
		if len(arg_list) == 0:
			return None
		elif len(arg_list) == 1 or arg_list[1] == '-h' or arg_list[1] == "help": 
			print(self.sendHelp())
			return {'helped': True}
		else :
			result_args = {}
			# Skip the first element, as that is the path (in this case)
			if (arg_list[1] == '/'):
				# For some reason things like 
				#	tftp://172.31.255.29/scripts/Watch.py /state/system/up-time
				#	tftp://172.31.255.29/scripts/Watch.py /nokia-state:state/system/up-time
				# are passed to arg_list with the first '/' in its own entry in the list so undo that..
				# 
				# # this also applies to 
				# #     /show system information
				# # that appears "/", "show system information"
				# # we do not want this, so lighten the condition on the if-statement above
				arg_list[1] += arg_list[2]
				del arg_list[2]
			arg_list_skip_path = arg_list[1:]

			### ### ###
			### If this command needs a tools/show/state command to start
			### this section is needed. If not provided it can't run.
			### ### ### 
			try:
				# parts of show commands that follow a space and start with - would be an issue but can't think of any
				self.arg_list_pointer = min([index for index,value in enumerate(arg_list_skip_path) if value.startswith('-')])
			except ValueError as _:
				# ValueError: min() arg is an empty sequence
				self.arg_list_pointer = len(arg_list_skip_path)
			result_args["xpath"] = " ".join(arg_list_skip_path[:self.arg_list_pointer])
			### ### ###

			# the arguments come after the show command
			for index, value in enumerate(arg_list_skip_path):
				if self.arg_list_pointer == index:
					try:
						self.handleArgument(index, arg_list_skip_path)
					except KeyError as e:
						# assert False, "%s is not a valid command option. Try \"%s\"" % (value, ARGS_MAP["___COMMAND_EXAMPLE"])
						# This is prettier than raising an AssertionError
						print("\"%s\" is not a valid command option. Try \"%s\"" % (value, ARGS_MAP["___COMMAND_HELP"][2]))
						sys.exit(98)
				else:
					# this parameter or flag was already used - skip
					pass

			intermediary = {v.name:v.value for _, v in self.args.items()}
			intermediary.update(result_args)
			return intermediary


def leaf_diff(path, ref, new):
	if ref != new:
		output = path + '/' + str(new)
		print(output)


def dict_diff(ref,new,path,r_exclude):
	#Used to display the value between two XPATHs
	for key in ref:
		# Case where a context was deleted
		if key not in new :
			print(path + '/' + str(key) + " *** removed ***  ")
	for key in new:
		# Case where a context was created
		if key not in ref :
			print (path + '/' + str(key) +" *** added ***  ")
			printTree(new[key])
		else :
			# Case where a context was changed but already existed
			if new[key]!=ref[key]:
				#Not reaching a leaf node -> recursive call to dict_diff
				if type(Container({})) == type(new[key]) :
					dict_diff(ref[key], new[key],path + '/' + str(key),r_exclude)
				else:
					#Reached a leaf -> Display the result if the xpath to reach it, doesn't match the exclude provided regex
					output = path + '/'+ str(key) + '/' + str(new[key])
					if r_exclude != None :
						if not bool(re.match(r_exclude,output)) : print (output)
					else : print(output)

def main():
	args = ArgumentHelper()
	args.addArgument("-e", Argument("exclude", simpleString, "Regex to exclude from the result(s)", 1, None))
	args.addArgument("-i", Argument("interval", simpleInteger, "Interval in second(s) between each check / Default = 3", 1, 3))
	args.addArgument("-r", Argument("repeat", simpleInteger, "Number of iterations / Default = 10" , 1, 10))
	args.addArgument("-a", Argument("absolute", simpleBoolean, "Compare to the initial output if set (otherwise incremental compares)" , 0, False))

	if (found_arguments := args.parseArgv(sys.argv)):    #type: ignore
		if 'helped' in found_arguments.keys():
			return
		# Connect to the node
		node_handle = get_connection()
		if 	found_arguments['xpath'].startswith('show') or found_arguments['xpath'].startswith('tools') or\
			found_arguments['xpath'].startswith('/show') or found_arguments['xpath'].startswith('/tools'):
			#Case where a show command is monitored
			ref_output = node_handle.cli(found_arguments['xpath'])
			ref_output_split = ref_output.splitlines()
			# Clear screen only if the script is launch from the node
			if sros(): 
				print(node_handle.cli("/environment more false"))
				print(node_handle.cli("/clear screen"))
			print(ref_output)
			for i in range(0,found_arguments['repeat']):
				time.sleep(found_arguments['interval'])
				#Clear screen only if the script is launch from the node
				if sros(): print(node_handle.cli("/clear screen"))
				current_output_split = node_handle.cli(found_arguments['xpath']).splitlines()
				current_output_mod = []
				for line in current_output_split:
					#Line is not reported as changed if the eclude regex matches
					if found_arguments['exclude'] != None:
						DontCheck = True if bool(re.match(found_arguments['exclude'],line)) else False
					else :
						DontCheck = False
					#Append --> at the beginning of the line if a change is observed
					if line in ref_output_split or DontCheck:
						current_output_mod.append("    " + line)
					else:
						current_output_mod.append("--> " + line)
					# Warning : Removed lines are not notified
				for line in current_output_mod: print(line)
				if found_arguments['absolute'] == False: ref_output_split = current_output_split
		else :
			#Case where an xpath is monitored
			if 'nokia' not in found_arguments['xpath'] :
				if found_arguments['xpath'].startswith('/'):
					xpath = '/nokia-state:' + found_arguments['xpath'][1:]
				else : 
					xpath = '/nokia-state:' + found_arguments['xpath']
			else : 
				xpath = found_arguments['xpath']
			if xpath[-1] == '/':
				xpath = xpath[:-1]
			#Get the initial state of the context as ref
			try :
				obj_ref = node_handle.running.get(xpath)
				print(obj_ref)
			except Exception as e:
				print('Error in the xpath : '+xpath)
				print(e)
				sys.exit()
			print('### Initial reference recorded ###\n')
			for i in range(0,found_arguments['repeat']):
				#Wait for the required interval
				time.sleep(found_arguments['interval'])
				#Get the new state of the context to check
				obj_new = node_handle.running.get(xpath)
				print('\n### Iteration nb. {iteration} ({elapsed_time}s) ###\n'.format(iteration = i+1, elapsed_time = (i+1)*found_arguments['interval']))
				if type(obj_new) == type(Container({})): 
					#Check the diff between ref & last record
					dict_diff(obj_ref,obj_new,'.',found_arguments['exclude'])
				elif type(obj_new) == type(Leaf("")):
					leaf_diff(xpath, obj_ref, obj_new)
				#Store the actual record as ref if absolute flag is no set
				if found_arguments['absolute'] == False : obj_ref = obj_new
	else : 
		print ('Error while parsing args')


if __name__ == "__main__":
	main()


# Tests:
# watch "/nokia-state:state/router[router-name='Base']/interface[interface-name='system']/ipv4/primary/"
# watch "/nokia-state:state/router[router-name='Base']/interface[interface-name='system']/ipv4/primary/oper-address"
# watch /nokia-state:state/system/up-time
# watch /nokia-state:state/system/
# watch /nokia-state:state/system
# watch show system information
# watch "/nokia-state:state/router[router-name='Base']/interface[interface-name='system']/ipv4/primary/" -i 5 -r 1 -a
# watch "/nokia-state:state/router[router-name='Base']/interface[interface-name='system']/ipv4/primary/" -i 5 -r 10 -a -e ".*oper.*"