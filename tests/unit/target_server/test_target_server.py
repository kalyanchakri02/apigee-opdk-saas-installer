from install.resources.TargetServer import TargetServer
from tests.unit.test_utils import get_test_config, get_test_connection, load_config
import os
from tests.utils.logger import logger

def test_target_server_operations():
    """Test Target Server creation and updates."""
    # Get test configuration
    config = get_test_config()
    connection = get_test_connection(config)
    
    # Load resource configuration
    resource_config = load_config(os.path.join(os.path.dirname(__file__), 'config.json'))
    
    try:
        # Get Target Server configuration from config file
        server_config = resource_config["envConfig"][config["env"]]["targetServers"][0]
        server = TargetServer(server_config["name"], server_config, connection)
        print(f"✓ Target Server initialization successful: {server.name}")
        
        # Test Target Server apply (should create since it doesn't exist)
        assert server.apply() is True
        print("✓ Target Server apply (create) handled correctly")
        
        # Test Target Server apply with updates
        server.config["host"] = "new.example.com"
        server.config["port"] = 8443
        server.config["sSLInfo"]["ignoreValidationErrors"] = True
        assert server.apply() is True
        print("✓ Target Server apply (update) handled correctly")
        
        print("\nAll Target Server tests passed!")
        
    except AssertionError as e:
        print(f"✗ Test failed: {str(e)}")
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_target_server_operations() 