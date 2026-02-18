#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.agent_stack import WeatherAgentStack

app = cdk.App()

WeatherAgentStack(
    app,
    "WeatherAgentStack",
    description="Weather service agent hosted on AgentCore Runtime"
)

app.synth()
