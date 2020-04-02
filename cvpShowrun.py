#!/usr/bin/env python
#
import argparse
from getpass import getpass
import json
import requests
from requests import packages
import time
import os

# CVP manipulation class

# Set up classes to interact with CVP API
# serverCVP exception class

class serverCvpError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# Create a session to the CVP server

class serverCvp(object):

    def __init__ (self,HOST,USER,PASS):
        self.url = "https://%s"%HOST
        self.authenticateData = {'userId' : USER, 'password' : PASS}
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS'
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        try:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        except packages.urllib3.exceptions.ProtocolError as e:
            if str(e) == "('Connection aborted.', gaierror(8, 'nodename nor servname provided, or not known'))":
                raise serverCvpError("DNS Error: The CVP Server %s can not be found" % CVPSERVER)
            elif str(e) == "('Connection aborted.', error(54, 'Connection reset by peer'))":
                raise serverCvpError( "Error, connection aborted")
            else:
                raise serverCvpError("Could not connect to Server")

    def logOn(self):
        try:
            headers = { 'Content-Type': 'application/json' }
            loginURL = "/web/login/authenticate.do"
            response = requests.post(self.url+loginURL,json=self.authenticateData,headers=headers,verify=False)
            if "errorMessage" in str(response.json()):
                text = "Error log on failed: %s" % response.json()['errorMessage']
                raise serverCvpError(text)
        except requests.HTTPError as e:
            raise serverCvpError("Error HTTP session to CVP Server: %s" % str(e))
        except requests.exceptions.ConnectionError as e:
            raise serverCvpError("Error connecting to CVP Server: %s" % str(e))
        except:
            raise serverCvpError("Error in session to CVP Server")
        self.cookies = response.cookies
        return response.json()

    def logOut(self):
        headers = { 'Content-Type':'application/json' }
        logoutURL = "/cvpservice/login/logout.do"
        response = requests.post(self.url+logoutURL, cookies=self.cookies, json=self.authenticateData,headers=headers,verify=False)
        return response.json()
    
    def getInventory(self):
       getURL = "/cvpservice/inventory/devices"
       response = requests.get(self.url+getURL,cookies=self.cookies,verify=False)
       if "errorMessage" in str(response.json()):
           text = "Error, retrieving tasks failed: %s" % response.json()['errorMessage']
           raise serverCvpError(text)
       inventoryList = response.json()
       return inventoryList
        
    def snapshotDeviceConfig(self,deviceSerial):
        getURL = "/cvpservice/snapshot/deviceConfigs/"+deviceSerial+"?current=true"
        response = requests.get(self.url+getURL,cookies=self.cookies,verify=False)
        if "errorMessage" in str(response.json()):
            text = "Error retrieving running config failed: %s" % response.json()['errorMessage']
            raise serverCvpError(text)
        deviceConfig = response.json()["runningConfigInfo"]
        return deviceConfig

def main():
    
    d1 = time.strftime("%Y_%m_%d_%H_%M_%S", time.gmtime())

    parser = argparse.ArgumentParser()
    parser.add_argument('--username', required=True)
    parser.add_argument('--cvpServer', required=True)

    args = parser.parse_args()
    username = args.username
    password = getpass()
    cvpServer=args.cvpServer
    
    print ("Attaching to API on %s to get Data" %cvpServer)
    try:
        cvpSession = serverCvp(str(cvpServer),username,password)
        logOn = cvpSession.logOn()
    except serverCvpError as e:
        text = "serverCvp:(main1)-%s" % e.value
        print (text)
    print ("Login Complete")

    inventoryList = cvpSession.getInventory()
    os.mkdir(d1)
    k=0
    for device in inventoryList:
        print (inventoryList[k]["hostname"]+","+inventoryList[k]["modelName"]+","+inventoryList[k]["version"]+","+inventoryList[k]["ipAddress"]+","+inventoryList[k]["serialNumber"])
        runningConfig=cvpSession.snapshotDeviceConfig(inventoryList[k]["serialNumber"])
        filename= inventoryList[k]["hostname"] + "_show_run_" + d1 + ".txt"
        f = open(d1 + "/" + filename,'w')
        f.write(runningConfig)
        k=k+1
    
    print ("Logout from CVP:%s"% cvpSession.logOut()['data'])

if __name__ == '__main__':
    main()

            
