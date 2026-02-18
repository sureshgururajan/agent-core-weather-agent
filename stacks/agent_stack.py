from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_ecr as ecr,
    CfnOutput,
)
from aws_cdk.aws_bedrock_agentcore_alpha import (
    Runtime,
    AgentRuntimeArtifact,
    RuntimeNetworkConfiguration,
)
from constructs import Construct

class WeatherAgentStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECR repository for the agent Docker image
        agent_repository = ecr.Repository(
            self,
            "WeatherAgentRepository",
            repository_name="weather-agent",
            image_scan_on_push=True,
        )

        # IAM role for AgentCore Runtime
        agent_execution_role = iam.Role(
            self,
            "WeatherAgentExecutionRole",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("bedrock.amazonaws.com"),
                iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
            ),
            description="Execution role for weather agent in AgentCore Runtime",
        )

        # Add permissions for the agent to access necessary services
        agent_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                resources=["*"],
            )
        )

        # Add any additional permissions your weather service needs
        # Example: if calling external APIs or accessing other AWS services
        agent_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "secretsmanager:GetSecretValue",
                ],
                resources=["*"],
                conditions={
                    "StringEquals": {
                        "secretsmanager:ResourceTag/Agent": "WeatherAgent"
                    }
                }
            )
        )

        # Outputs
        CfnOutput(
            self,
            "RepositoryUri",
            value=agent_repository.repository_uri,
            description="ECR repository URI for the weather agent image",
        )

        CfnOutput(
            self,
            "ExecutionRoleArn",
            value=agent_execution_role.role_arn,
            description="IAM role ARN for AgentCore Runtime execution",
        )

        CfnOutput(
            self,
            "RepositoryName",
            value=agent_repository.repository_name,
            description="ECR repository name",
        )

        # Create AgentCore Runtime
        agent_runtime_artifact = AgentRuntimeArtifact.from_ecr_repository(
            agent_repository,
            "v1.0.4"
        )

        runtime = Runtime(
            self,
            "WeatherAgentRuntime",
            runtime_name="weather_agent_runtime",
            agent_runtime_artifact=agent_runtime_artifact,
            execution_role=agent_execution_role,
            network_configuration=RuntimeNetworkConfiguration.using_public_network(),
            description="Weather service agent runtime",
            environment_variables={
                "PORT": "8080",
                "WEATHER_API_KEY": "demo-api-key-12345",
            }
        )
