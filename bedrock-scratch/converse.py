import os
import base64
import boto3
import json
from botocore.config import Config

model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'

bedrock_client = boto3.client('bedrock-runtime',region_name='us-east-1')
file = 'TamperedBankStatement_10.jpg'

# Read reference image from file and encode as base64 strings.
with open(file, "rb") as image_file:
    content_image = base64.b64encode(image_file.read()).decode('utf8')

def generate_message(bedrock_runtime, model_id, messages, max_tokens,top_p,temp):

    body=json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temp,
            "top_p": top_p
        }  
    )  
    
    response = bedrock_runtime.invoke_model(body=body, modelId=model_id)
    response_body = json.loads(response.get('body').read())

    return response_body

prompt = "Classify the document"


message_mm=[

    { "role": "user",
      "content": [
      {"type": "image","source": { "type": "base64","media_type":"image/jpeg","data": content_image}},
      {"type": "text","text":prompt}
      ]
    }
]

response = generate_message(bedrock_client, model_id = "anthropic.claude-3-sonnet-20240229-v1:0",messages=message_mm,max_tokens=1024,temp=0.5,top_p=0.9)


print(response['content'][0]['text'])



