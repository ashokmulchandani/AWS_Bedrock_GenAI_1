import boto3
import json
from datetime import datetime

# Function 1: Generate blog using AI
def blog_generate_using_bedrock(blogtopic: str) -> str:
    """
    This function takes a topic and asks AI to write a blog about it
    """
    
    # Step 1: Create instructions for the AI (using Llama format)
    prompt = f"Write a comprehensive blog post about {blogtopic}. Include an introduction, main points, and conclusion."

    # Step 2: Set up AI parameters (how the AI should behave)
    body = {
        "prompt": prompt,
        "max_gen_len": 1000,
        "temperature": 0.7,
        "top_p": 0.9
    }

    try:
        # Step 3: Connect to AWS Bedrock (AI service) with timeout settings
        bedrock = boto3.client(
            "bedrock-runtime",
            region_name="us-east-1",
            config=boto3.session.Config(
                read_timeout=60,
                connect_timeout=10
            )
        )
        
        # Step 4: Send request to AI model
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId="meta.llama3-8b-instruct-v1:0",
            accept='application/json',
            contentType='application/json'
        )

        # Step 5: Get the AI's response
        response_body = json.loads(response.get('body').read())

        # Step 6: Extract the blog text from response
        generation = response_body['generation']
        print("Blog generated successfully!")
        return generation

    except Exception as error:
        print(f"Error occurred: {error}")
        return ("Sorry, couldn't generate blog")

# Function 2: Save blog to cloud storage
def save_blog_details_s3(s3_key: str, s3_bucket: str, generate_blog: str) -> None:
    """
    This function saves the blog to AWS S3 (cloud storage)
    Input: s3_key, s3_bucket, generate_blog
    """
    try:
        # Connect to AWS S3 (cloud storage)
        print("Connecting to cloud storage...")
        s3_client = boto3.client('s3')
        
        # Upload the blog to cloud
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=generate_blog
        )
        
        print(f"Blog saved to cloud as: {s3_key}")

    except Exception as error:
        print(f"Error saving to cloud: {error}")

# Function 3: Main function (orchestrates everything)
def lambda_handler(event, context):
    """
    This is the main function that runs when Lambda is triggered
    It coordinates all the steps: get topic -> generate blog -> save to cloud
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Step 1: Get the blog topic from the request (FIXED REQUEST PARSING)
        if 'body' in event:
            # API Gateway format - parse the body
            request_data = json.loads(event['body'])
        else:
            # Direct test format - use event directly
            request_data = event
            
        if 'blog_topic' not in request_data:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing blog_topic in request')
            }
            
        blogtopic = request_data['blog_topic']
        print(f"Blog topic received: {blogtopic}")

        # Step 2: Generate the blog using AI
        generated_blog = blog_generate_using_bedrock(blogtopic)
        print(f"Blog generated successfully for topic: {blogtopic}")
        print(f"Blog content length: {len(generated_blog)} characters")
        print(f"Blog content: {generated_blog}")

        # Step 3: Check if blog was generated successfully
        if generated_blog and generated_blog != "Sorry, couldn't generate blog":
            # Create a unique filename with timestamp
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
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps(f'Invalid JSON in request body: {str(e)}')
        }
    except Exception as error:
        print(f"Main function error: {error}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
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