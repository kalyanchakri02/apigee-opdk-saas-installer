from install.resources.DeveloperApp import DeveloperApp
from install.WhitelistManager import WhitelistManager
import getpass
import base64

def test_developer_app_management():
    """Test developer app management using all whitelisted apps."""
    # Get deployment configuration from user
    org = input("Enter Apigee organization: ")
    username = input("Enter Apigee username: ")
    password = getpass.getpass("Enter Apigee password: ")
    host = input("Enter Apigee host (e.g., api.enterprise.apigee.com): ")
    instance_type = input("Enter instance type (cloud or on-prem): ")

    # Create basic auth credentials
    credentials = f'{username}:{password}'
    auth_header = f"Basic {base64.b64encode(credentials.encode()).decode('utf-8')}"

    # Initialize WhitelistManager with configuration
    wm = WhitelistManager()
    wm.load_instance(instance_type, f'../../../{instance_type}/config.json', f'../../../{instance_type}/whitelist.yml')

    # Get all whitelisted developer apps
    apps = wm.get_whitelisted_developer_apps(instance_type)
    if not apps:
        print("No developer apps found in whitelist")
        return

    print(f"\nFound {len(apps)} developer apps in whitelist")
    
    # Process each developer app
    for app_config in apps:
        app_name = app_config['name']
        print(f"\nProcessing developer app: {app_name}")
        print(f"Organization: {org}")
        print(f"Host: {host}")

        try:
            app = DeveloperApp(
                name=app_name,
                config=app_config,
                org=org,
                host=host,
                auth_header=auth_header
            )

            # Test developer app creation/update
            print("Creating/Updating developer app...")
            result = app.apply()
            assert result, True
            print("✓ Developer app created/updated successfully")
            print(f"✓ Successfully processed developer app {app_name}")

        except AssertionError as e:
            print(f"✗ Test failed for developer app {app_name}: {str(e)}")
        except Exception as e:
            print(f"✗ Unexpected error for developer app {app_name}: {str(e)}")

    print("\nCompleted processing all developer apps!")

if __name__ == "__main__":
    test_developer_app_management() 