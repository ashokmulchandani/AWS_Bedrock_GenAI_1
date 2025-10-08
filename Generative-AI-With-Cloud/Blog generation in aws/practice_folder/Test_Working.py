import json
import boto3
import botocore.config
from datetime import datetime

def lambda_handler(event, context):
    try:
        print(f"Event received: {json.dumps(event)}")
        
        # Step 1: Parse request body
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing request body'})
            }
        
        request_body = event['body']
        if isinstance(request_body, str):
            request_data = json.loads(request_body)
        else:
            request_data = request_body
            
        if 'blog_topic' not in request_data:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing blog_topic in request'})
            }
            
        blog_topic = request_data['blog_topic']
        print(f"Blog topic: {blog_topic}")
        
        # Step 2: Connect to Bedrock
        bedrock = boto3.client(
            "bedrock-runtime",
            region_name="us-east-1",
            config=botocore.config.Config(
                read_timeout=300,
                retries={'max_attempts': 3}
            )
        )
        
        # Step 3: Create prompt and call Bedrock
        prompt = f"<s>[INST]Human: Write a 200 words blog on the topic {blog_topic}[/INST]"
        
        body = {
            "prompt": prompt,
            "max_gen_len": 512,
            "temperature": 0.5,
            "top_p": 0.9
        }
        
        print("Calling Bedrock for blog generation...")
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId="meta.llama3-8b-instruct-v1:0"
        )
        
        response_body = json.loads(response.get('body').read())
        blog_content = response_body.get('generation', '')
        
        print("Blog generated successfully!")
        
        # Step 4: Save to S3 (optional - skip if S3 causes issues)
        try:
            s3_client = boto3.client('s3')
            current_time = datetime.now().strftime('%H%M%S')
            filename = f"blog-output/{current_time}.txt"
            bucket_name = 'awsbedrockcoursebucket1'
            
            s3_client.put_object(
                Bucket=bucket_name,
                Key=filename,
                Body=blog_content
            )
            print(f"Blog saved to S3: {filename}")
            s3_message = f"Saved to S3: {filename}"
        except Exception as s3_error:
            print(f"S3 error (continuing anyway): {s3_error}")
            s3_message = "S3 save failed, but blog generated successfully"
        
        # Step 5: Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Blog generated successfully!',
                'topic': blog_topic,
                'blog_content': blog_content,
                's3_status': s3_message
            })
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Invalid JSON: {str(e)}'})
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }