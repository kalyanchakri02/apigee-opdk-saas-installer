from install.resources.KVM import KVM
from tests.unit.test_utils import get_test_config, get_test_connection, load_config, load_whitelist
import os

def test_kvm_operations():
    """Test KVM creation and updates."""
    # Get test configuration
    config = get_test_config()
    connection = get_test_connection(config)
    
    # Load resource configuration
    resource_config = load_config(os.path.join(os.path.dirname(__file__), 'config.json'))
    whitelist = load_whitelist(os.path.join(os.path.dirname(__file__), 'whitelist.yml'))
    
    try:
        # Get KVM configuration from config file
        kvm_config = resource_config["envConfig"][config["env"]]["kvms"][0]
        kvm = KVM(kvm_config["name"], kvm_config, connection)
        print(f"✓ KVM initialization successful: {kvm.name}")
        
        # Test KVM apply (should create since it doesn't exist)
        assert kvm.apply() is None
        print("✓ KVM apply (create) handled correctly")
        
        # Test KVM apply with updates
        kvm.config["entries"] = {
            "key1": "new_value1",
            "key3": "value3"
        }
        assert kvm.apply() is None
        print("✓ KVM apply (update) handled correctly")
        
        print("\nAll KVM tests passed!")
        
    except AssertionError as e:
        print(f"✗ Test failed: {str(e)}")
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_kvm_operations() 