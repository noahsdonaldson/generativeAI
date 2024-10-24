from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    Duration
)
from constructs import Construct
from aws_cdk import aws_iam as _iam

class EntityRedactionStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define entity redaction lambda
        entity_redaction_lambda = _lambda.Function(
            self, "EntityRedactionLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda"),
            handler="entity-redaction.lambda_handler",
            timeout=Duration.seconds(120),
            memory_size=512
        )

        # Define the IAM policy for Bedrock 
        bedrock_policy = _iam.PolicyStatement(
            actions=["bedrock:*"],
            resources=["*"],
        )

        # Attach the policy to the Lambda function's role
        entity_redaction_lambda.role.add_to_policy(bedrock_policy)