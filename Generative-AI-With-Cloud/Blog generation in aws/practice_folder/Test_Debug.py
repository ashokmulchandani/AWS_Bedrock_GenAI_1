import json

def lambda_handler(event, context):
    try:
        print(f"Event received: {json.dumps(event)}")
        
        # Test 1: Check if body exists
        if 'body' not in event:
            print("ERROR: No body in event")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No body in event'})
            }
        
        print(f"Body type: {type(event['body'])}")
        print(f"Body content: {event['body']}")
        
        # Test 2: Try to parse body
        request_body = event['body']
        if isinstance(request_body, str):
            try:
                request_data = json.loads(request_body)
                print(f"Parsed JSON: {request_data}")
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'JSON parse error: {str(e)}'})
                }
        else:
            request_data = request_body
            print(f"Body is not string: {request_data}")
        
        # Test 3: Check for blog_topic
        if 'blog_topic' not in request_data:
            print("ERROR: No blog_topic in request")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No blog_topic in request'})
            }
        
        blog_topic = request_data['blog_topic']
        print(f"Blog topic found: {blog_topic}")
        
        # Test 4: Return success without calling Bedrock
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Debug test successful!',
                'topic': blog_topic,
                'event_keys': list(event.keys()),
                'body_type': str(type(event['body']))
            })
        }
        
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        import traceback
        print(f"TRACEBACK: {traceback.format_exc()}")
        
        # Return a simple error response
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'type': str(type(e))
            })
        }