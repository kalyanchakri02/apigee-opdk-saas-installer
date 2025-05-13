# Tests and Examples

This directory contains both unit tests and example scripts for the Apigee Installation Framework.

## Directory Structure

```
tests/
├── unit/                   # Unit tests for individual components
│   ├── test_product.py
│   ├── test_proxy.py
│   ├── test_shared_flow.py
│   └── test_kvm.py
├── integration/            # Integration tests
│   ├── test_installer.py
│   └── test_whitelist.py
├── examples/              # Example usage scripts
│   ├── install_all.py    # Install all resources
│   ├── install_proxy.py  # Install single proxy
│   └── install_flow.py   # Install single shared flow
└── data/                 # Test data and configurations
    ├── cloud/           # Cloud environment test data
    │   ├── config.json
    │   └── whitelist.yml
    └── onprem/          # OnPrem environment test data
        ├── config.json
        └── whitelist.yml
```

## Running Tests

### Unit Tests
```bash
python -m pytest tests/unit/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### Running Examples

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