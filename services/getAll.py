import boto3
dynamodb = boto3.resource(
    'dynamodb',
    region_name="ap-southeast-1"
)
TABLE_CALL_ANALYSIS='call-analysis-table'

def getAllCalls(data):
  try:
    analysisTable = dynamodb.Table(TABLE_CALL_ANALYSIS)
    response = analysisTable.query(
      KeyConditionExpression=boto3.dynamodb.conditions.Key('type').eq('call')
    )
    # Get the items from the response
    items = response.get('Items', [])
    print('items ' ,items )
    return items
  except ClientError as e:
    print('Error in getAllCalls :::', e)
    raise Exception(f"Error in getAllCalls: {e}")
