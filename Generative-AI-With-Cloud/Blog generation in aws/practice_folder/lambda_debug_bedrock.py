import json
import boto3

def lambda_handler(event, context):
    try:
        # Step 1: Parse request
        if 'body' in event:
            request_data = json.loads(event['body'])
        else:
            request_data = event
        
        blog_topic = request_data['blog_topic']
        print(f"Topic: {blog_topic}")
        
        # Step 2: Test Bedrock connection
        try:
            bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
            print("Bedrock client created successfully")
        except Exception as e:
            print(f"Bedrock client error: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Bedrock client error: {str(e)}'})
            }
        
        # Step 3: Test model invocation
        try:
            prompt = f"Write a short blog about {blog_topic}"
            
            body = json.dumps({
                "prompt": prompt,
                "max_gen_len": 500,
                "temperature": 0.7,
                "top_p": 0.9
            })
            
            print(f"Calling model with prompt: {prompt}")
            
            response = bedrock.invoke_model(
                body=body,
                modelId='meta.llama3-8b-instruct-v1:0',
                accept='application/json',
                contentType='application/json'
            )
            
            print("Model invoked successfully")
            
            # Step 4: Parse response
            response_body = json.loads(response.get('body').read())
            print(f"Response keys: {list(response_body.keys())}")
            
            blog_content = response_body.get('generation', 'No generation field found')
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'blog_topic': blog_topic,
                    'blog_content': blog_content,
                    'response_keys': list(response_body.keys())
                })
            }
            
        except Exception as e:
            print(f"Model invocation error: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Model error: {str(e)}'})
            }
            
    except Exception as e:
        print(f"General error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }