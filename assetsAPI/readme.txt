run the assetsAPI.py to test the assets part of RidgeBot 4.0.

1. I recommend to uncomment statement part by part the in main function.

	for example,
	 #_handle_deleteHost test 6/18 Jiahao Wang !!!SUCCESS
 	# _handle_deleteHost(RidgeBotAPIURL,RidgeBotAPIHeader)
	 #_handle_deleteHost test 6/18 Jiahao Wang

	to test _handle_deleteHost you need uncomment the code like this:
	(only the code part)

 	#_handle_deleteHost test 6/18 Jiahao Wang !!!SUCCESS
 	  _handle_deleteHost(RidgeBotAPIURL,RidgeBotAPIHeader) <- run this line
 	#_handle_deleteHost test 6/18 Jiahao Wang

2.Tou can also modifly the content of  JSON payload as your wish:

	the name rule of related JSON payload will be "function name"+"Payload.json" (function name not include"_handle_")

	for example,
	The payload of "_handle_deleteHost" function is "deleteHostPayload.json"

	find the related the payload and modify the content to see the difference.

3.You can also check the request status from server's response

	for example,
 	the response of  "_handle_deleteHost" function is deleteHostResponse

4. There have some existed problem can be reproduced by the json payload in "Problem with JSON" file
5. There has a report to reflect some problems that I found right now.

---Jiahao Wang
	

