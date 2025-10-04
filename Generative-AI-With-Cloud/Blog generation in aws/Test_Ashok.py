import boto3
import botocore.config
import json
from datetime import datetime

# Function 1: Generate blog using AI
def blog_generate_using_bedrock(blogtopic: str) -> str:
    """
    This function takes a topic and asks AI to write a blog about it
    """
    
    # Step 1: Create instructions for the AI (using Llama format)
    prompt = f"""<s>[INST]Human: Write a 200 words blog on the topic {blogtopic}
    Assistant:[/INST]
    """

    # Step 2: Set up AI parameters (how the AI should behave)
    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9
    }

    try:
        # Step 3: Connect to AWS Bedrock (AI service) with timeout and retry settings
        bedrock = boto3.client(
            "bedrock-runtime",
            region_name="us-east-1",
            config=botocore.config.Config(
                read_timeout=300,
                retries={'max_attempts': 3}
            )
        )
        
        # Step 4: Send request to AI model
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId="meta.llama3-8b-instruct-v1:0"
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
        # Step 1: Get the blog topic from the request
        blogtopic = json.loads(event['body'])['blog_topic']
        print(f"Blog topic: {blogtopic}")

        # Step 2: Generate the blog using AI
        generated_blog = blog_generate_using_bedrock(blogtopic)

        # Step 3: Save the blog to cloud storage
        # Create a unique filename with timestamp
        if generated_blog:
            current_time = datetime.now().strftime('%H%M%S')
            filename = f"blog-output/{current_time}.txt"
            bucket_name = 'aws_bedrock_course1'

            save_blog_details_s3(filename, bucket_name, generated_blog)

            return {
                'statusCode': 200,
                'body': json.dumps('Blog generated and saved successfully!')
            }
        
        else:
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to generate blog')
            }
        
    except Exception as error:
        print(f"Main function error: {error}")
        return {
            'statusCode': 500,
            'body': json.dumps('Something went wrong')
        }
    
    






