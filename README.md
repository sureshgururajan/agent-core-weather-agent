# Weather Agent for AgentCore Runtime

AWS CDK Python application for deploying a weather service agent to Amazon Bedrock AgentCore Runtime.

## Overview

This project demonstrates how to build and deploy a containerized agent to AWS AgentCore Runtime using AWS CDK. The weather agent provides a simple REST API for retrieving weather information.

## Prerequisites

- Python 3.11+
- AWS CDK CLI
- Docker or Finch
- AWS CLI configured with appropriate credentials

## Project Structure

```
.
├── app.py                      # CDK app entry point
├── cdk.json                    # CDK configuration
├── requirements.txt            # Python dependencies (CDK + boto3)
├── stacks/
│   └── agent_stack.py         # CDK stack definition
├── agent/
│   ├── Dockerfile             # Container definition
│   ├── requirements.txt       # Agent dependencies (Flask)
│   └── weather_agent.py       # Weather service implementation
└── test_weather_agent.py      # Test script for invoking the agent
```

## Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Bootstrap CDK (first time only):
```bash
cdk bootstrap aws://ACCOUNT_ID/us-west-2
```

## Deployment

### 1. Deploy the CDK Stack

```bash
source .venv/bin/activate
export AWS_DEFAULT_REGION=us-west-2
cdk deploy
```

This creates:
- ECR repository for the Docker image
- IAM execution role with necessary permissions
- AgentCore Runtime configuration

### 2. Build and Push Docker Image

Using Finch:
```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | finch login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com

# Build and push
finch build -t weather-agent ./agent
finch tag weather-agent:latest ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/weather-agent:v1.0.3
finch push ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/weather-agent:v1.0.3
```

Using Docker:
```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com

# Build and push
docker build -t weather-agent ./agent
docker tag weather-agent:latest ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/weather-agent:v1.0.3
docker push ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/weather-agent:v1.0.3
```

### 3. Update CDK Stack with New Image Version

After pushing a new image version, update the version in `stacks/agent_stack.py` and redeploy:
```bash
cdk deploy
```

## Testing

### Using Python SDK

```bash
python3 test_weather_agent.py Chennai
```

Or programmatically:

```python
import boto3
import json
import uuid

client = boto3.client('bedrock-agentcore', region_name='us-west-2')

payload = json.dumps({
    "action": "get_weather",
    "parameters": {
        "location": "Seattle"
    }
})

response = client.invoke_agent_runtime(
    agentRuntimeArn='arn:aws:bedrock-agentcore:us-west-2:ACCOUNT_ID:runtime/weather_agent_runtime-RUNTIME_ID',
    runtimeSessionId=f'session-{uuid.uuid4()}',
    payload=payload,
    qualifier="DEFAULT"
)

response_body = response['response'].read()
result = json.loads(response_body)
print(result)
```

### Using AWS Console

1. Navigate to Amazon Bedrock AgentCore in the AWS Console
2. Select your runtime: `weather_agent_runtime`
3. Choose the DEFAULT endpoint
4. Test with input:
```json
{
  "action": "get_weather",
  "parameters": {
    "location": "Seattle"
  }
}
```

## Agent Endpoints

The weather agent exposes the following endpoints:

- `GET /ping` - Health check (required by AgentCore)
- `GET /health` - Health check
- `POST /invocations` - Main AgentCore Runtime entry point
- `POST /invoke` - Alternative invocation endpoint
- `POST /weather` - Direct weather query endpoint

## Configuration

### Environment Variables

Configure in `stacks/agent_stack.py`:
- `PORT`: Server port (default: 8080)
- `WEATHER_API_KEY`: API key for weather service (optional)

### IAM Permissions

The execution role includes:
- CloudWatch Logs permissions
- Secrets Manager access (for tagged resources)
- Trust policy for bedrock-agentcore service

## Customization

To integrate with a real weather API:

1. Update `agent/weather_agent.py` to call your weather service
2. Add API credentials to AWS Secrets Manager
3. Tag the secret with `Agent=WeatherAgent`
4. Rebuild and redeploy

## Useful Commands

- `cdk ls` - List all stacks
- `cdk synth` - Synthesize CloudFormation template
- `cdk deploy` - Deploy stack
- `cdk diff` - Compare deployed stack with current state
- `cdk destroy` - Remove stack

## Troubleshooting

### Check Runtime Logs

```bash
aws logs tail /aws/bedrock-agentcore/runtimes/weather_agent_runtime-RUNTIME_ID-DEFAULT --region us-west-2 --follow
```

### Verify Runtime Status

Check the AWS Console under Amazon Bedrock > AgentCore > Runtimes

### Common Issues

- **Health checks failing**: Ensure `/ping` endpoint returns 200 OK
- **Runtime not updating**: Use versioned image tags instead of `latest`
- **Permission errors**: Verify IAM role trust policy includes `bedrock-agentcore.amazonaws.com`

## Resources

- [AgentCore Runtime Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
