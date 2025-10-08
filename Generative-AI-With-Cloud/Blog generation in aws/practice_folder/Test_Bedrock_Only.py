import json
import boto3
import botocore.config

def lambda_handler(event, context):
    try:
        print(f"Event received: {json.dumps(event)}")
        
        # Step 1: Test Bedrock connection only
        print("Testing Bedrock connection...")
        
        bedrock = boto3.client(
            "bedrock-runtime",
            region_name="us-east-1",
            config=botocore.config.Config(
                read_timeout=300,
                retries={'max_attempts': 3}
            )
        )
        
        # Step 2: Simple Bedrock test
        prompt = "<s>[INST]Human: Say hello[/INST]"
        
        body = {
            "prompt": prompt,
            "max_gen_len": 100,
            "temperature": 0.5,
            "top_p": 0.9
        }
        
        print("Calling Bedrock...")
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId="meta.llama3-8b-instruct-v1:0"
        )
        
        print("Bedrock responded successfully!")
        response_body = json.loads(response.get('body').read())
        generation = response_body.get('generation', 'No generation found')
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Bedrock test successful!',
                'response': generation[:100]
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Bedrock test failed',
                'details': str(e)
            })
        }