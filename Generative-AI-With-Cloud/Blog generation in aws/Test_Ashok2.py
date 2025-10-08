# Import required libraries
import boto3  # AWS SDK for Python
import botocore.config  # For AWS client configuration
import json   # For handling JSON data
from datetime import datetime  # For timestamps

# Function 1: Generate blog using AI
def generate_blog_with_ai(topic):
    """
    This function takes a topic and asks AI to write a blog about it
    Input: topic (string) - what you want the blog to be about
    Output: blog_text (string) - the AI-generated blog
    """
    
    # Step 1: Create instructions for the AI (using Llama format)
    ai_instructions = f"<s>[INST]Human: Write a 200 words blog on the topic {topic}[/INST]"
    
    # Step 2: Set up AI parameters (how the AI should behave)
    ai_settings = {
        "prompt": ai_instructions,      # What to ask the AI
        "max_gen_len": 512,            # Maximum tokens AI can generate
        "temperature": 0.5,            # Creativity level (0-1, higher = more creative)
        "top_p": 0.9                   # Word variety (0-1, higher = more variety)
    }
    
    try:
        # Step 3: Connect to AWS Bedrock (AI service) with timeout and retry settings
        print("Connecting to AWS AI service...")
        ai_client = boto3.client(
            "bedrock-runtime", 
            region_name="us-east-1",
            config=botocore.config.Config(
                read_timeout=300,  # Wait up to 5 minutes for response
                retries={'max_attempts': 3}  # Try 3 times if it fails
            )
        )
        
        # Step 4: Send request to AI model
        print("Asking AI to write the blog...")
        ai_response = ai_client.invoke_model(
            body=json.dumps(ai_settings),
            modelId="meta.llama3-8b-instruct-v1:0"
        )
        
        # Step 5: Get the AI's response
        raw_response = ai_response.get('body').read()
        response_data = json.loads(raw_response)
        
        # Step 6: Extract the blog text from response
        blog_text = response_data['generation']
        print("Blog generated successfully!")
        return blog_text
        
    except Exception as error:
        print(f"Error occurred: {error}")
        return "Sorry, couldn't generate blog"

# Function 2: Save blog to cloud storage
def save_blog_to_cloud(filename, bucket_name, blog_content):
    """
    This function saves the blog to AWS S3 (cloud storage)
    Input: filename, bucket_name, blog_content
    """
    
    try:
        # Connect to AWS S3 (cloud storage)
        print("Connecting to cloud storage...")
        s3_client = boto3.client('s3')
        
        # Upload the blog to cloud
        s3_client.put_object(
            Bucket=bucket_name, 
            Key=filename, 
            Body=blog_content
        )
        print(f"Blog saved to cloud as: {filename}")
        
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
        
        # Step 1: Validate request
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing request body'})
            }
        
        # Parse request body
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
        print(f"Received request to write blog about: {blog_topic}")
        
        # Step 2: Generate the blog using AI
        generated_blog = generate_blog_with_ai(blog_topic)
        
        # Step 3: If blog was generated successfully, save it
        if generated_blog and generated_blog != "Sorry, couldn't generate blog":
            
            # Create a unique filename with timestamp
            current_time = datetime.now().strftime('%H%M%S')
            filename = f"blog-output/{current_time}.txt"
            bucket_name = 'awsbedrockcoursebucket1'
            
            # Save to cloud storage
            save_blog_to_cloud(filename, bucket_name, generated_blog)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Blog generated and saved successfully!',
                    'filename': filename,
                    'preview': generated_blog[:200] + '...' if len(generated_blog) > 200 else generated_blog
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Failed to generate blog',
                    'details': generated_blog
                })
            }
            
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Invalid JSON: {str(e)}'})
        }
    except Exception as error:
        print(f"Main function error: {error}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(error)
            })
        }

# Test the function (uncomment to test locally)
# if __name__ == "__main__":
#     test_event = {
#         'body': '{"blog_topic": "Artificial Intelligence"}'
#     }
#     result = lambda_handler(test_event, None)
#     print(result)