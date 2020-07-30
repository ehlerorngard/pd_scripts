#!/usr/bin/python

import requests
import pprint
import argparse
import configparser
import sys
import time
from threading import Event, Thread


#############################
#### global variables #####
########################
pp = pprint.PrettyPrinter(indent=4)

url = f'https://api.pagerduty.com/users'
api_key = None # do not modify this value here
email = None # do not modify this value here
method = None
user_id = None
notification_rule_id = None
interval = None

config = configparser.ConfigParser()
config.read('config.ini')
if 'vars' in config:
	api_key = config['vars'].get('api_key', '')
	email = config['vars'].get('email', '')


#############################
#### helper functions #####
########################
def scrive(texto):
	pp.pprint(texto)
	

def headers():
	return {
	  'Content-Type': 'application/json',
	  'Accept': 'application/vnd.pagerduty+json;version=2',
	  'From': email,
	  'Authorization': f'Token token={api_key}'
	}


def aquiesces(str):
	ans = input(str)

	if ans.strip().lower() == 'y':
		return True
	elif ans.strip().lower() == 'n':
		return False
	else:
		return aquiesces(str)


def proceed(res):
	if res.status_code < 200 or res.status_code > 204:
		print(res.status_code)
		scrive(res.headers)
		scrive(res.content)
		return False, res.content
	else:
		try:
			return True, res.json()
		except:
			return True, {}


def is_num(str):
	try:
		int(str)
	except:
		return False
	return int(str)


def take_a_number(str):
	num = is_num(input(str))
	if not num:
		print("Must enter a number")
		return take_a_number(str)
	elif num < 0:
		print("Must be greater than 0")
		return take_a_number(str)
	return num


def extract_subdomain(user):
    """
    Function: extract_subdomain
    Summary: Extracts the subdomain of the account in order to confirm
        with the user that they wish to perform the action on that account
    Attributes:
        @param (user): Dict[str, Any] -- The full object of one user
    Returns: str or None
    """
    url = user.get('html_url')

    if url is None:
        return None

    return url.split("/")[2].split('.')[0]


def will_repeat(interval):
	repeat = False
	if interval:
		repeat = True
	elif aquiesces(f"Would you like your chosen action(s) to be exectued repeatedly? "):
		repeat = True
		interval = take_a_number("Rerun the action repeatedly how many seconds after "
								+ "each completion? ")
	return repeat, interval


def recur(interval, func, *args):
	print("\nTo exit, enter ^C \n")
	while True:
		func(*args)
		print(f'waiting {interval} seconds...')
		time.sleep(interval)


###########################
#### GET functions ######
#######################
def get_user_by_id(id):
	get_url = f"{url}/{id}"
	response = requests.get(get_url, headers=headers())
	suc, res = proceed(response)
	return res.get('user') if suc else {}


def get_first_user():
	get_url = f"{url}?limit=1"
	response = requests.get(get_url, headers=headers())
	suc, res = proceed(response)
	return res.get('users')[0] if suc else {}


def get_all_users():
	response = requests.get(url, headers=headers())
	success, res = proceed(response)
	return res.get('users') if success else [{}]


def get_handoff_rules(u_id):
	get_url = f"{url}/{u_id}/oncall_handoff_notification_rules"
	response = requests.get(get_url, headers=headers())
	suc, res = proceed(response)
	return res.get('oncall_handoff_notification_rules') if suc else []


###########################
#### POST functions #####
#######################
def create_new_notification_rule():
	# This function is INCOMPLETE
	contact_method_id = ''
	data = {
	    'notification_rule': {
	        'type': 'assignment_notification_rule',
	        'start_delay_in_minutes': 0,
	        'contact_method': {
	            'id': contact_method_id,
	            'type': 'email_contact_method'
	        },
	        'urgency': 'high'
	    }
	}
	response = requests.post(url, headers=headers(), data=data)


##############################
#### DELETE functions ######
#########################
def delete_handoff_rule(u_id, hn_id):
	del_url = f'{url}/{u_id}/oncall_handoff_notification_rules/{hn_id}'
	response = requests.delete(del_url, headers=headers())
	success, response = proceed(response)
	if success:
		print("    success")
	return


def delete_notification_rule(u_id, n_id):
	del_url = f'{url}/{u_id}/notification_rules/{n_id}'
	response = requests.delete(del_url, headers=headers())
	success, response = proceed(response)
	if success:
		print("    success")
	return


def delete_all_handoff_notification_rules(user):
	for handoff_rule in get_handoff_rules(user.get('id')):
		delete_handoff_rule(user.get('id'), handoff_rule.get('id'))


def delete_all_notification_rules(user):
	for notification_rule in user.get('notification_rules'):
		delete_notification_rule(user.get('id'), notification_rule.get('id'))


def delete_all_users_handoff(users):
	for user in users:
		print(f"{user['name']} ( {user['id']} )")
		delete_all_handoff_notification_rules(user)


def delete_all_users_notif(users):
	for user in users:
		print(f"{user['name']} ( {user['id']} )")
		delete_all_notification_rules(user)


def delete_all_users_handoff(users):
	for user in users:
		print(f"{user['name']} ( {user['id']} )")
		delete_all_handoff_notification_rules(user)


def delete_all_users_all_notif(users):
	delete_all_users_handoff(users)
	delete_all_users_notif(users)	


##########################
#### main ##############
######################
def main():
	global email, api_key, method, user_id, notification_rule_id, interval
	if email == '':
		email = input("Email address for 'From' header: ")

	if not api_key:
		api_key = input("API key: ")

	if not method:
		method = input("HTTP method: ")

	subdomain = extract_subdomain(get_first_user())
	if not aquiesces(f"Proceed with action on subdomain '{subdomain}'? (y/n) "):
		print("Aborting.")
		sys.exit()

	method = method.strip().lower()
	if method == 'get':
		if user_id:
			get_user_by_id(user_id)
		else:
			scrive(get_all_users())
	elif method == 'post':
		print(f"{method.upper()} method functionality is not yet built...")
		pass
		create_new_notification_rule()
	elif method == 'put':
		print(f"{method.upper()} method functionality is not yet built...")
		pass
	elif method == 'delete':
		if not user_id:
			users = get_all_users()
			del_handoff = aquiesces(f"Would you like to delete all on-call handoff notification "
				          + f"rules for all users on subdomain '{subdomain}'? (y/n) ")
			del_notif = aquiesces(f"Would you like to delete all incident notification "
				          + f"rules for all users on subdomain '{subdomain}'? (y/n) ")

			both = False
			if del_notif and del_handoff:
				both = True

			repeat, interval = will_repeat(interval)

			if repeat:
				if both:
					recur(interval, delete_all_users_all_notif, users)
				elif del_handoff:
					recur(interval, delete_all_users_handoff, users)
				elif del_notif:
					recur(interval, delete_all_users_notif, users)
			else:
				if del_handoff:
					delete_all_users_handoff(users)
				if del_notif:
					delete_all_users_notif(users)

		else:
			delete_all_notification_rules(get_user_by_id(user_id))
	else:
		main()

	print("    *** script completed successfully ***")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Users via REST API')
    parser.add_argument(
        '--method', '-m',
        help='HTTP method',
        dest='method',
        required=False
    )
    parser.add_argument(
        '--user-id', '-u',
        help='user id',
        dest='user_id',
        required=False
    )
    parser.add_argument(
        '--notification-rule-id', '-n',
        help='notification rule id',
        dest='notification_rule_id',
        required=False
    )
    parser.add_argument(
        '--email', '-e',
        help='email address for From header',
        dest='email',
        required=False
    )
    parser.add_argument(
        '--api-key', '-a',
        help='PD REST API key',
        dest='api_key',
        required=False
    )
    args = parser.parse_args()

    if args.api_key:
    	api_key = args.api_key

    if args.email:
    	email = args.email

    if args.method:
    	method = args.method

    if args.user_id:
    	user_id = args.user_id

    if args.notification_rule_id:
    	notification_rule_id = args.notification_rule_id

    main()