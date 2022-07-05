#!/usr/bin/python3
#-*-coding:utf8 -*-
from array import array
from ctypes import sizeof
import sqlite3
import urllib3
import time
import sys 
import requests
import base64
import json
import os
import argparse
import zipfile
import pandas as pd
import shutil
import chardet
from datetime import datetime
# from ridgeapisample import *v

# disable SSL certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

##### _handle_getHost 6/23 Jiahao Wang
def splitBytes(x):
    try:
        return int(x)
    except ValueError:
        return x       
def _handle_getHost(RidgeBotAPIURL,RidgeBotAPIHeader,size,page,search,asc_field,asc):
    RidgeBotRequestURL = RidgeBotAPIURL + "/assets/host" + "?" + "size=" + size + "&page=" + page+ "&search=" + search + "&asc_field="+asc_field+"&asc="+asc
    # merge the input size and page to the request URL
  
    getHostResponse = requests.get(RidgeBotRequestURL,headers = RidgeBotAPIHeader, verify = False)
    # get response from API about getHost

    if getHostResponse.status_code != 200 or getHostResponse.json()["code"] == 400:
        print("\nPossible RidgeBot authentication user error.\n")
        print("Server response: "+getHostResponse.json()["message"]["key"])
        exit()
    # if status code is not 200 which means error occur, the function will exist immediately

    getHost_content = getHostResponse._content
    # getHost raw content from response

    strGetHost = str(getHost_content,encoding = "utf-8")
    #translate the raw content from bytes to String with utf-8 encode

    splitedStrGetHost = ([splitBytes(x) for x in strGetHost.split(',"tags":')])
    #convert to list by spliting the Host information from String format raw content

    return splitedStrGetHost
##### _handle_getHost 6/23 Jiahao Wang

##### _handle_deleteHost 6/18 Jiahao Wang
def _handle_deleteHost(RidgeBotAPIURL,RidgeBotAPIHeader):
    RidgeBotRequestURL = RidgeBotAPIURL + "/assets/host/delete"
    # add related API postfit to the request URL

    with open("deleteHostPayload.json") as deleteHostJSONfile:
        deleteHostPayload = json.load(deleteHostJSONfile)
        deleteHostJSONfile.close()
    # open related API json payload and store in payload variable

    deleteHostResponse=requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = deleteHostPayload)
    # post the client request and get response from server about API 

    if deleteHostResponse.status_code != 200 or deleteHostResponse.json()["code"] == 400:
        print("\nPossible RidgeBot authentication user error or invaild input.\n")
        print("Server response: "+deleteHostResponse.json()["message"]["key"])
        exit()
    # if status code is not 200 which means error occur, the function will exist immediately
    
##### _handle_deleteHost 6/18 Jiahao Wang

##### _handle_updateHost 6/21 Jiahao Wang
def _handle_updateHost(RidgeBotAPIURL,RidgeBotAPIHeader):
    RidgeBotRequestURL = RidgeBotAPIURL + "/assets/host/update"
    # add related API postfit to the request URL

    with open("updateHostPayload.json") as updateHostJSONfile:
        updateHostPayload = json.load(updateHostJSONfile)
        updateHostJSONfile.close()
    # open related API json payload and store in payload variable

    updateHostResponse=requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = updateHostPayload)
    # post the client request and get response from server about API 

    if updateHostResponse.status_code != 200 or updateHostResponse.json()["code"] == 400:
        print("\nPossible RidgeBot authentication user error or invaild input.\n")
        print("Server response: "+updateHostResponse.json()["message"]["key"])
        exit()
    # if status code is not 200 which means error occur, the function will exist immediately
##### _handle_updateHost 6/21 Jiahao Wang

##### _handle_addSite 6/21 Jiahao Wang
def _handle_addSite(RidgeBotAPIURL,RidgeBotAPIHeader):
    RidgeBotRequestURL = RidgeBotAPIURL + "/assets/site/add"
    # add related API postfit to the request URL

    with open("addSitePayload.json") as addSiteJSONfile:
        addSitePayload = json.load(addSiteJSONfile)
        addSiteJSONfile.close()
    # open related API json payload and store in payload variable

    addSiteResponse=requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = addSitePayload)
    # post the client request and get response from server about API 

    if addSiteResponse.status_code != 200 or addSiteResponse.json()["code"] == 400:
        print("\nPossible RidgeBot authentication user error or invaild input.\n")
        print("Server response: "+addSiteResponse.json()["message"]["key"])
        exit()
    # if status code is not 200 which means error occur, the function will exist immediately
##### _handle_addSite 6/21 Jiahao Wang

##### _handle_deleteSite 6/22 Jiahao Wang
def _handle_deleteSite(RidgeBotAPIURL,RidgeBotAPIHeader):
    RidgeBotRequestURL = RidgeBotAPIURL + "/assets/site/delete"
    # add related API postfit to the request URL

    with open("deleteSitePayload.json") as deleteSiteJSONfile:
        addSitePayload = json.load(deleteSiteJSONfile)
        deleteSiteJSONfile.close()
    # open related API json payload and store in payload variable

    deleteSiteResponse=requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = addSitePayload)
    # post the client request and get response from server about API 

    if deleteSiteResponse.status_code != 200 or deleteSiteResponse.json()["code"] == 400:
        print("\nPossible RidgeBot authentication user error or invaild input.\n")
        print("Server response: "+deleteSiteResponse.json()["message"]["key"])
        exit()
    # if status code is not 200 which means error occur, the function will exist immediately
##### _handle_deleteSite 6/22 Jiahao Wang

##### _handle_deleteSite 6/22 Jiahao Wang
def _handle_updateSite(RidgeBotAPIURL,RidgeBotAPIHeader):
    RidgeBotRequestURL = RidgeBotAPIURL + "/assets/site/update"
    # add related API postfit to the request URL

    with open("updateSitePayload.json") as updateSiteJSONfile:
        addSitePayload = json.load(updateSiteJSONfile)
        updateSiteJSONfile.close()
    # open related API json payload and store in payload variable

    updateSiteResponse=requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = addSitePayload)
    # post the client request and get response from server about API 

    if updateSiteResponse.status_code != 200 or updateSiteResponse.json()["code"] == 400:
        print("\nPossible RidgeBot authentication user error or invaild input.\n")
        print("Server response: "+updateSiteResponse.json()["message"]["key"])
        exit()
    # if status code is not 200 which means error occur, the function will exist immediately
##### _handle_updateSite 6/22 Jiahao Wang

##### _handle_getUser 6/18 Jiahao Wang
def _handle_getUser(RidgeBotAPIURL,RidgeBotAPIHeader):
    RidgeBotRequestURL = RidgeBotAPIURL + "/assets/user"
    # add related postfit to the request URL

    getUserResponse = requests.get(RidgeBotRequestURL,headers = RidgeBotAPIHeader, verify = False)
    #get response from server about API 

    if getUserResponse.status_code != 200 or getUserResponse.json()["code"] == 400:
        print("\nPossible RidgeBot authentication user error.\n")
        print("Server response: "+getUserResponse.json()["message"]["key"])
        exit()
     # if status code is not 200 which means error occur, the function will exist immediately

    return getUserResponse._content
##### _handle_getUser 6/18 Jiahao Wang

##### _handle_getSites 6/24 Jiahao Wang
def _handle_getSites(RidgeBotAPIURL,RidgeBotAPIHeader,doc_type,size,page,search,asc_field,asc):
    
    RidgeBotRequestURL = RidgeBotAPIURL + "/assets/"+doc_type+"?"+"size=" + size + "&page=" + page+ "&search=" + search + "&asc_field="+asc_field+"&asc="+asc
      # merge the input size and page to the request URL

    getSitesResponse = requests.get(RidgeBotRequestURL,headers = RidgeBotAPIHeader, verify = False)
    #get response from server about API 

    if getSitesResponse.status_code != 200 or getSitesResponse.json()["code"] == 400:
        print("\nPossible RidgeBot authentication user error.\n")
        print("Server response: "+getSitesResponse.json()["message"]["key"])
        exit()
     # if status code is not 200 which means error occur, the function will exist immediately

    getSites_content = getSitesResponse._content
    # getHost raw content from response

    strGetSites = str(getSites_content,encoding = "utf-8")
    #translate the raw content from bytes to String with utf-8 encode

    splitedStrGetHost = ([splitBytes(x) for x in strGetSites.split('},')])
    #convert to list by spliting the Host information from String format raw content

    return splitedStrGetHost
##### _handle_getUser 6/24 Jiahao Wang

def main(): 
    RidgeBotAPIURL = "https://bot58.ridgesecurity.ai/api/v4"
    RidgeBotAuthToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJrZW4iLCJpYXQiOjE2NTM5NDU0MjcsImRhdGEiOnsidXNlcm5hbWUiOiJqaWF6aGFvIiwiaXNfbmV2ZXJfZXhwaXJlIjp0cnVlLCJpZCI6NCwic29mdHdhcmVfdGltZSI6MTY1MzU1MDE1NS4zNzg1NzQ4LCJyb2xlX2lkIjoxfSwiZXhwIjo0Nzc2MDA5NDI3fQ.ZZCeBjdM8MnuT54a8xRbFUc92E79-wArJzAuWIdOpzg"
    Content_Type = "application/json"
    RidgeBotAPIHeader = {'Authorization': RidgeBotAuthToken, 'Content-Type':Content_Type}
    RidgeBotAdminAuthToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJrZW4iLCJpYXQiOjE2NTM2ODU4MTcsImRhdGEiOnsidXNlcm5hbWUiOiJhZG1pbiIsImlzX25ldmVyX2V4cGlyZSI6dHJ1ZSwiaWQiOjEsInNvZnR3YXJlX3RpbWUiOjE2NTM1NTAxNTUuMzc4NTc0OCwicm9sZV9pZCI6bnVsbH0sImV4cCI6NDc3NTc0OTgxN30.op9FbAjYEpFT4DtE-e50FzWSnU-3TKtCtRt77aRWkPI"
    RidgeBotAdminAPIHeader = {'Authorization': RidgeBotAdminAuthToken, 'Content-Type':Content_Type}
    #perpare the basic API URL, Authentication Token,  Content Type and API Header for connection.

    #_handle_getHost test 6/23 Jiahao Wang !!!SUCCESS
    # size="10"
    # page="1"
    # search=""
    # asc_field=""
    # asc=""
    # splitedStrGetHost=_handle_getHost(RidgeBotAPIURL,RidgeBotAPIHeader,size,page,search,asc_field,asc)
    # #get list about Host information from getHost function
    # for subContent in splitedStrGetHost:
    #     print(subContent)
    #_handle_getHost test 6/23 Jiahao Wang

    #_handle_getUser test 6/18 Jiahao Wang !!!SUCCESS
    # getUserMessage = _handle_getUser(RidgeBotAPIURL,RidgeBotAPIHeader)
    # print(getUserMessage)
    #_handle_getUser test 6/18 Jiahao Wang
    
    #_handle_deleteHost test 6/18 Jiahao Wang !!!SUCCESS
    # _handle_deleteHost(RidgeBotAPIURL,RidgeBotAPIHeader)
    #_handle_deleteHost test 6/18 Jiahao Wang

    #_handle_updateHost test 6/18 Jiahao Wang $need !!!SUCCESS, admin token
    #_handle_updateHost(RidgeBotAPIURL,RidgeBotAdminAPIHeader)
    #_handle_updateHost test 6/18 Jiahao Wang

    ##### _handle_addSite 6/21 Jiahao Wang !!!SUCCESS
    _handle_addSite(RidgeBotAPIURL,RidgeBotAPIHeader)
    ##### _handle_addSite 6/21 Jiahao Wang
    
    ##### _handle_deleteSite 6/22 Jiahao Wang !!!SUCCESS
    #_handle_deleteSite(RidgeBotAPIURL,RidgeBotAPIHeader)
    ##### _handle_deleteSite 6/22 Jiahao Wang

    ##### _handle_updateSite 6/22 Jiahao Wang !!!SUCCESS
    #_handle_updateSite(RidgeBotAPIURL,RidgeBotAdminAPIHeader)
    ##### _handle_updateSite 6/22 Jiahao Wang

    ##### _handle_getSites 6/24 Jiahao Wang !!!SUCCESS
    # doc_type="site"
    # size="10"
    # page="1"
    # search=""
    # asc_field=""
    # asc=""
    # splitedgetSitesContent=_handle_getSites(RidgeBotAPIURL,RidgeBotAPIHeader,doc_type,size,page,search,asc_field,asc)
    # #get list about Host information from getHost function
    # for subContent in splitedgetSitesContent:
    #     print(subContent+"},")
    ##### _handle_getSites 6/24 Jiahao Wang

main()
