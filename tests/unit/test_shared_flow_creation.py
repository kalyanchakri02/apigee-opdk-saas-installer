import pytest
from install.setup.Connection import Connection
from install.resources.SharedFlow import SharedFlow
from install.WhitelistManager import WhitelistManager
import os

@pytest.fixture
def test_connection():
    """Create a test connection."""
    return Connection(
        org="test-org",
        host="test-host",
        env="test",
        auth_header="Basic dGVzdDp0ZXN0"  # test:test in base64
    )

@pytest.fixture
def test_whitelist_manager():
    """Create a test whitelist manager."""
    w = WhitelistManager()
    w.load_instance('cloud', 'tests/unit/shared_flow/config.json', 'tests/unit/shared_flow/whitelist.yml')
    return w

def test_shared_flow_initialization(test_connection):
    """Test shared flow initialization."""
    flow = SharedFlow("test-flow", {"deploy": True}, test_connection, "cloud")
    assert flow.name == "test-flow"
    assert flow.config["deploy"] is True
    assert flow.instance_type == "cloud"

def test_shared_flow_path_resolution(test_connection):
    """Test shared flow path resolution."""
    flow = SharedFlow("test-flow", {"deploy": True}, test_connection, "cloud")
    expected_path = os.path.join("cloud", "shared_flows", "test-flow", "sharedflowbundle")
    assert flow._get_flow_path() == expected_path

def test_shared_flow_exists(test_connection):
    """Test shared flow exists check."""
    flow = SharedFlow("test-flow", {"deploy": True}, test_connection, "cloud")
    assert flow.exists() is False  # Should be False with test connection

def test_shared_flow_create(test_connection):
    """Test shared flow creation."""
    flow = SharedFlow("test-flow", {"deploy": True}, test_connection, "cloud")
    assert flow.create() is None  # Should return None with test connection

def test_shared_flow_deploy(test_connection):
    """Test shared flow deployment."""
    flow = SharedFlow("test-flow", {"deploy": True}, test_connection, "cloud")
    assert flow.deploy() is None  # Should return None with test connection

def test_shared_flow_from_whitelist(test_connection, test_whitelist_manager):
    """Test shared flow creation from whitelist."""
    flows = test_whitelist_manager.get_whitelisted_shared_flows("cloud", "test")
    assert len(flows) > 0
    flow = SharedFlow(flows[0]["name"], flows[0], test_connection, "cloud")
    assert flow.name == "error-handler"
    assert flow.config["deploy"] is True 