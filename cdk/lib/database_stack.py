from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_docdb as docdb,
    aws_secretsmanager as secretsmanager,
    RemovalPolicy,
    Duration,
    SecretValue,
)
from constructs import Construct

class DatabaseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC without NAT gateways
        self.vpc = ec2.Vpc(
            self, "AuthServiceVPC",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
            ]
        )

        # Create security group for DocumentDB
        self.db_security_group = ec2.SecurityGroup(
            self, "DocDBSecurityGroup",
            vpc=self.vpc,
            description="Security group for DocumentDB cluster",
            allow_all_outbound=True
        )

        # Allow inbound from any security group that will be created later
        self.db_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(27017),
            description="Allow inbound from VPC CIDR"
        )

        # Create DB subnet group
        db_subnet_group = docdb.CfnDBSubnetGroup(
            self, "DocumentDBSubnetGroup",
            subnet_ids=self.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ).subnet_ids,
            db_subnet_group_description="Subnet group for DocumentDB"
        )

        # Create DocumentDB cluster with credentials from environment/parameters
        self.db_cluster = docdb.CfnDBCluster(
            self, "Database",
            availability_zones=self.vpc.availability_zones[:2],
            db_cluster_identifier="auth-service-db",
            vpc_security_group_ids=[self.db_security_group.security_group_id],
            db_subnet_group_name=db_subnet_group.ref,
            master_username="ADMIN_USERNAME",  # TODO: Replace with environment variable
            master_user_password="ADMIN_PASSWORD",  # TODO: Replace with SecretValue or parameter
            storage_encrypted=True,
            port=27017
        )

        # Create DB instance
        self.db_instance = docdb.CfnDBInstance(
            self, "DatabaseInstance",
            db_cluster_identifier=self.db_cluster.ref,
            db_instance_class="db.t3.medium"
        )

        # Store connection information securely
        self.connection_secret = secretsmanager.Secret(
            self, "DBConnectionSecret",
            description="DocumentDB connection information",
            secret_string_value=SecretValue.unsafe_plain_text(
                f'{{"username": "ADMIN_USERNAME", "password": "ADMIN_PASSWORD", "host": "{self.db_cluster.attr_endpoint}", "port": "27017", "dbname": "authservice"}}'
            )
        )