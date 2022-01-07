#!/usr/bin/env python
#
from cvprac.cvp_client import CvpClient
from cvprac.cvp_api import CvpApi
import urllib3
import ssl
import argparse
from getpass import getpass
import time
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

parser = argparse.ArgumentParser()
parser.add_argument('--username', required=True)
parser.add_argument('--cvpip', required=True)

args = parser.parse_args()
switchuser = args.username
cvpip = args.cvpip
switchpass = getpass()

clnt = CvpClient()
clnt.connect([cvpip], switchuser, switchpass)
clntapi = CvpApi(clnt)

inventory = clntapi.get_inventory()
d1 = time.strftime("%Y_%m_%d_%H_%M_%S", time.gmtime())
os.mkdir(d1)

for device in inventory:
    hostname = device["hostname"]
    print (hostname)
    device_mac = device["systemMacAddress"]
    runningConfig = clntapi.get_device_configuration(device_mac) 

    filename= hostname+ "_show_run_" + d1 + ".txt"
    with open(d1 + "/" + filename,'w') as f:
        f.write(runningConfig)
