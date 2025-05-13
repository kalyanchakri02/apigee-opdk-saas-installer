import pytest
from install.setup.Connection import Connection
from install.resources.Product import Product
from install.WhitelistManager import WhitelistManager

def get_test_config():
    """Get test configuration."""
    w = WhitelistManager()
    w.load_instance('cloud', './tests/data/cloud/config.json', './tests/data/cloud/whitelist.yml')
    return w.get_whitelisted_products('cloud')[0]

def get_test_connection():
    """Get test connection with mock credentials."""
    return Connection(
        org="test-org",
        host="test-host",
        env=None,  # Products are org-level resources
        auth_header="Basic dGVzdDp0ZXN0"  # test:test in base64
    )

def test_product_initialization():
    """Test product initialization."""
    config = get_test_config()
    connection = get_test_connection()
    product = Product(config['name'], config, connection)
    assert product.name == config['name']
    assert product.config == config

def test_product_exists():
    """Test product exists check."""
    config = get_test_config()
    connection = get_test_connection()
    product = Product(config['name'], config, connection)
    # This will return False since we're using a test connection
    assert product.exists() is False

def test_product_create():
    """Test product creation."""
    config = get_test_config()
    connection = get_test_connection()
    product = Product(config['name'], config, connection)
    # This will return None since we're using a test connection
    assert product.create() is None

def test_product_update():
    """Test product update."""
    config = get_test_config()
    connection = get_test_connection()
    product = Product(config['name'], config, connection)
    # This will return None since we're using a test connection
    assert product.update() is None

def test_product_delete():
    """Test product deletion."""
    config = get_test_config()
    connection = get_test_connection()
    product = Product(config['name'], config, connection)
    # This will return None since we're using a test connection
    assert product.delete() is None 