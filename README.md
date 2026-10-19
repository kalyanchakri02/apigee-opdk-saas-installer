# Apigee OPDK/SaaS Installer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)

**Promote Apigee configuration and API artifacts between environments with one config-driven command, for both Apigee OPDK (on-prem) and SaaS.**

Moving proxies, shared flows, KVMs, target servers, caches, API products and developer apps between Apigee orgs and environments usually means a pile of ad-hoc scripts, and OPDK and SaaS behave differently (for example, KVM updates). This tool puts one declarative `resource.json` and a `whitelist.yml` in front of both, so the same workflow works on either platform and you control exactly what gets deployed.

## Why use it

- **One tool, two platforms.** Set `--instance-type SaaS` or `on-prem`. Per-platform differences (such as KVM handling) are handled for you.
- **Whitelist-driven.** Only resources listed in `whitelist.yml` are touched, so promotions are explicit and reviewable in a pull request.
- **Safe by default.** Credentials are prompted for, never stored on disk. Encrypted KVM values are redacted from logs.
- **Idempotent.** Each resource checks whether it exists, then creates or updates it.
- **Extensible.** Adding a new resource type is one small class.

## Supported resources

| Scope | Resources |
|---|---|
| Environment | KVMs, References, Target Servers, Caches |
| Organization | API Products, Developer Apps |
| API | API Proxies, Shared Flows |

## Quickstart

```bash
git clone https://github.com/kalyanchakri02/apigee-opdk-saas-installer.git
cd apigee-opdk-saas-installer
pip install -r requirements.txt

python -m install.ApigeeInstaller \
  --org your-org \
  --host your-host \
  --instance-type SaaS \
  --project-root-dir /path/to/project \
  --config-file resource.json \
  --whitelist-file whitelist.yml
```

Config files are resolved as `<project-root-dir>/<SaaS|on-prem>/config/<file>`, so lay out your project like this:

```
my-project/
├── SaaS/config/{resource.json, whitelist.yml}
└── on-prem/config/{resource.json, whitelist.yml}
```

You will be prompted for your Apigee username and password (hidden input). The tool then validates the credentials and processes the resources listed in the whitelist.

> `--instance-type` is case-sensitive: `SaaS` or `on-prem`. Config paths are resolved automatically from it.

## How it works

```
resource.json  ──┐                       ┌── Proxy / SharedFlow
                 ├──> ApigeeInstaller ───┼── KVM / Reference / TargetServer / Cache
whitelist.yml  ──┘   (WhitelistManager)  └── Product / DeveloperApp
                          │
                  Connection (SaaS | on-prem)
```

1. `resource.json` describes *everything that could be deployed* per environment (`envConfig`) and org (`orgConfig`).
2. `whitelist.yml` selects *what to deploy this run*.
3. `ApigeeInstaller` builds the plan, and each resource class implements `_exists()`, `_create()` and `apply()`.

## Configuration

### `resource.json`

```json
{
  "version": "1.0",
  "envConfig": {
    "dev": {
      "sharedFlows": [{ "name": "SF-ErrorManagement" }],
      "kvms": [{ "name": "config-kvm", "entry": [{ "name": "key1", "value": "value1" }] }],
      "references": [{ "name": "test-reference", "refers": "my-keystore", "resourceType": "KeyStore" }],
      "targetServers": [], "caches": [], "flowHooks": []
    }
  },
  "orgConfig": {
    "apiProducts": {
      "test-product": {
        "name": "test-product",
        "displayName": "Test API Product",
        "approvalType": "auto",
        "environments": ["dev"],
        "proxies": ["example-api"]
      }
    },
    "developerApps": {
      "test-app": { "name": "test-app", "displayName": "Test App", "apiProducts": ["test-product"] }
    }
  }
}
```

### `whitelist.yml`

```yaml
config:
  products:
    - name: test-product
  developerApps:
    - name: test-app
  proxies:
    - name: example-api
      deploy: [dev]
  sharedFlows:
    - name: SF-ErrorManagement
      deploy: [dev]
  envConfig:
    dev:
      kvms:
        - name: config-kvm
```

## Platform differences

| Behavior | SaaS | on-prem (OPDK) |
|---|---|---|
| KVM updates | Per entry: checks existence, creates or updates each | Entire KVM payload replaced at once |

## Logging and security

- Logs go to a `logs/` directory (INFO and DEBUG); the folder is git-ignored. Tests use a separate log config.
- Sensitive and encrypted KVM values are redacted.
- Credentials are never written to disk, and the password prompt is hidden.

## Extending

1. Add a class in `install/resources/` that inherits the base `Resource` class.
2. Implement `_exists()`, `_create()` and `apply()`.
3. Wire it into `install/ApigeeInstaller.py` and add a sample to `resource.json`.

## Tests

Unit tests live in `tests/unit/` and run with `python -m pytest tests/unit/`. Some tests call a real Apigee org, so check `tests/unit/test_utils.py` and point them at a non-production org first.

## Roadmap

- [ ] Dry-run mode (`--dry-run`) that prints the plan without applying
- [ ] Non-interactive auth (env vars / token) for CI pipelines
- [ ] Flow hooks and developers support
- [ ] Docker image and GitHub Actions example
- [ ] Unit test coverage report

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Good first issues are labelled `good first issue`.

## License

MIT. See [LICENSE](LICENSE).
