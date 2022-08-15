import json
import boto3

def lambda_handler(event, context):
    client = boto3.client('cloudformation')
    allstacks = client.list_stacks(
        StackStatusFilter=[
            'CREATE_IN_PROGRESS','CREATE_FAILED','CREATE_COMPLETE','ROLLBACK_IN_PROGRESS','ROLLBACK_FAILED','ROLLBACK_COMPLETE','DELETE_IN_PROGRESS','DELETE_FAILED','UPDATE_IN_PROGRESS','UPDATE_COMPLETE_CLEANUP_IN_PROGRESS','UPDATE_COMPLETE','UPDATE_FAILED','UPDATE_ROLLBACK_IN_PROGRESS','UPDATE_ROLLBACK_FAILED','UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS','UPDATE_ROLLBACK_COMPLETE','REVIEW_IN_PROGRESS','IMPORT_IN_PROGRESS','IMPORT_COMPLETE','IMPORT_ROLLBACK_IN_PROGRESS','IMPORT_ROLLBACK_FAILED','IMPORT_ROLLBACK_COMPLETE'
        ]
    )
    for stack in allstacks['StackSummaries']:
        client.detect_stack_drift(
            StackName=stack['StackName']
        )

