import json
import boto3

def lambda_handler(event, context):
    try:
        # Parse request
        if 'body' in event:
            request_data = json.loads(event['body'])
        else:
            request_data = event
        
        blog_topic = request_data['blog_topic']
        print(f"Blog topic received: {blog_topic}")
        
        # Initialize Bedrock client with timeout settings
        bedrock = boto3.client(
            'bedrock-runtime', 
            region_name='us-east-1',
            config=boto3.session.Config(
                read_timeout=60,
                connect_timeout=10
            )
        )
        
        # Create shorter prompt for faster response
        prompt = f"Write a brief blog post about {blog_topic}."
        
        # Prepare request with smaller token limit
        body = json.dumps({
            "prompt": prompt,
            "max_gen_len": 300,
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
        print(f"Blog generated successfully for topic: {blog_topic}")
        print(f"Blog content length: {len(blog_content)} characters")
        print(f"Blog content: {blog_content}")
        
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