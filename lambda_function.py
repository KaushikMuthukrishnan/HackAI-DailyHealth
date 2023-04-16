import json
import boto3
import urllib3
import time

print('Loading function')

def lambda_handler(event, context):
	#1. Parse out query string params
	user = event['queryStringParameters']['user']
	message = event['queryStringParameters']['message']
	history = ' '

	print(message)
	print(user)
	
	dynamodb = boto3.resource('dynamodb')
	table_name = 'user_health_history'
	table = dynamodb.Table(table_name)
	
	response = table.get_item(Key={"user_data": user})
	
	if "Item" in response:
		history = response["Item"]["history"]
		
	http = urllib3.PoolManager()
	
  
	headers = {
	'Authorization': 'Bearer 9352d87d-c9c4-4d1a-9406-d0e1f212b480',
	'Accept': 'application/json',
	'Content-Type': 'application/json'
	}

	data = {
	"spellId": "bfa331bS_13ohdc6j6NAO",
	"spellVersionId": 'SYK_IfCPbiZhYXQpxUXbX',
	"inputs": {
		"new_patient_history_summary": 'Create a concise bulleted list that only consists of my health concerns. Do not include any suggestions or treatment plans.',
		"state_problem": message,
		"patient_past_history": history,
		"therapist_personality": 'You are a therapist whose goal is to address my concerns and provide with me a plan on how to manage my situation and treat any physical or mental health problems that I have. Convey the plan to me like I am an elderly person and be sympathetic to my situation. If I had a good experience then encourage me to continue my habits and how to keep those habits consistent. Encourage me to talk about any physical health or mental health problems. Explain any causes of my problems. Give accurate advice on how to treat my situation through a check list of 5 concise steps. End responses by asking to elaborate on my health concerns or any situation that is troubling me.',
		}
	}
	
	
	encoded_data = json.dumps(data).encode('utf-8')
	
	
	response = http.request(
		'POST',
		'https://api.respell.ai/v1/run',
		headers=headers,
		body=encoded_data
	)  
	
	
	response = response.data.decode('utf-8')
  
	response = json.loads(response)


	#2. Construct the body of the response object
	transactionResponse = {}
	transactionResponse['message'] = response['outputs']['therapist_response']

	newhist = response['outputs']['converted_patient_history']
	table.put_item(Item={"user_data": user, "history": newhist})
	
	#3. Construct http response object
	responseObject = {}
	responseObject['statusCode'] = 200
	responseObject['headers'] = {}
	responseObject['headers']['Content-Type'] = 'application/json'
	responseObject['body'] = json.dumps(transactionResponse)

	#4. Return the response object
	return responseObject
