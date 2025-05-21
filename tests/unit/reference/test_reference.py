import base64
import getpass
from install.resources.Reference import Reference
from install.WhitelistManager import WhitelistManager

def test_reference_management():
    """Test reference management using all whitelisted references."""
    # Get user input for Apigee configuration
    username = input("Enter Apigee username: ")
    password = getpass.getpass("Enter Apigee password: ")
    host = input("Enter Apigee host: ")
    org = input("Enter Apigee organization: ")
    env = input("Enter Apigee environment: ")
    instance_type = input("Enter instance type (cloud/onprem): ").lower()

    # Create basic auth header
    auth_header = f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode('utf-8')}"

    # Initialize WhitelistManager
    wm = WhitelistManager()
    wm.load_instance(instance_type, f'../../../{instance_type}/config.json', f'../../../{instance_type}/whitelist.yml')

    # Get whitelisted references
    references = wm.get_whitelisted_references(instance_type, env)
    if not references:
        print("No references found in whitelist.")
        return

    # Process each reference
    for reference_config in references:
        try:
            print(f"\nProcessing reference: {reference_config['name']}")
            print(f"Reference configuration: {reference_config}")
            
            # Validate required fields
            required_fields = ['name', 'refers', 'resourceType']
            missing_fields = [field for field in required_fields if field not in reference_config]
            if missing_fields:
                print(f"Missing required fields in reference configuration: {missing_fields}")
                continue
            
            # Create and apply reference
            reference = Reference(
                name=reference_config['name'],
                config=reference_config,
                org=org,
                host=host,
                auth_header=auth_header,
                env=env
            )
            
            # Apply reference configuration
            success = reference.apply()
            if success:
                print(f"Successfully processed reference: {reference_config['name']}")
                print(f"Reference type: {reference_config['resourceType']}")
                print(f"Reference target: {reference_config['refers']}")
            else:
                print(f"Failed to process reference: {reference_config['name']}")
                
        except AssertionError as e:
            print(f"Assertion error processing reference {reference_config['name']}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error processing reference {reference_config['name']}: {str(e)}")

    print("\nCompleted processing all references.")

if __name__ == "__main__":
    test_reference_management() 