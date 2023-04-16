import boto3
import json
import urllib3
import time

def respond(err, res=None):
  return {
      'statusCode': '400' if err else '200',
      'body': err.message if err else json.dumps(res),
      'headers': {
          'Content-Type': 'application/json',
      },
}

def lambda_handler(event: any, context: any):
  print('event: ', json.dumps(event))

  # Prepare the DynamoDB client
  dynamodb = boto3.resource("dynamodb")
  table_name = 'user_health_history'
  table = dynamodb.Table(table_name)

  user: str = event["user_data"]
  message : str = event["message"]
  history: str =' '
  
  ##########
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
  
  ##############
  response = http.request(
      'POST',
      'https://api.respell.ai/v1/run',
      headers=headers,
      body=encoded_data
  )  
  
  #########
  response = response.data.decode('utf-8')
  
  ###
  time.sleep(3)
  response = json.loads(response)
  
  ######
  respell_out: str = response['outputs']['therapist_response']
  respell_new_hist: str = response['outputs']['converted_patient_history']
  
  print('\n')
  print(respell_out)
  print('\n')
  print(respell_new_hist)
  
  #######
  table.put_item(Item={"user_data": user, "history": respell_new_hist})

  message: str = f"Hello {user}! {respell_out}"
  # return respond(None, message)
  return respond(None, "Response is working!!!")
