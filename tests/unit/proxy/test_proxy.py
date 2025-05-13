from install.setup.Connection import Connection
from install.resources.Proxy import Proxy
from install.WhitelistManager import WhitelistManager
import os
import shutil

def create_dummy_proxy(name):
    """Create a dummy proxy structure for testing."""
    proxy_path = os.path.join("cloud", "api_proxies", name, "api_proxy")
    os.makedirs(proxy_path, exist_ok=True)
    
    # Create apiproxy directory
    apiproxy_dir = os.path.join(proxy_path, "apiproxy")
    os.makedirs(apiproxy_dir, exist_ok=True)
    
    # Create proxy XML
    with open(os.path.join(apiproxy_dir, f"{name}.xml"), "w") as f:
        f.write(f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<APIProxy name="{name}">
    <Description>Test API Proxy</Description>
    <DisplayName>{name}</DisplayName>
    <Policies/>
    <ProxyEndpoints>
        <ProxyEndpoint>default</ProxyEndpoint>
    </ProxyEndpoints>
    <Resources/>
    <TargetEndpoints>
        <TargetEndpoint>default</TargetEndpoint>
    </TargetEndpoints>
</APIProxy>''')

    # Create proxies directory with default endpoint
    proxies_dir = os.path.join(proxy_path, "proxies")
    os.makedirs(proxies_dir, exist_ok=True)
    with open(os.path.join(proxies_dir, "default.xml"), "w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ProxyEndpoint name="default">
    <PreFlow name="PreFlow"/>
    <Flows/>
    <PostFlow name="PostFlow"/>
    <HTTPProxyConnection>
        <BasePath>/test/v1</BasePath>
        <VirtualHost>default</VirtualHost>
    </HTTPProxyConnection>
    <RouteRule name="default"/>
</ProxyEndpoint>''')

    # Create targets directory with default endpoint
    targets_dir = os.path.join(proxy_path, "targets")
    os.makedirs(targets_dir, exist_ok=True)
    with open(os.path.join(targets_dir, "default.xml"), "w") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<TargetEndpoint name="default">
    <PreFlow name="PreFlow"/>
    <Flows/>
    <PostFlow name="PostFlow"/>
    <HTTPTargetConnection>
        <URL>http://example.com</URL>
    </HTTPTargetConnection>
</TargetEndpoint>''')

def cleanup_dummy_proxy(name):
    """Clean up the dummy proxy."""
    proxy_path = os.path.join("cloud", "api_proxies", name)
    if os.path.exists(proxy_path):
        shutil.rmtree(proxy_path)

def test_proxy_creation():
    """Test proxy creation and deployment."""
    # Setup
    proxy_name = "test-proxy"
    create_dummy_proxy(proxy_name)
    
    # Create test connection
    connection = Connection(
        org="test-org",
        host="test-host",
        env="test",
        auth_header="Basic dGVzdDp0ZXN0"  # test:test in base64
    )
    
    try:
        # Test proxy initialization
        proxy = Proxy(proxy_name, {"deploy": True}, connection, "cloud")
        print(f"✓ Proxy initialization successful: {proxy.name}")
        
        # Test proxy path resolution
        expected_path = os.path.join("cloud", "api_proxies", proxy_name, "api_proxy")
        actual_path = proxy._get_proxy_path()
        assert expected_path == actual_path
        print(f"✓ Proxy path resolution correct: {actual_path}")
        
        # Test proxy exists (should be False with test connection)
        assert proxy.exists() is False
        print("✓ Proxy exists check working")
        
        # Test proxy create
        assert proxy.create() is None
        print("✓ Proxy create handled correctly")
        
        # Test proxy deploy
        assert proxy.deploy() is None
        print("✓ Proxy deploy handled correctly")
        
        print("\nAll proxy tests passed!")
        
    except AssertionError as e:
        print(f"✗ Test failed: {str(e)}")
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
    finally:
        # Cleanup
        cleanup_dummy_proxy(proxy_name)

if __name__ == "__main__":
    test_proxy_creation() 