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
#@param periodicType: "week" or "month"
#@param targets: an array of targets
#@param startTime: example: "12:06"
#@param end_date: example: "2022-07-07 14:48"
#@param pause_start: pause start time, example: "05:06"
#@param pause_end: pause end time, example: "11:08"
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
#@param periodicType: "run now" or "run once"
#@param targets: an array of targets
#@param pending_time: pending time, example: "2022-07-25 08:47"
#@param pause_start: pause start time, example: "05:06"
#@param pause_end: pause end time, example: "11:08"
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
#@param periodicType: "run now", "run once", "week" or "month"
#@param targets: an array of targets
#@param time: start time, example: "12:06"
#@param end_date: end date, example: "2022-07-07 14:48"
#@param pause_start: pause start time, example: "05:06"
#@param pause_end: pause end time, example: "11:08" 
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


# Use task_id and report type to generate a report
# runIteration means whether this is the first time running the task or second time
# Return: a dictionary containing the reportName and report_id
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




# # Get Risk Statistics data info CSV file
# def _handle_generateRstatistics(task_id, filepath, RidgeBotAPIURL, RidgeBotAPIHeader):
#   RidgeBotRequestURL = RidgeBotAPIURL + "/tasks/sensitive_statistics"
  
#   with open("createRStatistics.json") as createRStatisticsJSONfile:
#     createRStatisticsPayload = json.load(createRStatisticsJSONfile)
#     createRStatisticsPayload['task_id'] = task_id
  
#   createRStatisticsJSONfile.close()
  
#   generateRSatisticsResponse = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = createRStatisticsPayload)
#   statistics_target=generateRSatisticsResponse.json()

#   date_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
#   dt_summary = {'Type':[], date_time:[]}
#   dt_detail = {'Target': [],'Type':[], date_time:[]}
#   for each in statistics_target['data']['targets']:
#     dt_summary['Type'].append(each['value'])
#     dt_summary[date_time].append(each['count'])
#     with open("createRStatistics.json") as createRStatisticsJSONfile:
#       createRStatisticsPayload = json.load(createRStatisticsJSONfile)
#       createRStatisticsPayload['task_id'] = task_id
#       createRStatisticsPayload['filter_fields'][0]['value'] = [each['value']]
      
#       createRStatisticsJSONfile.close()
  
#       generateRSatisticsResponse_target = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False,json = createRStatisticsPayload)
     
#       statistics_R_target=generateRSatisticsResponse_target.json()
      
#       for detail in statistics_R_target['data']['sen_type']:
#         if (detail['value'] == 0):
#             detail['value'] = 'Command Execution'
#         elif (detail['value'] == 1):
#             detail['value'] = 'Credential Exposure'
#         elif (detail['value'] == 2):
#             detail['value'] = 'DataBase Manipulation'
#         elif (detail['value'] == 3):
#             detail['value'] = 'Sensitive Data Exfiltration'
#         else:
#             detail['value'] = 'Other'
#         dt_detail['Target'].append(each['value'])
#         dt_detail['Type'].append(detail['value'])
#         dt_detail[date_time].append(detail['count'])
        
#   df_detail= pd.DataFrame.from_dict(dt_detail)
#   df_detail.to_csv(filepath+"/"+ 'risk_count.csv', index=False)
  
#   df_summary = pd.DataFrame.from_dict(dt_summary)
#   df_summary.to_csv(filepath + "/" + 'risksummary.csv', index=False)
  
# # Get Vul statistics data into CSV file
# def _handle_generateVstatistics(task_id, filepath, RidgeBotAPIURL, RidgeBotAPIHeader):
#   RidgeBotRequestURL = RidgeBotAPIURL + "/tasks/vulnerabilities_statistics"
    
#   with open("createVStatistics.json") as createVStatisticsJSONfile:
#     createVStatisticsPayload = json.load(createVStatisticsJSONfile)
#     createVStatisticsPayload['task_id'] = task_id
  
#   createVStatisticsJSONfile.close()
  
#   generateVSatisticsResponse = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False, json = createVStatisticsPayload)
#   statistics_target=generateVSatisticsResponse.json()
#   targetindex = 0
#   date_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
#   dt_summary = {'Type':[], date_time:[]}
#   dt_type= {'Target':[], 'Type':[], 'Severity':[],date_time:[]}
#   dt_detail = {'Target':[],'Type':[], date_time:[]}
  
#   for each in statistics_target['data']['targets']:
#     dt_summary['Type'].append(each['value'])
#     dt_summary[date_time].append(each['count'])
#     with open("createVStatistics.json") as createVStatisticsJSONfile:
#       createVStatisticsPayload = json.load(createVStatisticsJSONfile)
#       createVStatisticsPayload['task_id'] = task_id
#       targetstr = each['value']
#       createVStatisticsPayload['filter_fields'][0]['value'] = [targetstr]
      
#       createVStatisticsJSONfile.close()
  
#       generateVSatisticsResponse_target = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False,json = createVStatisticsPayload)
     
#       statistics_1_target=generateVSatisticsResponse_target.json()
      
#       for detail in statistics_1_target['data']['severity']:
#         if (detail['value']== 'MIDDLE'):
#           detail['value'] = 'MEDIUM'
#         dt_detail['Type'].append(detail['value'])
#         dt_detail[date_time].append(detail['count'])
#         dt_detail['Target'].append(targetstr)
      
#       TableSeverity = 'High'
#       with open("createVStatistics_high.json") as createVHStatisticsJSONfile:
#         createVHStatisticsPayload = json.load(createVHStatisticsJSONfile)
#         createVHStatisticsPayload['task_id'] = task_id
#         createVHStatisticsPayload['filter_fields'][0]['value'] = [targetstr]
      
#       createVHStatisticsJSONfile.close()

#       generateVHSatisticsResponse_target = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False,json = createVHStatisticsPayload)
#       statistics_h_target=generateVHSatisticsResponse_target.json()
 
#       for type_detail in statistics_h_target['data']['vul_name']:
#         dt_type['Type'].append(type_detail['value'])
#         dt_type['Severity'].append(TableSeverity)
#         dt_type[date_time].append(type_detail['count'])
#         dt_type['Target'].append(targetstr)
        
#       TableSeverity = 'Medium'
#       with open("createVStatistics_medium.json") as createVMStatisticsJSONfile:
#         createVMStatisticsPayload = json.load(createVMStatisticsJSONfile)
#         createVMStatisticsPayload['task_id'] = task_id
#         createVMStatisticsPayload['filter_fields'][0]['value'] = [targetstr]
      
#       createVMStatisticsJSONfile.close()
      
#       generateVMSatisticsResponse_target = requests.post(RidgeBotRequestURL, headers=RidgeBotAPIHeader, verify=False,json = createVMStatisticsPayload)
     
#       statistics_m_target=generateVMSatisticsResponse_target.json()
#       for type_detail in statistics_m_target['data']['vul_name']:
#         dt_type['Type'].append(type_detail['value'])
#         dt_type['Severity'].append(TableSeverity)
#         dt_type[date_time].append(type_detail['count'])
#         dt_type['Target'].append(targetstr)
    
#   df_detail= pd.DataFrame.from_dict(dt_detail)
#   df_detail.to_csv(filepath+"/"+'vul_count_based_severity.csv', index=False)
  
#   df_type= pd.DataFrame.from_dict(dt_type)
#   df_type= df_type.sort_values('Severity',ascending=True)
#   df_type.to_csv(filepath+"/"+'vul_count_based_type.csv', index=False)
  
#   df_summary = pd.DataFrame.from_dict(dt_summary)
#   df_summary.to_csv(filepath + "/" + 'vulnsummary.csv', index=False)
#   #print('target Summary in directory: ', filepath)
    
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
  
