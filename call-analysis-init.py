import boto3
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource(
    'dynamodb',
    region_name="ap-southeast-1"
  )
from services.analysis import callAnalysis

TABLE_CALL_ANALYSIS='call-analysis-table'
analysisTable = dynamodb.Table(TABLE_CALL_ANALYSIS)

def checkTaskStatus(call_id):
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('type').eq('CALL') &
                         boto3.dynamodb.conditions.Key('call_id').eq(call_id)
    )
    return response

def init():
    try:
        pending_call_analysis = analysisTable.query(
            KeyConditionExpression=Key('type').eq('CALL') & Key('call_id').begins_with('PENDING')
        )
        print('pending_call_analysis', pending_call_analysis)
        for call in pending_call_analysis['Items']:
            file = call['s3_file_path']
            call_id = call['call_id']
            print('call_id', call_id)
            taskStatus = checkTaskStatus(call_id)
            print('taskStatus', taskStatus)
            updated_call_id = call_id.replace("PENDING", "INPROGRESS")
            print('updated_call_id', updated_call_id)
            params = {'type': 'CALL', 'call_id': call_id}
            print('params', params)
            analysisTable.delete_item(Key=params)
            call['call_id'] = updated_call_id
            response = analysisTable.put_item(Item=call)
            callAnalysis(file, call)
    except Exception as e:
        print('Error in callAnalysis init :::', e)
        raise Exception(f"Error in callAnalysis init: {e}")

init()
