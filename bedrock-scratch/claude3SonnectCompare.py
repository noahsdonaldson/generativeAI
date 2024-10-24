import base64
import httpx
import boto3
import json

# image_url = "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg"
image_media_type = "image/jpeg"
# image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")

image_path1 = "tankless_water_heater-replacement-old1.jpg"
image_path2 = "tankless_water_heater-replacement-new1.jpg"

def image_prep(image_path):
    with open(image_path, "rb") as image_file:
        binary_data = image_file.read()
        base_64_encoded_data = base64.b64encode(binary_data)
        base64_string = base_64_encoded_data.decode('utf-8')
        image_data = base64_string
    return image_data    

image_data_old = image_prep(image_path1)
image_data_new = image_prep(image_path2)

bedrock_rt = boto3.client("bedrock-runtime")

def create_claude_body(messages = [
                         {"role": "user", "content": "Hello"}
                        ], 
                       token_count=150, 
                       temp=0, 
                       topP=1,
                       topK=250, 
                       stop_sequence=["Human"]):
    """
    Simple function for creating a body for Anthropic Claude models.
    """
    body = {
        "messages": messages,
        "max_tokens": token_count,
        "temperature": temp,
        "anthropic_version":"",
        "top_k": topK,
        "top_p": topP,
        "stop_sequences": stop_sequence
    }
    return body

def get_claude_response(messages="", 
                        system="",
                        token_count=250, 
                        temp=0,
                        topP=1, 
                        topK=250, 
                        stop_sequence=["Human:"], 
                        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"):
    """
    Simple function for calling Claude via boto3 and the invoke_model API. 
    """
    body = create_claude_body(messages=messages, 
                              token_count=token_count, 
                              temp=temp,
                              topP=topP, 
                              topK=topK, 
                              stop_sequence=stop_sequence)
    response = bedrock_rt.invoke_model(modelId=model_id, body=json.dumps(body))
    response = json.loads(response['body'].read().decode('utf-8'))
    return response
    
prompt = [{"role": "user", "content": [
  {
    "type": "image",
    "source": {
      "type": "base64",
      "media_type": image_media_type, # png, jpeg
      "data": image_data_old,
    }
  },
  {
    "type": "image",
    "source": {
      "type": "base64",
      "media_type": image_media_type, # png, jpeg
      "data": image_data_new,
    }
  },
  {"type": "text", "text": "How are these images different? Provide confidence in your response"}
]}]
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
text_resp = get_claude_response(messages=prompt, 
                                 token_count=250, 
                                 temp=0,
                                 topP=1, 
                                 topK=0, 
                                 stop_sequence=["Human:"], 
                                 model_id = model_id)
print(text_resp['content'][0]['text'])