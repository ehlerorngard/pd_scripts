# PD scripts

Some scripts for use with a PagerDuty account.


## notifications.py

This script performs actions on notification rules and on-call handoff notification rules on a given account.

It is designed to be run directly from the command line.

Current capabilites include these:
* GET all users and their notifications and print to the console
* DELETE
    - all notification rules for one specified user
    - all notification rules and all on-call handoff notification rules for all users on an account

The script **requires** these values to be input in one way or another:
* a _PD REST API key_
* an _email address_ to be used in the _From_ header of HTTP requests
* an _HTTP method_

Optional values:
* a _PD user id_ (if wanting to perform actions on only one user)
* a _PD notification rule id_


### Requirements

* python 3
* requests


### Running the script
This script can be run in any of three ways:

#### 1. Let the script prompt for the values it needs

```
python notifications.py
```


#### 2. Use options flags to specify parameter values
* `-a` _or_ `--api-key` : REST API key
* `-e` _or_ `--email` : email address
* `-m` _or_ `--method` : HTTP method
* `-u` _or_ `--user-id` : user id
* `-n` _or_ `--notification-rule-id` : notification rule id

```
python notifications.py -a YOUR_API_KEY_HERE -e YOUR_EMAIL@example.com -m DELETE
```

#### 3. Set values in a config file

Create a file named **config.ini** in the working directory 
with a format like this:
```
[vars]
api_key = yourapikey1234
email = youremail@example.com
```
Then run the script.  

#### NOTE
> As a best practice (i.e., to avoid all risk of exposing keys in a future push) do not modify the global variables' values directly in the script.  
