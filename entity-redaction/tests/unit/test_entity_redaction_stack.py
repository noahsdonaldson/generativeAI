import aws_cdk as core
import aws_cdk.assertions as assertions

from entity_redaction.entity_redaction_stack import EntityRedactionStack

# example tests. To run these tests, uncomment this file along with the example
# resource in entity_redaction/entity_redaction_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = EntityRedactionStack(app, "entity-redaction")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
