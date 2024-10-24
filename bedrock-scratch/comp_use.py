import boto3
import json

bedrock = boto3.client("bedrock-runtime")

with open('console.png', 'rb') as f:
        png = f.read()

response = bedrock.converse(
    modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
    messages=[
        {
            'role': 'user',
            'content': [
                {
                    'text': 'Go to the bedrock console'
                },
                {
                    'image': {
                        'format': 'png',
                        'source': {
                            'bytes': png
                        }
                    }
                }
            ]
        }
    ],
    additionalModelRequestFields={
        "tools": [
            {
                "type": "computer_20241022",
                "name": "computer",
                "display_height_px": 768,
                "display_width_px": 1024,
                "display_number": 0
            },
            {
                "type": "bash_20241022",
                "name": "bash",

            },
            {
                "type": "text_editor_20241022",
                "name": "str_replace_editor",
            }
        ],
        "anthropic_beta": ["computer-use-2024-10-22"]
    },
    toolConfig={
        'tools': [
            {
                'toolSpec': {
                    'name': 'get_weather',
                    'inputSchema': {
                        'json': {
                            'type': 'object'
                        }
                    }
                }
            }
        ]
    })

print(json.dumps(response, indent=4))