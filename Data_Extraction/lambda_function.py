import json

def lambda_handler(event, context):
    # TODO implement
    print("Hello")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello!')
    }
