#!/usr/bin/env python3
"""
Example script demonstrating how to use the Apigee Installation Framework.
"""
import argparse
import getpass
from apigee_installer.core.installer import ApigeeInstaller

def main():
    parser = argparse.ArgumentParser(description="Install Apigee resources using configuration files")
    parser.add_argument('--username', required=True, help='Apigee username')
    parser.add_argument('--host', required=True, help='Apigee host (SaaS or OnPrem management server)')
    parser.add_argument('--org', required=True, help='Apigee organization')
    parser.add_argument('--environments', required=True, help='Comma-separated list of environments to install to')
    parser.add_argument('--resource-file', required=True, help='Path to the resource configuration JSON file')
    parser.add_argument('--whitelist-file', required=True, help='Path to the whitelist YAML file')
    parser.add_argument('--proxy-dir', help='Base directory containing API proxies')
    parser.add_argument('--shared-flow-dir', help='Base directory containing shared flows')
    
    args = parser.parse_args()

    # Get password securely
    password = getpass.getpass(prompt='Password: ')
    if not password:
        print("Error: Password is required.")
        return

    # Create installer
    installer = ApigeeInstaller(
        username=args.username,
        password=password,
        org=args.org,
        host=args.host,
        resource_file=args.resource_file,
        whitelist_file=args.whitelist_file,
        proxy_base_path=args.proxy_dir,
        shared_flow_base_path=args.shared_flow_dir
    )

    # Parse environments
    environments = [env.strip() for env in args.environments.split(',')]

    # Install all resources
    installer.install_all(environments)

if __name__ == "__main__":
    main() 