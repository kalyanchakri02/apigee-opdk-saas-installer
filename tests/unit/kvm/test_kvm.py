from install.resources.KVM import KVM
from tests.unit.test_utils import get_test_config, get_test_connection, load_config, load_whitelist
from tests.utils.logger import logger
import os

def test_kvm_operations():
    """Test KVM creation and updates."""
    logger.info("Starting KVM operations test")
    
    # Get test configuration
    logger.debug("Loading test configuration")
    config = get_test_config()
    connection = get_test_connection(config)
    
    # Load resource configuration
    logger.debug("Loading resource configuration")
    resource_config = load_config(os.path.join(os.path.dirname(__file__), 'config.json'))
    whitelist = load_whitelist(os.path.join(os.path.dirname(__file__), 'whitelist.yml'))
    
    try:
        # Get KVM configuration from config file
        kvm_config = resource_config["envConfig"][config["env"]]["kvms"][0]
        kvm = KVM(kvm_config["name"], kvm_config, connection)
        logger.info(f"KVM initialization successful: {kvm.name}")
        
        # Test KVM apply (should create since it doesn't exist)
        logger.debug("Testing KVM creation")
        assert kvm.apply() is None
        logger.info("KVM apply (create) handled correctly")
        
        # Test KVM apply with updates
        logger.debug("Testing KVM updates")
        kvm.config["entries"] = {
            "key1": "new_value1",
            "key3": "value3"
        }
        assert kvm.apply() is None
        logger.info("KVM apply (update) handled correctly")
        
        logger.info("All KVM tests passed!")
        
    except AssertionError as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    test_kvm_operations() 