import base64
import httpx
import boto3
import json
import io

# image_url = "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg"
image_media_type = "image/jpeg"
# image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")

image_path = "WFBankStatement-page1.png"
with open(image_path, "rb") as image_file:
  binary_data = image_file.read()
  base_64_encoded_data = base64.b64encode(binary_data)
  base64_string = base_64_encoded_data.decode('utf-8')
image_data = base64_string   

# print(image_data)

# bucket = "bedrockimagetotextsamples-imagecomparebucketc53067-qjjczzgcxtue"
# key = "broken-electrical-outlet.jpg"

# s3 = boto3.resource('s3')

# obj = s3.Object(bucket, key)
# obj_string = obj.get()['Body'].read()
# image_data = base64.b64encode(obj_string).decode("utf-8")


bedrock_rt = boto3.client("bedrock-runtime")
token_count=150 
temp=0 
topP=1
topK=250
model_id='anthropic.claude-3-sonnet-20240229-v1:0' 
stop_sequence=["Human"]

def get_claude_response():
    prompt = [{"role": "user", "content": [
       {
        "type": "image",
        "source": {
          "type": "base64",
          "media_type": image_media_type, # png, jpeg
          "data": image_data,
        }
      },
      {"type": "text", "text": "You are a highly expierenced home repair assistant.  Please explain the repairs needed in each image."}
    ]}]
    body = {
        "messages": prompt,
        "max_tokens": token_count,
        "temperature": temp,
        "anthropic_version":"",
        "top_k": topK,
        "top_p": topP,
        "stop_sequences": stop_sequence
    }
    response = bedrock_rt.invoke_model(modelId=model_id, body=json.dumps(body))
    response = json.loads(response['body'].read().decode('utf-8'))
    print(response['content'][0]['text'])
    return response

 
get_claude_response()