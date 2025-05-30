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
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    logger.info("EVENT:")
    logger.info(event)

    
    return {
        'statusCode': 200,
        'body': 'Passed checks',
    }
