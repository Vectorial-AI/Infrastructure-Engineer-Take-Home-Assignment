from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_ec2 as ec2,
    aws_iam as iam,
    Duration,
)
from constructs import Construct
import os
from pathlib import Path
import subprocess

class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, database_stack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get project root directory and API source directory
        this_dir = Path(__file__).parent.parent.parent
        api_dir = os.path.join(this_dir, "src", "api")
        
        # TODO: Consider moving build script path to configuration
        subprocess.run([
            "powershell", 
            "-ExecutionPolicy", "Bypass",
            "-File", "build.ps1"
        ], cwd=api_dir, check=True)

        # Create security group for Lambda
        lambda_security_group = ec2.SecurityGroup(
            self, "LambdaSecurityGroup",
            vpc=database_stack.vpc,
            description="Security group for Lambda function",
            allow_all_outbound=True
        )

        # Lambda function configuration
        auth_lambda = _lambda.Function(
            self, "AuthFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="main.handler",
            code=_lambda.Code.from_asset(os.path.join(api_dir, "lambda_function.zip")),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "SECRETS_ARN": database_stack.connection_secret.secret_arn,
                "DATABASE_NAME": "${DATABASE_NAME}",  # Replace with environment variable
            },
            vpc=database_stack.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            security_groups=[lambda_security_group]
        )

        # Add Lambda permissions
        auth_lambda.role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "secretsmanager:GetSecretValue",
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "ec2:CreateNetworkInterface",
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:DeleteNetworkInterface",
                    "ec2:AssignPrivateIpAddresses",
                    "ec2:UnassignPrivateIpAddresses"
                ],
                resources=["*"]
            )
        )

        # Grant access to Secrets Manager
        database_stack.connection_secret.grant_read(auth_lambda)

        # Create API Gateway
        api = apigateway.RestApi(
            self, "AuthApi",
            rest_api_name="Auth Service API",
            description="Authentication Service API",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["*"],
                allow_methods=["GET", "POST", "DELETE"],
                allow_headers=["*"]
            )
        )

        # Create Lambda integration
        lambda_integration = apigateway.LambdaIntegration(auth_lambda)

        # Add health check endpoint
        api.root.add_resource("health").add_method("GET", lambda_integration)

        # Add auth endpoints
        auth = api.root.add_resource("auth")
        auth.add_resource("register").add_method("POST", lambda_integration)
        auth.add_resource("login").add_method("POST", lambda_integration)

        # Add user endpoints
        users = api.root.add_resource("users")
        users.add_resource("me").add_method("GET", lambda_integration)
        users.add_resource("{id}").add_method("DELETE", lambda_integration) 