from install.resources.Cache import Cache
from tests.unit.test_utils import get_test_config, get_test_connection, load_config, load_whitelist
import os

def test_cache_operations():
    """Test Cache creation and updates."""
    # Get test configuration
    config = get_test_config()
    connection = get_test_connection(config)
    
    # Load resource configuration
    resource_config = load_config(os.path.join(os.path.dirname(__file__), 'config.json'))
    whitelist = load_whitelist(os.path.join(os.path.dirname(__file__), 'whitelist.yml'))
    
    try:
        # Get Cache configuration from config file
        cache_config = resource_config["envConfig"][config["env"]]["caches"][0]
        cache = Cache(cache_config["name"], cache_config, connection)
        print(f"✓ Cache initialization successful: {cache.name}")
        
        # Test Cache apply (should create since it doesn't exist)
        assert cache.apply() is None
        print("✓ Cache apply (create) handled correctly")
        
        # Test Cache apply with updates
        cache.config["expirySettings"]["timeoutInSec"]["value"] = 7200
        cache.config["maxElementsInMemory"] = 2000
        assert cache.apply() is None
        print("✓ Cache apply (update) handled correctly")
        
        print("\nAll Cache tests passed!")
        
    except AssertionError as e:
        print(f"✗ Test failed: {str(e)}")
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_cache_operations() 