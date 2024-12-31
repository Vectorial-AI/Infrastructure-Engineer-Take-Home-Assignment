#!/usr/bin/env python3
from aws_cdk import App
from lib.database_stack import DatabaseStack
from lib.api_stack import ApiStack

app = App()

# Create database stack
database_stack = DatabaseStack(app, "AuthServiceDatabase")

# Create API stack with reference to database stack
api_stack = ApiStack(app, "AuthServiceApi", database_stack)

app.synth()
