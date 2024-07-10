import boto3
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource(
    'dynamodb',
    region_name="ap-southeast-1"
  )
from services.analysis import callAnalysis

TABLE_CALL_ANALYSIS='call-analysis-table'

def init():
    analysisTable = dynamodb.Table(TABLE_CALL_ANALYSIS)
    pending_call_analysis = analysisTable.query(
       KeyConditionExpression=Key('type').eq('CALL') & Key('call_id').begins_with('PENDING')
    )
    print('pending_call_analysis', pending_call_analysis)
    for call in pending_call_analysis['Items']:
        body= {
            "files": [
                call['s3_file_path']
            ]
        }
        call_id = call['call_id']
        updated_call_id = call_id.replace("PENDING", "INPROGRESS")
        response = analysisTable.update_item(
            Key={
                'type': 'CALL',
                'call_id': call['call_id']
            },
            UpdateExpression="set call_id = :new_call_id",
            ExpressionAttributeValues={
                ':new_call_id': updated_call_id
            },
            ConditionExpression="attribute_exists(type) AND attribute_exists(call_id)",
            ReturnValues="UPDATED_NEW"
        )
        callAnalysis(body, call_id)

init()
