# Sample code, software libraries, command line tools, proofs of concept, templates, 
# or other related technology are provided as AWS Content or Third-Party Content under the AWS Customer Agreement, 
# or the relevant written agreement between you and AWS (whichever applies). 
# You should not use this AWS Content or Third-Party Content in your production accounts, 
# or on production or other critical data. You are responsible for testing, securing, 
# and optimizing the AWS Content or Third-Party Content, such as sample code, 
# as appropriate for production grade use based on your specific quality control practices and standards. 
# Deploying AWS Content or Third-Party Content may incur AWS charges for creating or using AWS chargeable resources, 
# such as running Amazon EC2 instances or using Amazon S3 storage.


import json
from os import getenv
import boto3
from datetime import datetime, timedelta, timezone
import re


def return_name(e_dict):
    if isinstance(e_dict, str):
        pass
    else:
        test_key = list(e_dict.keys())[0]
        if test_key == "properties":
            e_dict = e_dict['properties']['entities']
        else: 
            e_dict = e_dict['entities']
            # Sometimes the model returns a string instead of a list, put the string into a list    
            # e_dict = {e_dict} if isinstance(e_dict, str) else e_dict


        # list of names
        names = []
        for e in e_dict:
            if e["item_type"] == "ORGANIZATION" or e["item_type"] == "PERSON":
                # name = e["name"]
                # names.append(name)
                names.append(e)
        return names


def redaction(cust_names, entry):
    if not cust_names: 
        print('Not customer names found in the list.')
        return entry
    else:
        words_to_redact = cust_names
        # title = entry["title"]
        # summary = entry["summary"]
        # redacted_title = re.sub(r'\b(' + '|'.join(words_to_redact) + r')\b', '[CUSTOMER]', title)
        # redacted_summary = re.sub(r'\b(' + '|'.join(words_to_redact) + r')\b', '[CUSTOMER]', summary)
        # entry["title"] = redacted_title
        # entry["summary"] = redacted_summary
        print(f"This is the entry we are parsing {entry}")
        for k,v in entry:
            print(k,v)
            redacted = re.sub(r'\b(' + '|'.join(words_to_redact) + r')\b', '[CUSTOMER]', v)
            entry[k] = redacted
        return entry


def detect_entities(text):
    bedrock_client = boto3.client('bedrock-runtime',region_name='us-east-1')

    tools =[
        {
            "toolSpec": {
                "name": "print_entities",
                "description": "Finds all entities in a sentence or paragraph",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "entities": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string", "description": "The extracted entity name."},
                                        "item_type": {"type": "string", "enum": ["PERSON", "ORGANIZATION", "LOCATION"], "description": "Type of the entity extracted from the text"},
                                        "context": {"type": "string", "description": "The context in which the entity appears in the text."}
                                    },
                                    "required": ["name", "item_type", "context"]
                                }
                            }
                        },
                        "required": ["entities"]
                    }
                }
            }
        }
    ]

    query = f"""
    <document>
    {text}
    </document>
        
    Use the print_entities tool use.

    """
    message_mm = [
        {
            "role": "user",
            "content": [
                {
                    "text": query
                }
            ]
        }
    ]

    response = bedrock_client.converse(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        toolConfig={"tools": tools},
        messages=message_mm,
        inferenceConfig={
            "temperature": 0.2,
            "maxTokens": 2048
        },
    )

    data = response["output"]["message"]["content"]
    # use list comprehension to find the dictionary in the list that starts with 'toolUse'
    content = next((item for item in data if item.get("toolUse")), None)

    if content["toolUse"]["name"] == "print_entities":
        entities = content["toolUse"]["input"]
        
    return entities

def is_customer(name_list):
    bedrock_client = boto3.client('bedrock-runtime',region_name='us-east-1')

    customer_names = []

    for name in name_list:
        customer_name = name["name"]
        context = name["context"]

        query = f"""
        You will be given customer names as input in the <text></text> XML tags.  
        Your task is the following: 
            1. Read the information in detail. 
            2. Responde with True if this is an Amazon or AWS customer if you are not sure respond with True.
            3. Amazon and AWS are not considered customers.
            4. All Amazon and AWS services are not considered customers.
            5. Review the examples in <Example></Example> before responding.
            6. No need for a preamble.

        <Example>
            name: SEC, context:  The SEC was extracting check data manually for every investigation, each investigation could contain multiple bank account data with hundreds of thousands of checks that the SEC enforcement team needed data from, Result: TRUE, Explanation: SEC is a stock exchange in the United States.
            name: FNMA, context: I worked with FNMA on a solution to migrate 10,000 legacy applications to the cloud, Result: TRUE, Explanation: FNMA is an abbriviation of Fannie Mae who is a financial services company.
            name: Fannie Mae, context: I presented a successful re:Invent recap at Fannie Mae's Reston Center, with over 1000 attendees and a 4.71 speaker CSAT score, Result: TRUE, Explanation: Fannie Mae is a financial services company.
            name: Freddie Mac, context: I led the demo portion of the Freddie Mac executive briefing on generative AI where I showcased five ways the customer could leverage generative AI, including a text-to-SQL demo that impressed Frank Nazzaro, CIO so much that we regained trust in our knowledge and capabilities of generative AI use cases, Result: TRUE, Explanation: Freddie Mac is a financial services company.
            name: AWS, context: I worked with customer to migrate to AWS S3, Result: FALSE, Explanation: AWS is a cloud computing company.
            name: Amazon, context: I worked with the customer to move a worked to Amazon, Result: FALSE, Explanation: Amazon is a cloud computing company.
            name: Bedrock, context: I worked with the customer to move to Bedrock, Result: FALSE, Explanation: Bedrock is a cloud computing service under Amazon.
            name: Mission Solutions, context: I worked with the Mission Solutions team to build a check processings solution and implemented it for customer, Result: FALSE, Explanation: Mission Solutions is a team inside of AWS.
            name: DWA, context: I used the DWA solution for customer document processing needs, Result: FALSE, Explanation: DWA is a solution built by AWS.
            name: City of Miami Parking Authority, context: I am the go-to point of contact for IDP and DWA for the City of Miami Parking Authority, Result: TRUE, Explanation: City of Miami Parking Authority is a state and local government agency.
            name: GREF, context: I worked along side the GREF team for the re:Invent ReCap session, Result: FALSE, Explanation: GREF is an Amazon team.
            name: FedFin, context: FedFin re:Invent recap AI/ML track owner, Result: FALSE, Explanation: FedFin is an internal Amazon team.
            name: Ted Williams, context: Ted Williams, a cloud architect at ABC Company, congradulated us on a job well done, Result: TRUE, Explanation: Ted Williams works for ABC Company.
            name: Jane Smith, context: Jane Smith, SVP and CDO "Thank you AWS team. This was a great event and thank you for contributing to our culture of learning.", Result: TRUE, Explanation: Jane Smith is a company executive and this is a quote from them.
            name: Siri, context: Siri contributed to a project that automated the process of extracting financial check data mapped to bank statements to identify potential fraud schemes., Result: FALSE, Explanation: This is written in 3rd person and the persons name should not be marked True.
            name: Noah, context: Siri is partnering with Noah and Kevin Shaw in building this solution. Currently customer internally is working on path to production., Result: FALSE, Explanation: Noah works for AWS and should not be marked as true.
        </Example>


        <text>
        name: {customer_name}, context: {context}
        </text>
        """
        message_mm = [
            {
                "role": "user",
                "content": [
                    {
                        "text": query
                    }
                ]
            }
        ]
        response = bedrock_client.converse(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            messages=message_mm,
            inferenceConfig={
                "temperature": 0.2,
                "maxTokens": 2048
            },
        )

        data = response["output"]["message"]["content"][0]["text"]
        if data == "True":
            customer_names.append(customer_name)

    return customer_names

def find_entries(entry):    
    ### On save anywhere they can type whould be checked for redaction.
    entities = detect_entities(entry)
    print("entities \n", entities)
    names = return_name(entities)
    temp_names = []
    for name in names:
        temp_names.append(name["name"])
    print("Names gathered \n",temp_names)
    cust_names = is_customer(names)
    print("These are the ones I think are customers \n", cust_names)
    redacted_entry = redaction(cust_names, entry)
    print("This is the redacted entry \n", redacted_entry)

    return redacted_entry


def lambda_handler(event, context):

    print("EVENT:\n")
    print(event)

    redacted_entry = find_entries(event)

    
    return {
        'statusCode': 200,
        'body': redacted_entry,
    }
