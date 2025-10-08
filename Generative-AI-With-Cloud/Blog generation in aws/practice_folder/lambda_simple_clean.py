import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    try:
        if 'body' in event:
            request_data = json.loads(event['body'])
        else:
            request_data = event
        
        blog_topic = request_data['blog_topic']
        print(f"Blog topic received: {blog_topic}")
        
        bedrock = boto3.client(
            'bedrock-runtime', 
            region_name='us-east-1',
            config=boto3.session.Config(
                read_timeout=60,
                connect_timeout=10
            )
        )
        
        prompt = f"Write a comprehensive blog post about {blog_topic}."
        
        body = json.dumps({
            "prompt": prompt,
            "max_gen_len": 1000,
            "temperature": 0.7,
            "top_p": 0.9
        })
        
        response = bedrock.invoke_model(
            body=body,
            modelId='meta.llama3-8b-instruct-v1:0',
            accept='application/json',
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        blog_content = response_body['generation']
        print(f"Blog generated successfully for topic: {blog_topic}")
        print(f"Blog content: {blog_content}")
        
        # Save to S3
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
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Blog generated and saved successfully!',
                    'blog_topic': blog_topic,
                    'blog_content': blog_content,
                    'filename': filename
                })
            }
            
        except Exception as s3_error:
            print(f"S3 error: {s3_error}")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Blog generated but S3 save failed',
                    'blog_topic': blog_topic,
                    'blog_content': blog_content,
                    's3_error': str(s3_error)
                })
            }
        
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }