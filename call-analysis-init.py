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
    response = analysisTable.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('type').eq('CALL') &
                         boto3.dynamodb.conditions.Key('call_id').eq(call_id)
    )
    if response and len(response.Items) > 0:
        return True
    else:
        return False

def init():
    print('*************** CALL ANALYSIS INIT ***************')
    try:
        pending_call_analysis = analysisTable.query(
            KeyConditionExpression=Key('type').eq('CALL') & Key('call_id').begins_with('PENDING')
        )
        print('*************** Pending Calls START ***************')
        print(pending_call_analysis)
        print('*************** Pending Calls END***************')
        for call in pending_call_analysis['Items']:
            file = call['s3_file_path']
            call_id = call['call_id']
            print('*************** Started Process for Call_id :::', call_id)
            taskStatus = checkTaskStatus(call_id)
            print('*************** taskStatus :::', taskStatus)
            if(taskStatus):
                updated_call_id = call_id.replace("PENDING", "INPROGRESS")
                print('*************** updated_call_id :::', updated_call_id)
                params = {'type': 'CALL', 'call_id': call_id}
                analysisTable.delete_item(Key=params)
                call['call_id'] = updated_call_id
                response = analysisTable.put_item(Item=call)
                print('*************** Making Call to CallAnalysis with File and Call data ***************')
                callAnalysis(file, call)
    except Exception as e:
        print('Error in callAnalysis init :::', e)
        raise Exception(f"Error in callAnalysis init: {e}")

init()
