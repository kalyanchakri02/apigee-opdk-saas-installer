from install.resources.Proxy import Proxy
from install.WhitelistManager import WhitelistManager
import os
import getpass
import base64

def test_proxy_deployment():
    """Test proxy deployment using all whitelisted proxies."""
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

    # Get all whitelisted proxies
    proxies = wm.get_whitelisted_proxies(instance_type)
    if not proxies:
        print("No proxies found in whitelist")
        return

    print(f"\nFound {len(proxies)} proxies in whitelist")
    
    # Process each proxy
    for proxy_config in proxies:
        proxy_name = proxy_config['name']
        deploy_envs = proxy_config.get('deploy', [])  
        print(f"\nProcessing proxy: {proxy_name}")
        print(f"Deployment environments: {', '.join(deploy_envs)}")
        print(f"Organization: {org}")
        print(f"Host: {host}")

        try:
            proxy = Proxy(
                name=proxy_name,
                config=proxy_config,
                org=org,
                host=host,
                auth_header=auth_header,
                instance_type=instance_type,
                environments=deploy_envs,
                project_root=project_root
            )

            # Test proxy path resolution
            proxy_path = proxy._get_proxy_path()
            print(f"Proxy path: {proxy_path}")
            assert os.path.exists(proxy_path), f"Proxy path does not exist: {proxy_path}"
            print("✓ Proxy path exists")

            # Test proxy upload
            print("Uploading proxy...")
            upload_result = proxy.apply()
            assert upload_result, True
            print("✓ Proxy uploaded and deployed successfully based on whitelist")
            print(f"✓ Successfully processed proxy {proxy_name}")

        except AssertionError as e:
            print(f"✗ Test failed for proxy {proxy_name}: {str(e)}")
        except Exception as e:
            print(f"✗ Unexpected error for proxy {proxy_name}: {str(e)}")

    print("\nCompleted processing all proxies!")

if __name__ == "__main__":
    test_proxy_deployment()