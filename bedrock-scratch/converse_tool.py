import os
import base64
import boto3
import json
from botocore.config import Config

model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'

bedrock_client = boto3.client('bedrock-runtime',region_name='us-east-1')
file = 'TamperedBankStatement_10.jpg'

# # Read reference image from file and encode as base64 strings.
# with open(file, "rb") as image_file:
#     content_image = base64.b64encode(image_file.read()).decode('utf8')

# Read reference image from file and encode as base64 strings.
with open(file, "rb") as image_file:
    content_image = image_file.read()

tools =[
    {
        "toolSpec": {
            "name": "doc_class",
            "description": "Classify the document as a document type like a bank statement or a w-2",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "doc_class": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "document_type": {"type": "string", "description": "The name of the document type"},
                                    "context": {"type": "string", "description": "The context used to classify the document type in the text."}
                                },
                                "required": ["document_type", "context"]
                            }
                        }
                    },
                    "required": ["doc_class"]
                }
            }
        }
    }
]

prompt = '''
What kind of document is this

Use the doc_class tool
'''

message_mm = [
    {
        "role": "user",
        "content": [
            {
                "text": prompt
            },
            {
                    "image": {
                        "format": "jpeg",
                        "source": {
                            "bytes": content_image
                        }
                    }
            }
        ]
    }
]

response = bedrock_client.converse(
    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
    inferenceConfig={
        "temperature": 1.0,
        "maxTokens": 2048
    },
    messages=message_mm,
    toolConfig={"tools": tools}
)

print(json.dumps(response['output']['message']['content'][0]['toolUse']['input'],indent=2))




