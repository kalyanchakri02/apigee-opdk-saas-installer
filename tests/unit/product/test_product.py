from install.resources.Product import Product
from install.WhitelistManager import WhitelistManager
import getpass
import base64

def test_product_management():
    """Test product management using all whitelisted products."""
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

    # Get all whitelisted products
    products = wm.get_whitelisted_products(instance_type)
    if not products:
        print("No products found in whitelist")
        return

    print(f"\nFound {len(products)} products in whitelist")
    
    # Process each product
    for product_config in products:
        product_name = product_config['name']
        print(f"\nProcessing product: {product_name}")
        print(f"Organization: {org}")
        print(f"Host: {host}")

        try:
            product = Product(
                name=product_name,
                config=product_config,
                org=org,
                host=host,
                auth_header=auth_header
            )

            # Test product creation/update
            print("Creating/Updating product...")
            result = product.apply()
            assert result, True
            print("✓ Product created/updated successfully")
            print(f"✓ Successfully processed product {product_name}")

        except AssertionError as e:
            print(f"✗ Test failed for product {product_name}: {str(e)}")
        except Exception as e:
            print(f"✗ Unexpected error for product {product_name}: {str(e)}")

    print("\nCompleted processing all products!")

if __name__ == "__main__":
    test_product_management() 