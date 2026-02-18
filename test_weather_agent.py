#!/usr/bin/env python3
"""
Test script for Weather Agent in AgentCore Runtime
Usage: python3 test_weather_agent.py [location]
"""
import boto3
import json
import sys
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Runtime configuration from environment
RUNTIME_ID = os.getenv("RUNTIME_ID")
ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")
REGION = os.getenv("AWS_REGION", "us-west-2")
RUNTIME_ARN = f"arn:aws:bedrock-agentcore:{REGION}:{ACCOUNT_ID}:runtime/{RUNTIME_ID}"

def invoke_weather_agent(location):
    """Invoke the weather agent with a location"""
    client = boto3.client('bedrock-agentcore', region_name=REGION)
    
    request_payload = {
        "action": "get_weather",
        "parameters": {
            "location": location
        }
    }
    
    session_id = f"test-session-{uuid.uuid4()}"
    
    print(f"Invoking weather agent for: {location}")
    print(f"Request: {json.dumps(request_payload, indent=2)}")
    print("-" * 60)
    
    response = client.invoke_agent_runtime(
        agentRuntimeArn=RUNTIME_ARN,
        runtimeSessionId=session_id,
        payload=json.dumps(request_payload),
        qualifier="DEFAULT"
    )
    
    response_body = response['response'].read()
    response_data = json.loads(response_body)
    
    print("Success!")
    print(f"Response: {json.dumps(response_data, indent=2)}")
    return response_data

if __name__ == "__main__":
    location = sys.argv[1] if len(sys.argv) > 1 else "Seattle"
    
    try:
        result = invoke_weather_agent(location)
        
        print("\n" + "="*60)
        print(f"Weather in {result.get('location')}:")
        print(f"  Temperature: {result.get('temperature')}")
        print(f"  Condition: {result.get('condition')}")
        print(f"  Humidity: {result.get('humidity')}")
        print("="*60)
        
    except Exception as e:
        print(f"\nFailed to invoke agent: {e}")
        sys.exit(1)
