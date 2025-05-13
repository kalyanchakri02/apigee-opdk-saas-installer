import json
import yaml

class WhitelistManager:
    def __init__(self):
        self.instances = {}

    def load_instance(self, instance_name: str, resource_path: str, whitelist_path: str):
        """Load resource and whitelist files for an instance (e.g., cloud or onprem)."""
        with open(resource_path, 'r') as rf:
            resources = json.load(rf)
        with open(whitelist_path, 'r') as wf:
            whitelist = yaml.safe_load(wf)
        self.instances[instance_name] = {
            'resources': resources,
            'whitelist': whitelist
        }

    def _get_env_config(self, instance: str, env: str):
        """Get environment config from whitelist."""
        return self.instances[instance]['whitelist'].get('config', {}).get('envConfig', {}).get(env, {})

    def _get_resource_env_config(self, instance: str, env: str):
        """Get environment config from resources."""
        return self.instances[instance]['resources'].get('envConfig', {}).get(env, {})

    def get_whitelisted_proxies(self, instance: str, env: str):
        whitelisted = self._get_env_config(instance, env).get('proxies', [])
        return [p for p in whitelisted if p.get('name')]

    def get_whitelisted_shared_flows(self, instance: str, env: str):
        whitelisted = self._get_env_config(instance, env).get('sharedFlows', [])
        return [sf for sf in whitelisted if sf.get('name')]

    def get_whitelisted_kvms(self, instance: str, env: str):
        whitelisted = self._get_env_config(instance, env).get('kvms', [])
        return [k for k in whitelisted if k.get('name')]

    def get_whitelisted_target_servers(self, instance: str, env: str):
        whitelisted_names = set(t['name'] for t in self._get_env_config(instance, env).get('targetServers', []) if t.get('name'))
        resource_servers = self._get_resource_env_config(instance, env).get('targetServers', [])
        return [server for server in resource_servers if server.get('name') in whitelisted_names]

    def get_whitelisted_products(self, instance: str):
        whitelisted = self.instances[instance]['whitelist'].get('config', {}).get('products', [])
        products = self.instances[instance]['resources'].get('orgConfig', {}).get('apiProducts', {})
        return [products[p['name']] for p in whitelisted if p.get('name') and p['name'] in products]

    def get_whitelisted_developer_apps(self, instance: str):
        whitelisted = self.instances[instance]['whitelist'].get('config', {}).get('developerApps', [])
        apps = self.instances[instance]['resources'].get('orgConfig', {}).get('developerApps', {})
        return [apps[a['name']] for a in whitelisted if a.get('name') and a['name'] in apps]
