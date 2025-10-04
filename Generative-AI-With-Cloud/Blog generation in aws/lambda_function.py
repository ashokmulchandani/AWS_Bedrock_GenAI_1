import json
import boto3

def lambda_handler(event, context):
    # Initialize Bedrock client
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # Get blog topic from event
    blog_topic = event.get('blog_topic', 'AI and Machine Learning')
    
    # Create prompt for blog generation
    prompt = f"Write a comprehensive blog post about {blog_topic}. Include an introduction, main content with key points, and a conclusion."
    
    # Prepare request body for Claude model
    body = json.dumps({
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "max_tokens_to_sample": 1000,
        "temperature": 0.7,
        "top_p": 0.9
    })
    
    try:
        # Invoke Bedrock model
        response = bedrock.invoke_model(
            body=body,
            modelId='anthropic.claude-v2',
            accept='application/json',
            contentType='application/json'
        )
        
        # Parse response
        response_body = json.loads(response.get('body').read())
        blog_content = response_body.get('completion', '')
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'blog_topic': blog_topic,
                'blog_content': blog_content
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }