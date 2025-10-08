import boto3
import json
from datetime import datetime

def blog_generate_using_bedrock(blogtopic: str) -> str:
    """Generate blog using AI"""
    prompt = f"Write a clear and engaging 200-word blog post about {blogtopic}. Use simple language and avoid any markup or special formatting."
    
    body = {
        "prompt": prompt,
        "max_gen_len": 1000,
        "temperature": 0.7,
        "top_p": 0.9
    }

    try:
        bedrock = boto3.client(
            "bedrock-runtime",
            region_name="us-east-1",
            config=boto3.session.Config(
                read_timeout=60,
                connect_timeout=10
            )
        )
        
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId="meta.llama3-8b-instruct-v1:0",
            accept='application/json',
            contentType='application/json'
        )

        response_body = json.loads(response.get('body').read())
        generation = response_body['generation']
        print("Blog generated successfully!")
        return generation

    except Exception as error:
        print(f"Error occurred: {error}")
        return "Sorry, couldn't generate blog"

def save_blog_details_s3(s3_key: str, s3_bucket: str, generate_blog: str) -> None:
    """Save blog to S3"""
    try:
        print("Connecting to cloud storage...")
        s3_client = boto3.client('s3')
        
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=generate_blog
        )
        
        print(f"Blog saved to cloud as: {s3_key}")

    except Exception as error:
        print(f"Error saving to cloud: {error}")

def lambda_handler(event, context):
    """Main Lambda function"""
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Parse request - same logic as lambda_simple_clean.py
        if 'body' in event:
            request_data = json.loads(event['body'])
        else:
            request_data = event
            
        if 'blog_topic' not in request_data:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing blog_topic in request')
            }
            
        blogtopic = request_data['blog_topic']
        print(f"Blog topic received: {blogtopic}")

        # Generate blog
        generated_blog = blog_generate_using_bedrock(blogtopic)
        print(f"Blog generated successfully for topic: {blogtopic}")
        print(f"Blog content length: {len(generated_blog)} characters")
        print(f"Blog content: {generated_blog}")

        # Check if successful
        if generated_blog and generated_blog != "Sorry, couldn't generate blog":
            # Save to S3
            current_time = datetime.now().strftime('%H%M%S')
            filename = f"blog-output/{current_time}.txt"
            bucket_name = 'awsbedrockcoursebucket1'

            save_blog_details_s3(filename, bucket_name, generated_blog)

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Blog generated and saved successfully!',
                    'filename': filename,
                    'blog_topic': blogtopic,
                    'blog_content': generated_blog
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Failed to generate blog',
                    'details': generated_blog
                })
            }
        
    except Exception as error:
        print(f"Main function error: {error}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(error)
            })
        }