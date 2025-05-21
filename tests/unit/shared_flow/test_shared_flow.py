from install.resources.SharedFlow import SharedFlow
from install.WhitelistManager import WhitelistManager
import os
import getpass
import base64

def test_shared_flow_deployment():
    """Test shared flow deployment using all whitelisted shared flows."""
    # Get deployment configuration from user
    org = input("Enter Apigee organization: ")
    username = input("Enter Apigee username: ")
    password = getpass.getpass("Enter Apigee password: ")
    host = input("Enter Apigee host (e.g., api.enterprise.apigee.com): ")
    project_root = input("Enter project root directory path: ")
    instance_type = input("Enter instance type (cloud or on-prem): ")

    # Validate project root
    if not os.path.exists(project_root):
        print(f"Error: Project root directory '{project_root}' does not exist")
        return

    # Create basic auth credentials
    credentials = f'{username}:{password}'
    auth_header = f"Basic {base64.b64encode(credentials.encode()).decode('utf-8')}"
    print(f"\nUsing project root: {project_root}")

    # Initialize WhitelistManager with cloud configuration
    wm = WhitelistManager()
    wm.load_instance(instance_type, f'../../../{instance_type}/config.json', f'../../../{instance_type}/whitelist.yml')

    # Get all whitelisted shared flows
    shared_flows = wm.get_whitelisted_shared_flows(instance_type)
    if not shared_flows:
        print("No shared flows found in whitelist")
        return

    print(f"\nFound {len(shared_flows)} shared flows in whitelist")
    
    # Process each shared flow
    for shared_flow_config in shared_flows:
        shared_flow_name = shared_flow_config['name']
        deploy_envs = shared_flow_config.get('deploy', [])  
        print(f"\nProcessing shared flow: {shared_flow_name}")
        print(f"Deployment environments: {', '.join(deploy_envs)}")
        print(f"Organization: {org}")
        print(f"Host: {host}")

        try:
            shared_flow = SharedFlow(
                name=shared_flow_name,
                config=shared_flow_config,
                org=org,
                host=host,
                auth_header=auth_header,
                instance_type=instance_type,
                environments=deploy_envs,
                project_root=project_root
            )

            # Test shared flow path resolution
            flow_path = shared_flow._get_flow_path()
            print(f"Shared flow path: {flow_path}")
            assert os.path.exists(flow_path), f"Shared flow path does not exist: {flow_path}"
            print("✓ Shared flow path exists")

            # Test shared flow upload
            print("Uploading shared flow...")
            upload_result = shared_flow.apply()
            assert upload_result, True
            print("✓ Shared flow uploaded and deployed successfully based on whitelist")
            print(f"✓ Successfully processed shared flow {shared_flow_name}")

        except AssertionError as e:
            print(f"✗ Test failed for shared flow {shared_flow_name}: {str(e)}")
        except Exception as e:
            print(f"✗ Unexpected error for shared flow {shared_flow_name}: {str(e)}")

    print("\nCompleted processing all shared flows!")

if __name__ == "__main__":
    test_shared_flow_deployment() 