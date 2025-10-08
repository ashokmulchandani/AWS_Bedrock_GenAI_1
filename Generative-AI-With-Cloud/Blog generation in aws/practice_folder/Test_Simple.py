import json
import boto3

def lambda_handler(event, context):
    try:
        print(f"Event received: {json.dumps(event)}")
        
        # Simple test - just return success without calling Bedrock
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Lambda is working!'})
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }