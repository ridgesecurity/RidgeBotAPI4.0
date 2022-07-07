#!/usr/bin/python3
import urllib3
import time
import sys 
import requests
import base64
import json
import os
import zipfile
import pandas as pd
import shutil
from datetime import datetime


###############################################################################################
# Common Functions



def encodeCredentials(auth):
  auth_bytes = auth.encode('ascii')
  base64_bytes = base64.b64encode(auth_bytes)
  base64_auth = base64_bytes.decode('ascii')
  return 'Basic ' + base64_auth

#create periodic tasks (weekly or monthly)
# targets: an array of targets
# task_name: a name string
# periodicType: "week" or "month"
# startTime: example: "12:06"
# end_date: example: "2022-07-07 14:48"
# pause_start: pause start time, example: "05:06"
# pause_end: pause end time, example: "11:08"
# RidgeBotAPIURL: "https://bot58.ridgesecurity.ai/api/v4"
# RidgeBotAPIHeader: {'Authorization': YourRidgeBotAuthToken, 'Content-Type':'application/json'}
# scenario_template: Integer
def _handle_createPeriodicTask(targets, task_name, periodicType, startTime, end_date, pause_start, pause_end, RidgeBotAPIURL, RidgeBotAPIHeader, scenario_template=6):
  # Create a task using RidgeBot API
  RidgeBotRequestURL = RidgeBotAPIURL + "/tasks"

  # Open and modify JSON file with payload information
  if periodicType == "week": #Weekly attack mode
    with open("createWeeklyTaskPayload.json") as createTaskJSONfile:
      createTaskPayload = json.load(createTaskJSONfile)
      createTaskPayload['name'] = task_name
      createTaskPayload['schedule']['type'] = periodicType
      createTaskPayload['schedule']['time'] = startTime
      createTaskPayload['schedule']['end_date'] = end_date
      createTaskPayload['schedule']['pause_start'] = pause_start
      createTaskPayload['schedule']['pause_end'] = pause_end
      for target in targets:
        createTaskPayload['targets'].append(target)
      createTaskPayload['template_id'] = scenario_template
      createTaskJSONfile.close()
  elif periodicType == "month": #Monthly attack mode
    with open("createMonthlyTaskPayload.json") as createTaskJSONfile:
      createTaskPayload = json.load(createTaskJSONfile)
      createTaskPayload['name'] = task_name
      createTaskPayload['schedule']['type'] = periodicType
      createTaskPayload['schedule']['time'] = startTime
      createTaskPayload['schedule']['end_date'] = end_date
      createTaskPayload['schedule']['pause_start'] = pause_start
      createTaskPayload['schedule']['pause_end'] = pause_end
      for target in targets:
        createTaskPayload['targets'].append(target)
      createTaskPayload['template_id'] = scenario_template
      createTaskJSONfile.close()
  else:
    print("Periodic type is wrong.")
    exit()

#post create task request and get response
#@param periodicType: "week" or "month"
#@param targets: an array of targets
#@param time: start time, example: "12:06"
#@param end_date: end date, example: "2022-07-07 14:48"
#@param pause_start: pause start time, example: "05:06"
#@param pause_end: pause end time, example: "11:08"
  createTaskResponse = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = createTaskPayload)

  if createTaskResponse.status_code != 200 or createTaskResponse.json()["code"] == 400:
    print("\nTask create unsuccessful. Possible RidgeBot authentication user error.\n")
    print(createTaskResponse.json())
    exit()

  task_id = createTaskResponse.json()['data']['task_id']
  print("\nTask creation successful. task_id:", task_id, '\n')
  return task_id

#create one-time tasks (run now or run once)
# targets: an array of targets
# task_name: a name string
# periodicType: "week" or "month"
# pending_time: example: "2022-07-25 08:47"
# pause_start: pause start time, example: "05:06"
# pause_end: pause end time, example: "11:08"
# RidgeBotAPIURL: "https://bot58.ridgesecurity.ai/api/v4"
def _handle_createOneTimeTask(targets, task_name, periodicType, pause_start, pause_end, pending_time, RidgeBotAPIURL, RidgeBotAPIHeader, scenario_template=6):
    # Create a task using RidgeBot API
  RidgeBotRequestURL = RidgeBotAPIURL + "/tasks"
  
  # Open and modify JSON file with payload information
  if periodicType == "run now": #run now mode
    with open("createTaskPayload.json") as createTaskJSONfile:
      createTaskPayload = json.load(createTaskJSONfile)
      createTaskPayload['name'] = task_name
      createTaskPayload['schedule']['pause_start'] = pause_start
      createTaskPayload['schedule']['pause_end'] = pause_end
      for target in targets:
        createTaskPayload['targets'].append(target)
      createTaskPayload['template_id'] = scenario_template
      createTaskJSONfile.close()
  elif periodicType == "run once":  #run once mode
    with open("createRunOnceTaskPayload.json") as createTaskJSONfile:
      createTaskPayload = json.load(createTaskJSONfile)
      createTaskPayload['name'] = task_name
      createTaskPayload['schedule']['pause_start'] = pause_start
      createTaskPayload['schedule']['pause_end'] = pause_end
      createTaskPayload['schedule']['pending_time'] = pending_time
      for target in targets:
        createTaskPayload['targets'].append(target)
      createTaskPayload['template_id'] = scenario_template
      createTaskJSONfile.close()
  else:
    print("Periodic type is wrong.")
    exit()

  #post create task request and get response
  createTaskResponse = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = createTaskPayload)

  if createTaskResponse.status_code != 200 or createTaskResponse.json()["code"] == 400:
    print("\nTask create unsuccessful. Possible RidgeBot authentication user error.\n")
    print(createTaskResponse.json())
    exit()

  task_id = createTaskResponse.json()['data']['task_id']
  print("\nTask creation successful. task_id:", task_id, '\n')
  return task_id

#use task_id to getTaskStatus
# callHeader{'Authorization': YourRidgeBotAuthToken, 'Content-Type':'application/json'}
# task_id: the id of the task
# RidgeBotAPIURL: "https://bot58.ridgesecurity.ai/api/v4"
def _handle_getTaskStatus(callHeader, task_id, RidgeBotAPIURL):
  # Get the task completion status. Make sure task is finished before 
  # trying to generate a report
  RidgeBotRequestURL = RidgeBotAPIURL + "/tasks?task_id=" + task_id
  taskStatusHeader = callHeader
  # Get Running Status
  taskStatusResponse = requests.get(RidgeBotRequestURL, headers = taskStatusHeader, verify = False)
  # You can still generate a report from an abort/stopped task, but you cannot generate a report
  # if the task is paused.
  try:
    running_status = taskStatusResponse.json()['data']['running_status']
  except IOError as e:
    print('The task ID is invalide')
    exit()
  
  #print('\n*** ' + runIteration + ' Task In Progress ***')
  print("running_status: 1 means incomplete/running, 2 means paused, 3 means aborted/stopped, 4 means complete")
  
  #2022/06/17 Jiahao Wang added
  if running_status == 1:
    print("running_status: 1 means incomplete/running")
  elif running_status == 2:
    print("running_status: 2 means paused")
  elif running_status == 3:
    print("running_status: 3 means aborted/stopped")
  elif running_status == 4:
    print("running_status: 4 means complete")
  #To judge the running status and print in the terminal

  while running_status == 1: 
    print("Waiting for task to finish running. running_status: ", running_status, " Trying again in 10 seconds.")
    time.sleep(10)
    taskStatusResponse = requests.get(RidgeBotRequestURL, headers = taskStatusHeader, verify = False)
    running_status = taskStatusResponse.json()['data']['running_status']
  print(running_status)
  return running_status
  

#use task_id to stop task
# task_id: the id of the task
#RidgeBotAPIURL: "https://bot58.ridgesecurity.ai/api/v4"
#RidgeBotAPIHeader{'Authorization': YourRidgeBotAuthToken, 'Content-Type':'application/json'}			
def _handle_taskStop(taskId, RidgeBotAPIURL, RidgeBotAPIHeader):
  RidgeBotRequestURL = RidgeBotAPIURL + "/tasks/stop"
  with open("generalTaskPayload.json") as taskStopFile:
    taskStopPayload = json.load(taskStopFile)
    taskStopPayload['task_id'] = taskId
  stopTaskResponse = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = taskStopPayload)
  if stopTaskResponse.status_code != 200 or stopTaskResponse.json()["code"] == 400:
    print("\nTask stop unsuccessful. Possible RidgeBot authentication user error.\n")
    print(stopTaskResponse.json())
    exit()
  print("task id stopped: " + stopTaskResponse)

#use task_id to pause task
# task_id: the id of the task
# RidgeBotAPIURL: "https://bot58.ridgesecurity.ai/api/v4"
# RidgeBotAPIHeader{'Authorization': YourRidgeBotAuthToken, 'Content-Type':'application/json'}			
def _handle_taskPause(taskId, RidgeBotAPIURL, RidgeBotAPIHeader):
  RidgeBotRequestURL = RidgeBotAPIURL + "/tasks/pause"
  with open("generalTaskPayload.json") as taskPauseFile:
    taskPausePayload = json.load(taskPauseFile)
    taskPausePayload['task_id'] = taskId
  pauseTaskResponse = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = taskPausePayload)
  if pauseTaskResponse.status_code != 200 or pauseTaskResponse.json()["code"] == 400:
    print("\nTask pause unsuccessful. Possible RidgeBot authentication user error.\n")
    print(pauseTaskResponse.json())
    exit()
  print(pauseTaskResponse)

#use task_id to get taskInfo task
# task_id: the id of the task
# RidgeBotAPIURL: "https://bot58.ridgesecurity.ai/api/v4"
# RidgeBotAPIHeader{'Authorization': YourRidgeBotAuthToken, 'Content-Type':'application/json'}	
def _handle_taskInfo(taskId, RidgeBotAPIURL, RidgeBotAPIHeader):
  RidgeBotRequestURL = RidgeBotAPIURL + "/tasks/info"
  with open("generalTaskPayload.json") as taskinfoFile:
    taskinfoPayload = json.load(taskinfoFile)
    taskinfoPayload['task_id'] = taskId
  response = requests.get(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = taskinfoPayload)
  if response.status_code != 200 or response.json()["code"] == 400:
    print("\nGet task info unsuccessful. Possible RidgeBot authentication user error.\n")
    print(response.json())
    exit()
  print(response.json()["data"])
  return response.json()["data"]

#use task_id to get taskStatistics task
# task_id: the id of the task
# RidgeBotAPIURL: "https://bot58.ridgesecurity.ai/api/v4"
# RidgeBotAPIHeader{'Authorization': YourRidgeBotAuthToken, 'Content-Type':'application/json'}	
def _handle_taskStatistics(taskId, RidgeBotAPIURL, RidgeBotAPIHeader):
  RidgeBotRequestURL = RidgeBotAPIURL + "/tasks/statistics?task_id="+taskId
  response = requests.get(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False)
  if response.status_code != 200 or response.json()["code"] == 400:
    print("\nGet task statistics unsuccessful. Possible RidgeBot authentication user error.\n")
    print(response.json())
    exit()
  taskStatistics_content=response._content
  print(taskStatistics_content)
  return taskStatistics_content

#use task_id to delete task
# targets: an array of target task ids
# RidgeBotAPIURL: "https://bot58.ridgesecurity.ai/api/v4"
# RidgeBotAPIHeader{'Authorization': YourRidgeBotAuthToken, 'Content-Type':'application/json'}			
def _handle_taskDelete(targets, RidgeBotAPIURL, RidgeBotAPIHeader):
  RidgeBotRequestURL = RidgeBotAPIURL + "/tasks/delete"
  with open("deleteTaskPayload.json") as taskdeleteFile:
    taskdeletePayload = json.load(taskdeleteFile)
    for target in targets:
      taskdeletePayload['tasks_id'].append(target)

  deleteTaskResponse = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = taskdeletePayload)
  if deleteTaskResponse.status_code != 200 or deleteTaskResponse.json()["code"] == 400:
    print("\nTask stop unsuccessful. Possible RidgeBot authentication user error.\n")
    print(deleteTaskResponse.json())
    exit()
  print(deleteTaskResponse)

#use task_id to clone task
# task_id: the id of the task
# RidgeBotAPIURL: "https://bot58.ridgesecurity.ai/api/v4"
# RidgeBotAPIHeader{'Authorization': YourRidgeBotAuthToken, 'Content-Type':'application/json'}		
def _handle_taskClone(taskId, RidgeBotAPIURL, RidgeBotAPIHeader):
  RidgeBotRequestURL = RidgeBotAPIURL + "/tasks/clone"
  with open("generalTaskPayload.json") as taskcloneFile:
    taskclonePayload = json.load(taskcloneFile)
    taskclonePayload['task_id'] = taskId
  cloneTaskResponse = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = taskclonePayload)
  if cloneTaskResponse.status_code != 200 or cloneTaskResponse.json()["code"] == 400:
    print("\nTask clone unsuccessful. Possible RidgeBot authentication user error.\n")
    print(cloneTaskResponse.json())
    exit()
  print(cloneTaskResponse)

#use task_id to start task
# task_id: the id of the task
# RidgeBotAPIURL: "https://bot58.ridgesecurity.ai/api/v4"
# RidgeBotAPIHeader{'Authorization': YourRidgeBotAuthToken, 'Content-Type':'application/json'}		
def _handle_taskStart(taskId, RidgeBotAPIURL, RidgeBotAPIHeader):
  RidgeBotRequestURL = RidgeBotAPIURL + "/tasks/start"
  with open("generalTaskPayload.json") as taskStartFile:
    taskStartPayload = json.load(taskStartFile)
    taskStartPayload['task_id'] = taskId
  startTastResponse = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = taskStartPayload)
  if startTastResponse.status_code != 200 or startTastResponse.json()["code"] == 400:
    print("\nTask start unsuccessful. Possible RidgeBot authentication user error.\n")
    print(startTastResponse.json())
    exit()
  print(startTastResponse)  

#use task_id to restart task
# task_id: the id of the task
# RidgeBotAPIURL: "https://bot58.ridgesecurity.ai/api/v4"
# RidgeBotAPIHeader{'Authorization': YourRidgeBotAuthToken, 'Content-Type':'application/json'}		
def _handle_taskRestart(taskId, RidgeBotAPIURL, RidgeBotAPIHeader):
  RidgeBotRequestURL = RidgeBotAPIURL + "/tasks/restart"
  with open("generalTaskPayload.json") as taskRestartFile:
    taskRestartPayload = json.load(taskRestartFile)
    taskRestartPayload['task_id'] = taskId
  restartTastResponse = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = taskRestartPayload)
  if restartTastResponse.status_code != 200 or restartTastResponse.json()["code"] == 400:
    print("\nTask restart unsuccessful. Possible RidgeBot authentication user error.\n")
    print(restartTastResponse.json())
    exit()
  print(restartTastResponse)
  
#save tasks (run now, run once, weekly or monthly) (incomplete)
def _handle_saveTask(targets, task_name, periodicType, time, end_date, pause_start, pause_end, pending_time, RidgeBotAPIURL, RidgeBotAPIHeader, scenario_template=6):
    # Create a task using RidgeBot API
  RidgeBotRequestURL = RidgeBotAPIURL + "/tasks/draft/save"

  if periodicType == "run now":
    # Open and modify JSON file with payload information
    with open("saveTaskPayload.json") as createTaskJSONfile:
      createTaskPayload = json.load(createTaskJSONfile)
      
  elif periodicType == "run once":
    with open("createRunOnceTaskPayload.json") as createTaskJSONfile:
      createTaskPayload = json.load(createTaskJSONfile)
      createTaskPayload['name'] = task_name
      createTaskPayload['schedule']['pause_start'] = pause_start
      createTaskPayload['schedule']['pause_end'] = pause_end
      createTaskPayload['schedule']['pending_time'] = pending_time
      for target in targets:
        createTaskPayload['targets'].append(target)
      createTaskPayload['template_id'] = scenario_template
      createTaskJSONfile.close()
      print (createTaskPayload['targets'])
  elif periodicType == "week":
    with open("createWeeklyTaskPayload.json") as createTaskJSONfile:
      createTaskPayload = json.load(createTaskJSONfile)
      createTaskPayload['name'] = task_name
      createTaskPayload['schedule']['type'] = periodicType
      createTaskPayload['schedule']['time'] = time
      createTaskPayload['schedule']['end_date'] = end_date
      createTaskPayload['schedule']['pause_start'] = pause_start
      createTaskPayload['schedule']['pause_end'] = pause_end
      for target in targets:
        createTaskPayload['targets'].append(target)
      createTaskPayload['template_id'] = scenario_template
      createTaskJSONfile.close()
      print (createTaskPayload['schedule'])
  elif periodicType == "month":
    with open("createMonthlyTaskPayload.json") as createTaskJSONfile:
      createTaskPayload = json.load(createTaskJSONfile)
      createTaskPayload['name'] = task_name
      createTaskPayload['schedule']['type'] = periodicType
      createTaskPayload['schedule']['time'] = time
      createTaskPayload['schedule']['end_date'] = end_date
      createTaskPayload['schedule']['pause_start'] = pause_start
      createTaskPayload['schedule']['pause_end'] = pause_end
      for target in targets:
        createTaskPayload['targets'].append(target)
      createTaskPayload['template_id'] = scenario_template
      createTaskJSONfile.close()
      print (createTaskPayload['schedule'])
  else:
    print("Periodic type is wrong.")
    exit()

  createTaskResponse = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = createTaskPayload)

  if createTaskResponse.status_code != 200 or createTaskResponse.json()["code"] == 400:
    print("\nTask create unsuccessful. Possible RidgeBot authentication user error.\n")
    print(createTaskResponse.json())
    exit()

  task_id = createTaskResponse.json()['data']['task_id']
  print("\nTask creation successful. task_id:", task_id, '\n')
  return task_id



def convertNameToDate(str) :
  name_array = str.split("_")
  date_time_array = name_array[1].split("-")
  date_time_str = ""
  for i in range(0, len(date_time_array)):
    if i < 2:
      date_time_str = date_time_str +  date_time_array[i] + "/"
    elif i == 2:
      date_time_str = date_time_str +  date_time_array[i]  + " "
    else:
      date_time_str  = date_time_str +  date_time_array[i]

  return name_array[0], datetime.strptime(date_time_str[2:], '%y/%m/%d %H:%M:%S')


# # Use task_id and report type to generate a report
# task_id: the id of the task
# RidgeBotAuthToken: {'Authorization': YourRidgeBotAuthToken, 'Content-Type':'application/json'}
# reportType: "pdf" or "csv"
# runIteration: whether this is the first time running the task or second time
# RidgeBotAPIURL: "https://bot58.ridgesecurity.ai/api/v4"
def _handle_generateReport(task_id, RidgeBotAuthToken, reportType, runIteration, RidgeBotAPIURL):
  # Generate and download a CSV report from the task just created
  RidgeBotRequestURL = RidgeBotAPIURL + "/tasks?task_id=" + task_id
   # Get Running Status
  taskStatusHeader = {'Authorization': RidgeBotAuthToken, 'task_id': task_id}
  taskStatusResponse = requests.get(RidgeBotRequestURL, headers = taskStatusHeader, verify = False)
  # Check the running status to see if the task is complete.
  try:
    running_status = taskStatusResponse.json()['data']['running_status']
  except IOError as e:
    print('The task ID is invalid')
    exit()
  if running_status != 4:
    print("The task is not complete, unable to generate reports")
    exit()

  RidgeBotAPIHeader = {'Authorization': RidgeBotAuthToken, 'Content-Type':'application/json'}
  RidgeBotRequestURL = RidgeBotAPIURL + "/report/generate"
  with open("createReportPayload.json") as createReportJSONfile:
    createReportPayload = json.load(createReportJSONfile)
    createReportPayload['task_id'] = task_id
    createReportPayload['type'] = reportType
    # template number means what kind of report is generated
    # 0 means a "custom" PDF report, 3 means "raw data" or CSV report
    createReportPayload['template'] = 0 if reportType == 'pdf' else 3
    createReportJSONfile.close()

    requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = createReportPayload)

 
  # Get PDF report from the /report/ endpoint
  RidgeBotRequestURL = RidgeBotAPIURL + "/report/"
  getReportCall = requests.get(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False)
  report_id = -1
  
  # Find the report_id given the file type of report
  create_time=datetime.strptime(runIteration, '%y/%m/%d %H:%M:%S')
  min = create_time - datetime.strptime("07:00:00", "%H:%M:%S")
  report_name =""
  for report in getReportCall.json()['data']:
    report_name, reportTime = convertNameToDate(report['name'])
    if report['report_type'] == reportType and report['task_id'] == task_id and min > create_time - reportTime:
        min = create_time - reportTime
        report_id = report['id']

  print("\n*** " + runIteration + " Report Generation In Progress (" + reportType+ ") ***\n")
  print("report_status: 1 means running, 2 means finished, 3 means report generation failed")
  # wait until the report is fully generated
  reportCompleted = False 
  while(not reportCompleted):
    getReportCall = requests.get(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False)
    # parse the GET call for the report status
    for report in getReportCall.json()['data']:

      if report['id'] == report_id:              
        # check if the report failed to generate
        if report['status'] == 3:
          print("\nERROR GENERATING REPORT")
          sys.exit()
        elif report['status'] == 2:
          print("\nReport successfully generated!\n")
          reportCompleted = True
          break
        else:
          print("Waiting for report to generate. Report status: ", report['status'], "Trying again in 5 seconds.")
          time.sleep(5)
  
  reportDict = {'reportName' : report_name, 'report_id': report_id}
  
  print("Report Information: ", reportDict)

  return reportDict


# Download the report 
# report_id: the number ID of the generated report
# report type: either CSV or PDF
# report_name: the name you want give to the report 
# report_id: the id of the report
# reportType: "pdf" or "csv"
# folderName: the foldername you want put the report in
# RidgeBotAPIURL: "https://bot58.ridgesecurity.ai/api/v4"
# RidgeBotAPIHeader: {'Authorization': YourRidgeBotAuthToken, 'Content-Type':'application/json'}
def _handle_downloadReport(report_name, report_id, reportType, folderName, RidgeBotAPIURL, RidgeBotAPIHeader):
  RidgeBotRequestURL = RidgeBotAPIURL + "/report/download"
  downloadReportCall = requests.post(RidgeBotRequestURL, \
  headers=RidgeBotAPIHeader, stream=True, verify = False, \
  json = {"ids": [report_id]})

  if reportType == "pdf":
    reportFileName = report_name + "." + reportType
  else:
    reportFileName = report_name + ".zip" 

  # Download file returned by the POST call
  # wb: write mode, binary file
  path = folderName + "/" + reportFileName
  with open(path, 'wb') as fd:
      for chunk in downloadReportCall.iter_content(chunk_size=128):
          fd.write(chunk) 

  print("Report downloaded in the following directory:", folderName + "/" + reportFileName) 

    
def _handle_mergeTwoCSV(CSV_name, reportFolderName, firstReportFolder, secondReportFolder, create_time):
  use_file = ''
  trendfilename = firstReportFolder + CSV_name[:-4] +'_trend.csv'
  try:
    A = pd.read_csv(trendfilename)
  except IOError as e:
    print ('first run missing file', CSV_name)
    use_file = 'b'
  try:
    B = pd.read_csv(secondReportFolder + CSV_name)
  except IOError as e:
    print ('second run missing file', CSV_name)
    use_file = 'a'
  
  #do raw data prcess: add create_time for iteration
  if ('site' in CSV_name):
    B['Iteration'] = create_time
    B=B.drop(columns='Index')
  elif ('ip' in CSV_name):
    B=B.rename(columns={'Attack surface':'Attack surface'+create_time})
    B=B.drop(columns=['Index', 'Nums of risk', 'Active', 'Nums of vulnerability'])
  elif ('url' in CSV_name):
    B['Iteration'] = create_time
    B=B.drop(columns='Index')
  elif ('port' in CSV_name):
    B['Iteration'] = create_time
    B=B.drop(columns='Index')
  elif ('domain' in CSV_name):
    B['Iteration'] = create_time
    B=B.drop(columns='Index')
  elif ('risk.csv' in CSV_name):
    #Should change Type to risk name
    B['Iteration'] = create_time
    B=B.drop(columns='Index')
  elif ('vulnerability.csv' in CSV_name):
    B['Iteration'] = create_time
    B=B.drop(columns=['Index','Description','Reference','Cve-Number','Cvss Vector', 'Cvss Score', 'Remediation'])

  if (use_file == ''):
    if ('summary' in CSV_name):
      csvCountSummaryDF = pd.merge(A, B, on='Type', how='outer')
    elif ('risk_count' in CSV_name):
      csvCountSummaryDF = pd.merge(A, B, on=['Type', 'Target'], how='outer')
    elif ('based_severity' in CSV_name):
      csvCountSummaryDF = pd.merge(A, B, on=['Type', 'Target'], how='outer')
    elif ('based_type' in CSV_name):
      csvCountSummaryDF = pd.merge(A,B, on=['Type', 'Severity', 'Target'], how='outer')
      csvCountSummaryDF=csvCountSummaryDF.sort_values('Severity',ascending=True)
    elif ('site' in CSV_name):
      csvCountSummaryDF = pd.merge(A,B, on=['Site', 'Server','Title','Language','Framework','Waf/CDN Type'], how='outer')
    elif ('ip' in CSV_name):
      csvCountSummaryDF = pd.merge(A,B, on=['IP', 'System Version'], how='outer')
    elif ('url' in CSV_name):
      csvCountSummaryDF = pd.merge(A,B, on=['URL', 'Method', 'Label Type', 'Params'], how='outer')
    elif ('port' in CSV_name):
      csvCountSummaryDF = pd.merge(A,B, on=['IP', 'Port', 'Service', 'Application'], how='outer')
    elif ('domain' in CSV_name):
      csvCountSummaryDF = pd.merge(A,B, on=['Domain', 'IP', 'Nums of risk','Attack surface', 'Nums of vulnerability'], how='outer')
    elif ('risk.csv' in CSV_name):
      csvCountSummaryDF = pd.merge(A,B, on=['Type', 'Related Vulnerability', 'Impacted Node'], how='outer')
    elif ('vulnerability.csv' in CSV_name):
      csvCountSummaryDF = pd.merge(A,B, on=['Title', 'Severity', 'Affected node'], how='outer')
  elif (use_file == 'a'):
    csvCountSummaryDF = A
  elif (use_file == 'b'):
    csvCountSummaryDF = B
  csvCountSummaryDF.to_csv(trendfilename, index=False)
  
