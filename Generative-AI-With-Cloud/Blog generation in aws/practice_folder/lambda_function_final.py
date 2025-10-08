import json
import boto3

def lambda_handler(event, context):
    try:
        # Handle direct test vs API Gateway
        if 'body' in event:
            # API Gateway format
            request_body = event['body']
            if isinstance(request_body, str):
                request_data = json.loads(request_body)
            else:
                request_data = request_body
        else:
            # Direct Lambda test - event IS the data
            request_data = event
        
        blog_topic = request_data['blog_topic']
        
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Create prompt
        prompt = f"Write a comprehensive blog post about {blog_topic}. Include an introduction, main points, and conclusion."
        
        # Prepare request for Llama model
        body = json.dumps({
            "prompt": prompt,
            "max_gen_len": 1000,
            "temperature": 0.7,
            "top_p": 0.9
        })
        
        # Call Bedrock
        response = bedrock.invoke_model(
            body=body,
            modelId='meta.llama3-8b-instruct-v1:0',
            accept='application/json',
            contentType='application/json'
        )
        
        # Parse response
        response_body = json.loads(response.get('body').read())
        blog_content = response_body['generation']
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'blog_topic': blog_topic,
                'blog_content': blog_content
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }