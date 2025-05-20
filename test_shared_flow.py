import getpass
import base64
import argparse
from install.resources.SharedFlow import SharedFlow
from install.WhitelistManager import WhitelistManager

def get_whitelist_manager():
    w = WhitelistManager()
    w.load_instance('cloud', './cloud/config.json', './install/config/cloud/whitelist.yml')
    return w

def main():
    parser = argparse.ArgumentParser(description="Test Shared Flow management")
    parser.add_argument('--username', required=True, help='Apigee username')
    parser.add_argument('--host', required=True, help='Apigee host')
    parser.add_argument('--org', required=True, help='Apigee organization')
    parser.add_argument('--env', required=True, help='Apigee environment')
    args = parser.parse_args()

    # Get password securely
    password = getpass.getpass(prompt='Password: ')
    if not password:
        print("Error: Password is required.")
        return

    # Create basic auth credentials
    credentials = f'{args.username}:{password}'
    encoded_credentials = f"Basic {base64.b64encode(credentials.encode()).decode('utf-8')}"

    # Get shared flow configuration
    wm = get_whitelist_manager()
    shared_flows = wm.get_whitelisted_shared_flows('cloud', args.env)
    
    if not shared_flows:
        print("No whitelisted shared flows found")
        return

    # Test shared flow operations
    for shared_flow_config in shared_flows:
        # Initialize shared flow
        shared_flow = SharedFlow(shared_flow_config['name'], shared_flow_config, args.org, args.host, encoded_credentials, 'cloud')
        
        # Try operations
        print("\nTesting shared flow operations...")
        shared_flow.apply()
        
        # If deploy is specified and true in config, deploy the shared flow
        if shared_flow_config.get('deploy', True):
            shared_flow.deploy([args.env])

if __name__ == "__main__":
    main() 