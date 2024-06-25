import boto3
dynamodb = boto3.resource(
    'dynamodb',
    region_name="ap-southeast-1"
)
TABLE_CALL_ANALYSIS='call-analysis-table'

def getAllCalls:
  analysisTable = dynamodb.Table(TABLE_CALL_ANALYSIS)
  response = table.query(
      KeyConditionExpression=boto3.dynamodb.conditions.Key('PrimaryKey').eq('call')
  )
  # Get the items from the response
  items = response.get('Items', [])
  # Print the items
  for item in items:
      print(item)
  return items
