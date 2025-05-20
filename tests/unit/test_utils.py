import getpass
from install.setup.Connection import OrgConnection, EnvConnection
import json
import yaml
import base64

def get_test_config():
    """Get test configuration from user input."""
    print("\n=== Test Configuration ===")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    org = input("Organization: ")
    host = input("Host: ")
    env = input("Environment [test]: ") or "test"
    instance = input("Instance type [cloud]: ") or "cloud"
    
    # Create base64 encoded credentials
    credentials = f'{username}:{password}'
    auth_header = f"Basic {base64.b64encode(credentials.encode()).decode('utf-8')}"
    
    return {
        "username": username,
        "org": org,
        "host": host,
        "env": env,
        "instance": instance,
        "auth_header": auth_header
    }

def get_test_org_connection(config):
    """Create a test organization-level connection from config."""
    return OrgConnection(
        org=config["org"],
        host=config["host"],
        auth_header=config["auth_header"]
    )

def get_test_env_connection(config):
    """Create a test environment-level connection from config."""
    return EnvConnection(
        org=config["org"],
        host=config["host"],
        env=config["env"],
        auth_header=config["auth_header"]
    )

def load_config(file_path):
    """Load configuration from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def load_whitelist(file_path):
    """Load whitelist configuration from a YAML file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f) 