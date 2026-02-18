import boto3
import json
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

RUNTIME_ID = os.getenv("RUNTIME_ID")
ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")
REGION = os.getenv("AWS_REGION", "us-west-2")
RUNTIME_ARN = f"arn:aws:bedrock-agentcore:{REGION}:{ACCOUNT_ID}:runtime/{RUNTIME_ID}"

client = boto3.client('bedrock-agentcore', region_name=REGION)

payload = json.dumps({"prompt": "Hello! How are you today?"})

print("Sending greeting to weather agent...")
print(f"Input: {payload}")
print("-" * 60)

response = client.invoke_agent_runtime(
    agentRuntimeArn=RUNTIME_ARN,
    runtimeSessionId=f'greeting-{uuid.uuid4()}',
    payload=payload,
    qualifier="DEFAULT"
)

response_body = response['response'].read()
result = json.loads(response_body)

print("Response:")
print(json.dumps(result, indent=2))
