# Apigee OPDK/SaaS Installer

A Python-based tool for installing and managing Apigee resources across different environments and instance types (OPDK and SaaS).

## Project Structure

```
apigee-opdk-saas-installer/
├── install/
│   ├── config/
│   │   ├── SaaS/
│   │   │   └── config/
│   │   │       ├── resource.json
│   │   │       └── whitelist.yml
│   │   └── on-prem/
│   │       └── config/
│   │           ├── resource.json
│   │           └── whitelist.yml
│   ├── resources/
│   │   ├── KVM.py
│   │   ├── Proxy.py
│   │   ├── SharedFlow.py
│   │   ├── Product.py
│   │   ├── TargetServer.py
│   │   ├── CacheResource.py
│   │   ├── DeveloperApp.py
│   │   └── Reference.py
│   ├── setup/
│   │   ├── Connection.py
│   │   └── logger_config.py
│   ├── ApigeeInstaller.py
│   └── WhitelistManager.py
├── logs/
│   └── apigee_installer.log
└── README.md
```

## Features

- Supports both Apigee OPDK and SaaS instances
- Handles environment-specific and organization-level resources
- Secure credential management using interactive input
- Comprehensive logging with sensitive data redaction
- Case-sensitive instance type handling
- Automatic path resolution based on instance type
- Whitelist-based resource management

## Resource Types

1. **Environment-specific Resources**:
   - Key Value Maps (KVMs)
   - References
   - Target Servers
   - Cache Resources

2. **Organization-level Resources**:
   - API Products
   - Developer Apps

3. **API Resources**:
   - API Proxies
   - Shared Flows

## Configuration Files

### Resource Configuration (resource.json)
```json
{
  "KVM": [
    {
      "name": "example-kvm",
      "encrypted": true,
      "entry": [
        {
          "name": "key1",
          "value": "value1"
        }
      ]
    }
  ],
  "Product": [
    {
      "name": "example-product",
      "displayName": "Example Product",
      "description": "Example API Product",
      "apiResources": ["/example/**"],
      "environments": ["test", "prod"]
    }
  ]
}
```

### Whitelist Configuration (whitelist.yml)
```yaml
config:
  products:
    - name: test-product
    - name: 3skey-product

  developerApps:
    - name: test-app
  proxies:
    - name: example-api
      deploy:
        - dev
  sharedFlows:
    - name: SF-ErrorManagement
      deploy:
        - dev
  envConfig:
    dev:
      kvms:
        - name: config-kvm
      targetServers:
        - name: target-server
      references:
        - name: test-reference
```

## Usage

### Command Line Interface

```bash
python -m install.ApigeeInstaller \
  --org your-org \
  --host your-host \
  --instance-type SaaS \
  --project-root-dir /path/to/project \
  --config-file resource.json \
  --whitelist-file whitelist.yml
```

The script will:
1. Prompt for Apigee username (visible)
2. Prompt for Apigee password (hidden)
3. Validate credentials
4. Process resources based on whitelist configuration

### Instance Type Handling

- Instance type is case-sensitive: 'SaaS' or 'on-prem'
- Configuration paths are automatically determined based on instance type
- Resource handling varies by instance type (e.g., KVM updates)

### KVM Handling

- **SaaS Instances**:
  - Entries are updated individually
  - Checks for entry existence before update
  - Creates new entries if they don't exist
  - Updates existing entries if found

- **On-prem Instances**:
  - Entire KVM payload is updated at once
  - No individual entry management

### Logging

- Comprehensive logging with different levels (INFO, DEBUG)
- Sensitive data redaction for encrypted KVMs
- Separate log files for main application and tests
- Clear separation between different resource operations

## Development

### Adding New Resources

1. Create a new resource class in `install/resources/`
2. Inherit from the base `Resource` class
3. Implement required methods:
   - `_exists()`
   - `_create()`
   - `apply()`

### Testing

- Unit tests for each resource type
- Test configuration in `tests/config/`
- Separate logging configuration for tests

## Security

- Credentials are never stored on disk
- Passwords are hidden during input
- Sensitive KVM values are redacted in logs
- Instance-specific security handling

## Error Handling

- Comprehensive error checking
- Detailed error messages
- Graceful failure handling
- Resource-specific error recovery

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
