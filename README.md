# Apigee OnPrem/SaaS Installation Framework

A Python framework for installing and managing Apigee resources across OnPrem and SaaS environments. This framework provides a unified approach to managing API proxies, shared flows, and other Apigee resources regardless of the deployment type.

## Features

- Unified management for both OnPrem and SaaS environments
- Support for all Apigee resources:
  - API Proxies
  - Shared Flows
  - API Products
  - Target Servers
  - Key-Value Maps (KVMs)
  - Caches
  - Developer Apps
- Environment-specific installations
- Configuration-driven using JSON and YAML files
- Comprehensive logging
- Secure credential handling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kalyanchakri02/apigee-opdk-saas-installer
cd apigee-opdk-saas-installer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration Files

The framework uses two main configuration files:

1. `config.json`: Contains the resource definitions and configurations
2. `whitelist.yml`: Defines which resources should be deployed

These files should be placed in your instance-specific directory (e.g., `cloud/` or `onprem/`).

### config.json Example
```json
{
  "version": "1.0",
  "envConfig": {
    "test": {
      "targetServers": [
        {
          "name": "test-server",
          "host": "api.test.com",
          "port": 443,
          "ssl": true
        }
      ],
      "sharedFlows": [
        {
          "name": "error-handler",
          "deploy": true
        }
      ],
      "kvms": [
        {
          "name": "config-kvm",
          "encrypted": true,
          "entries": {
            "key1": "value1",
            "key2": "value2"
          }
        }
      ],
      "caches": [
        {
          "name": "response-cache",
          "description": "Cache for API responses",
          "timeoutInSec": 3600,
          "maxElementsInMemory": 1000,
          "maxElementSizeInKB": 512,
          "overflowToDisk": true,
          "persistent": false
        }
      ]
    }
  },
  "orgConfig": {
    "apiProducts": {
      "product-name": {
        "name": "product-name",
        "displayName": "Example Product",
        "description": "Example API Product",
        "environments": ["test"],
        "proxies": ["example-api"],
        "scopes": [],
        "quota": "10000",
        "quotaInterval": "1",
        "quotaTimeUnit": "month"
      }
    },
    "developers": {
      "developer@example.com": {
        "email": "developer@example.com",
        "firstName": "Test",
        "lastName": "Developer",
        "userName": "testdev"
      }
    },
    "developerApps": {
      "test-app": {
        "name": "test-app",
        "developer": "developer@example.com",
        "products": ["product-name"]
      }
    }
  }
}
```

### whitelist.yml Example
```yaml
config:
  products:
    - name: product-name
  developerApps:
    - name: test-app
  envConfig:
    test:
      proxies:
        - name: example-api
          deploy: true
      sharedFlows:
        - name: error-handler
          deploy: true
      kvms:
        - name: config-kvm
      caches:
        - name: response-cache
      targetServers:
        - name: test-server
```

## Project Structure
```
.
├── install/             # Main package
│   ├── core/           # Core functionality
│   │   ├── installer.py    # Main installer class
│   │   ├── client.py      # Apigee API client
│   │   └── config.py      # Configuration management
│   └── resources/     # Resource implementations
│       ├── proxy.py
│       ├── shared_flow.py
│       ├── kvm.py
│       ├── cache.py
│       └── ...
├── tests/            # Tests and examples
│   ├── unit/        # Unit tests
│   ├── integration/ # Integration tests
│   ├── examples/    # Example scripts
│   └── data/        # Test data and configurations
├── cloud/           # Cloud instance configs and resources
│   ├── config.json
│   ├── whitelist.yml
│   ├── api_proxies/     # API Proxies for cloud environment
│   │   └── ...
│   └── shared_flows/    # Shared Flows for cloud environment
│       └── ...
├── onprem/          # OnPrem instance configs and resources
│   ├── config.json
│   ├── whitelist.yml
│   ├── api_proxies/
│   │   └── ...
│   └── shared_flows/
│       └── ...
└── README.md
```

## Usage

### Command Line Examples

1. Install all resources:
```bash
python tests/examples/install_all.py \
  --username your-username \
  --host api.enterprise.apigee.com \
  --org your-org \
  --environments "test,prod" \
  --instance cloud
```

2. Install single proxy:
```bash
python tests/examples/install_proxy.py \
  --username your-username \
  --host api.enterprise.apigee.com \
  --org your-org \
  --env test \
  --proxy-name example-api \
  --instance cloud
```

3. Install single shared flow:
```bash
python tests/examples/install_flow.py \
  --username your-username \
  --host api.enterprise.apigee.com \
  --org your-org \
  --env test \
  --flow-name error-handler \
  --instance cloud
```

### As a Library

```python
from install.ApigeeInstaller import ApigeeInstaller

# Create installer instance
installer = ApigeeInstaller(
    username="your-username",
    password="your-password",
    org="your-org",
    host="api.enterprise.apigee.com",  # For SaaS
    instance_type="cloud"  # or "onprem"
)

# Install resources in specific environments
installer.install_all(["test", "prod"])
```

## Resource Types

### Key Value Maps (KVMs)
- Support for encrypted and unencrypted KVMs
- Batch entry management
- Environment-specific configurations

### Cache Resources
- Configurable timeout settings
- Memory and disk overflow settings
- Size limits configuration
- Persistence options
- Environment-specific configurations

### API Proxies
- Support for multiple environments
- Version management
- Deployment status tracking

### Shared Flows
- Reusable flow management
- Environment-specific deployments
- Version control

### API Products
- Product bundling
- Quota management
- Access control

### Developer Apps
- Developer management
- Product association
- Credential management

## Resource Structures

### API Proxy Structure
```
{instance_type}/api_proxies/
└── {proxy_name}/
    └── api_proxy/          # Standard Apigee proxy structure
        ├── proxies/
        ├── policies/
        ├── resources/
        ├── targets/
        └── apiproxy/
```

Example:
```
cloud/api_proxies/
└── example-api/
    └── api_proxy/
        ├── proxies/
        │   └── default.xml
        ├── policies/
        │   └── rate-limit.xml
        └── apiproxy/
            └── example-api.xml
```

### Shared Flow Structure
```
{instance_type}/shared_flows/
└── {flow_name}/
    └── sharedflowbundle/   # Standard Apigee shared flow structure
        ├── policies/
        ├── sharedflows/
        └── sharedflowbundle/
```

Example:
```
cloud/shared_flows/
└── error-handler/
    └── sharedflowbundle/
        ├── policies/
        │   ├── raise-fault.xml
        │   └── set-response.xml
        ├── sharedflows/
        │   └── default.xml
        └── sharedflowbundle/
            └── error-handler.xml
```

The framework will automatically:
1. Look for proxies in `{instance_type}/api_proxies` directory
2. Look for shared flows in `{instance_type}/shared_flows` directory
3. Use the directory names as the resource names
4. Zip and deploy the contents of the appropriate directories (`api_proxy` or `sharedflowbundle`)

## Environment Support

### SaaS
- Uses standard Apigee SaaS endpoints
- Supports all Apigee Edge features
- Compatible with Apigee X/hybrid configurations

### OnPrem
- Supports custom management server URLs
- Compatible with private cloud deployments
- Handles OnPrem-specific configurations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## API Proxy Structure

API proxies should follow this structure:
```
{instance_type}/api_proxies/
└── {proxy_name}/
    └── api_proxy/          # Standard Apigee proxy structure
        ├── proxies/
        ├── policies/
        ├── resources/
        ├── targets/
        └── apiproxy/
```

For example:
```
cloud/api_proxies/
└── example-api/
    └── api_proxy/
        ├── proxies/
        │   └── default.xml
        ├── policies/
        │   └── rate-limit.xml
        └── apiproxy/
            └── example-api.xml
```

The framework will automatically:
1. Look for proxies in the `{instance_type}/api_proxies` directory
2. Use the directory name as the proxy name
3. Zip and deploy the contents of the `api_proxy` directory

The rest of the README remains unchanged. # apigee-opdk-saas-installer
