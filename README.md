# Weather Agent for AgentCore Runtime

AWS CDK Python application for deploying a weather service agent to Amazon Bedrock AgentCore Runtime using the Strands SDK.

## Overview

This project demonstrates how to build and deploy an AI agent to AWS AgentCore Runtime using AWS CDK and the Strands Agents SDK. The weather agent uses Claude 4.5 Sonnet and provides weather information through both conversational prompts and structured API calls.

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
├── requirements.txt            # Python dependencies (CDK + boto3 + python-dotenv)
├── .env                        # Environment configuration (gitignored)
├── .env.example                # Example environment configuration
├── stacks/
│   └── agent_stack.py         # CDK stack definition
├── agent/
│   ├── Dockerfile             # Container definition
│   ├── requirements.txt       # Agent dependencies (strands-agents, bedrock-agentcore)
│   └── weather_agent.py       # Weather agent implementation using Strands SDK
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

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your AWS account details
```

4. Bootstrap CDK (first time only):
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
- IAM execution role with Bedrock and CloudWatch permissions
- AgentCore Runtime configuration

### 2. Build and Push Docker Image

Using Finch:
```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | finch login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com

# Build and push
finch build -t weather-agent ./agent
finch tag weather-agent:latest ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/weather-agent:v2.1.1
finch push ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/weather-agent:v2.1.1
```

Using Docker:
```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com

# Build and push
docker build -t weather-agent ./agent
docker tag weather-agent:latest ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/weather-agent:v2.1.1
docker push ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/weather-agent:v2.1.1
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

# Weather query
payload = json.dumps({
    "action": "get_weather",
    "parameters": {
        "location": "Seattle"
    }
})

# Or conversational prompt
# payload = json.dumps({"prompt": "What's the weather like in Seattle?"})

response = client.invoke_agent_runtime(
    agentRuntimeArn='arn:aws:bedrock-agentcore:us-west-2:ACCOUNT_ID:runtime/RUNTIME_ID',
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
4. Test with structured input:
```json
{
  "action": "get_weather",
  "parameters": {
    "location": "Seattle"
  }
}
```

Or conversational input:
```json
{
  "prompt": "What's the weather in Tokyo?"
}
```

## Architecture

### Strands SDK Integration

The agent uses the Strands Agents SDK with:
- `@tool` decorator for defining the weather tool
- `BedrockAgentCoreApp` for AgentCore Runtime integration
- `BedrockModel` configured with Claude 4.5 Sonnet
- Automatic tool discovery and invocation

### Agent Endpoints

The agent exposes:
- `GET /ping` - Health check (required by AgentCore)
- `POST /invocations` - Main AgentCore Runtime entry point

### Model Configuration

The agent uses Claude 4.5 Sonnet via the inference profile:
- Model ID: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- Configured in `agent/weather_agent.py`

## Configuration

### Environment Variables

Runtime environment variables (configured in `stacks/agent_stack.py`):
- `PORT`: Server port (default: 8080)
- `WEATHER_API_KEY`: API key for weather service (demo value)

Test script configuration (`.env` file):
- `AWS_ACCOUNT_ID`: Your AWS account ID
- `AWS_REGION`: AWS region (default: us-west-2)
- `RUNTIME_ID`: AgentCore Runtime ID

### IAM Permissions

The execution role includes:
- CloudWatch Logs permissions
- Bedrock model invocation permissions (InvokeModel, InvokeModelWithResponseStream)
- Secrets Manager access (for tagged resources)
- Trust policy for bedrock-agentcore service

## Customization

### Integrating a Real Weather API

1. Update the `get_weather` function in `agent/weather_agent.py`
2. Add API credentials to environment variables or Secrets Manager
3. Rebuild and redeploy

### Changing the Model

Update the model configuration in `agent/weather_agent.py`:
```python
from strands.models import BedrockModel

model = BedrockModel(model_id="anthropic.claude-3-5-sonnet-20241022-v2:0")
agent = Agent(name="WeatherAgent", model=model, tools=[get_weather])
```

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
- **Runtime not updating**: Use versioned image tags (v2.1.1, v2.1.2, etc.) instead of `latest`
- **Permission errors**: Verify IAM role includes Bedrock invocation permissions
- **Model access errors**: Ensure the model is enabled in your AWS account

## Resources

- [AgentCore Runtime Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [Strands Agents Documentation](https://strandsagents.com/latest/documentation/)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
