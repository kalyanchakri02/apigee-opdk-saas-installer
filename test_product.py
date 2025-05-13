import getpass
import base64
import argparse
from install.setup.Connection import Connection
from install.resources.Product import Product
from install.WhitelistManager import WhitelistManager

def get_whitelist_manager():
    w = WhitelistManager()
    w.load_instance('cloud', './cloud/config.json', './install/config/cloud/whitelist.yml')
    return w

def main():
    parser = argparse.ArgumentParser(description="Test API Product management")
    parser.add_argument('--username', required=True, help='Apigee username')
    parser.add_argument('--host', required=True, help='Apigee host')
    parser.add_argument('--org', required=True, help='Apigee organization')
    args = parser.parse_args()

    # Get password securely
    password = getpass.getpass(prompt='Password: ')
    if not password:
        print("Error: Password is required.")
        return

    # Create basic auth credentials
    credentials = f'{args.username}:{password}'
    encoded_credentials = f"Basic {base64.b64encode(credentials.encode()).decode('utf-8')}"

    # Get product configuration
    wm = get_whitelist_manager()
    products = wm.get_whitelisted_products('cloud')
    
    if not products:
        print("No whitelisted products found")
        return

    # Test product operations
    for product_config in products:
        # Create connection for org-level operations (no environment needed)
        connection = Connection(args.org, args.host, None, encoded_credentials)
        
        # Initialize product
        product = Product(product_config['name'], product_config, connection)
        
        # Try operations
        print("\nTesting product operations...")
        product.apply()

if __name__ == "__main__":
    main() 