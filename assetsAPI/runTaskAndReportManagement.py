#!/usr/bin/python3
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
from datetime import datetime
from pytz import timezone
import pytz
from taskAndReportManagement import *
from taskAndReportManagement import _handle_getTaskStatus
from taskAndReportManagement import _handle_generateReport
from taskAndReportManagement import _handle_downloadReport
from taskAndReportManagement import _handle_createOneTimeTask
from taskAndReportManagement import _handle_createPeriodicTask
from taskAndReportManagement import _handle_taskStop
from taskAndReportManagement import _handle_taskInfo
from taskAndReportManagement import _handle_taskStatistics
from taskAndReportManagement import _handle_taskPause
from taskAndReportManagement import _handle_taskClone
from taskAndReportManagement import _handle_taskDelete
from taskAndReportManagement import _handle_taskStart
from taskAndReportManagement import _handle_taskRestart

# disable SSL certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Global variables 
RidgeBot_API_URL = ""
default_RidgeBot_API_Header = ""


# Automation Script
def main(): 
    # Check for config file
  
  parser = argparse.ArgumentParser()
  parser.add_argument("--config", '-c', nargs='?', type=argparse.FileType('r'), help="Input the JSON config file")
  args, leftovers = parser.parse_known_args()
  if args.config is not None:
    configFile = args.config
  else:
    print ('No configuration file. Exit')
    exit()

  if configFile is not None:
    # load config information into script variables
    with open("config.json") as configFileJSON:
        config_data = json.load(configFileJSON)
        baseURL = config_data['RidgeBotBaseURL'] 
        RidgeBotAuthToken = config_data['RidgeBotAuthToken']
        configFileJSON.close()

        #global RidgeBot_API_URL
        RidgeBot_API_URL = baseURL + "api/v4"

        #global default_RidgeBot_API_Header
        default_RidgeBot_API_Header = {'Authorization': RidgeBotAuthToken, 'Content-Type':'application/json'}

        
        # Create a RidgeBot one-time task with the target
        targets = ["198.168.1.200", "198.168.1.211"]
        scenario_template = 1
        task_name = "python test task"
        periodicType = "run once"
        pending_time = "2022-07-25 08:47"
        pause_start = "05:06"
        pause_end = "11:08"
        end_date = "2022-07-07 14:48"
        startTime = "12:06"
        task_id = _handle_createOneTimeTask(targets, task_name, periodicType, pause_start, pause_end, pending_time, RidgeBot_API_URL, default_RidgeBot_API_Header, scenario_template)
        targets = ["https://www.google.com"]
        scenario_template = 2
        periodicType = "week"
        _handle_createPeriodicTask(targets, task_name, periodicType, startTime, end_date, pause_start, pause_end, RidgeBot_API_URL, default_RidgeBot_API_Header, scenario_template)

        # #task_id for test:
        # task_id = 'f62260f6-ef25-11ec-8f79-00505693f632'

        taskStatusHeader = {'Authorization': RidgeBotAuthToken, 'task_id': task_id}
        create_time=datetime.now(tz=pytz.timezone('US/Pacific')).strftime("%Y-%m-%d-%H:%M:%S")
        createat=datetime.now(tz=pytz.timezone('US/Pacific')).strftime("%m-%d-%Y-%H-%M-%S")

        # Check the task status before proceeding 
        _handle_getTaskStatus(taskStatusHeader, task_id, RidgeBot_API_URL)

        #use task_id to get taskInfo task
        _handle_taskInfo(task_id, RidgeBot_API_URL, default_RidgeBot_API_Header)

        #use task_id to stop task
        _handle_taskStatistics(taskStatusHeader, task_id, RidgeBot_API_URL)

        # #use task_id to stop task
        # _handle_taskStop(taskStatusHeader, task_id, RidgeBot_API_URL)

        #use task_id to pause task
        _handle_taskPause(task_id, RidgeBot_API_URL, taskStatusHeader)

        #use task_id to clone task
        _handle_taskClone(task_id, RidgeBot_API_URL, taskStatusHeader)

        #use task_id to delete task
        _handle_taskDelete(targets, RidgeBot_API_URL, taskStatusHeader) 
        
        #use task_id to start task
        _handle_taskStart(task_id, RidgeBot_API_URL, taskStatusHeader) 

        #use task_id to restart task
        _handle_taskRestart(task_id, RidgeBot_API_URL, taskStatusHeader)


        # Save all generated reports to a Reports Folder
        reportFolderName = task_name + 'Reports'
        if os.path.exists(os.getcwd() + "/" + reportFolderName):
          print(os.getcwd()+ "/" + reportFolderName)
          print('Warning: a folder with the same name exists')
        else:
          os.makedirs(reportFolderName)

        # Generate and download a CSV and PDF report
        # reportDict: a dictionary containing the reportName and report_id returned from function
        reportDict = _handle_generateReport(task_id, RidgeBotAuthToken, "pdf", create_time, task_name, RidgeBot_API_URL)
        _handle_downloadReport(task_name + createat, reportDict['report_id'], "pdf", reportFolderName, RidgeBot_API_URL, default_RidgeBot_API_Header)
        # reportDict = generateReport(task_id, RidgeBotAuthToken, "csv", create_time, task_name, RidgeBot_API_URL)
        # downloadReport(task_name + createat, reportDict['report_id'], "csv", reportFolderName, RidgeBot_API_URL, default_RidgeBot_API_Header)
        
        

       
       
       
        
        
main()

