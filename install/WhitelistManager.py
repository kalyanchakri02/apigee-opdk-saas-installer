import json
import yaml
from typing import Optional
from install.setup.logger_config import setup_logger

logger = setup_logger('WhitelistManager')

class WhitelistManager:
    def __init__(self):
        self.instances = {}

    def load_instance(self, instance_name: str, resource_path: str, whitelist_path: str):
        """Load resource and whitelist files for an instance (e.g., cloud or onprem)."""
        with open(resource_path, 'r') as rf:
            logger.info(f"Loading resource file: {resource_path}")
            resources = json.load(rf)
        with open(whitelist_path, 'r') as wf:
            logger.info(f"Loading whitelist file: {whitelist_path}")
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

    def get_whitelisted_proxies(self, instance: str):
        """Get all whitelisted proxies."""
        return self.instances[instance]['whitelist'].get('config', {}).get('proxies', [])

    def get_whitelisted_shared_flows(self, instance: str):
        """Get all whitelisted shared flows."""
        return self.instances[instance]['whitelist'].get('config', {}).get('sharedFlows', [])

    def get_proxy_deployment_envs(self, instance: str, proxy_name: str):
        """Get deployment environments for a specific proxy."""
        proxies = self.get_whitelisted_proxies(instance)
        for proxy in proxies:
            if proxy.get('name') == proxy_name:
                return proxy.get('deploy', [])
        return []

    def get_shared_flow_deployment_envs(self, instance: str, shared_flow_name: str):
        """Get deployment environments for a specific shared flow."""
        shared_flows = self.get_whitelisted_shared_flows(instance)
        for sf in shared_flows:
            if sf.get('name') == shared_flow_name:
                return sf.get('deploy', [])
        return []

    def get_whitelisted_kvms(self, instance: str, env: str):
        """Get whitelisted KVMs for the specified environment."""
        whitelisted = self._get_env_config(instance, env).get('kvms', [])
        resource_kvms = self._get_resource_env_config(instance, env).get('kvms', [])
        
        # Create a map of whitelisted KVM names to their configs
        whitelisted_map = {k['name']: k for k in whitelisted if k.get('name')}
        
        # Return KVMs that are in both whitelist and resources
        return [kvm for kvm in resource_kvms if kvm.get('name') in whitelisted_map]

    def get_whitelisted_target_servers(self, instance: str, env: str):
        """Get whitelisted target servers for the specified environment."""
        whitelisted_names = set(t['name'] for t in self._get_env_config(instance, env).get('targetServers', []) if t.get('name'))
        resource_servers = self._get_resource_env_config(instance, env).get('targetServers', [])
        return [server for server in resource_servers if server.get('name') in whitelisted_names]
    
    def get_whitelisted_caches(self, instance: str, env: str):
        """Get whitelisted caches for the specified environment."""
        whitelisted_names = set(c['name'] for c in self._get_env_config(instance, env).get('caches', []) if c.get('name'))
        resource_caches = self._get_resource_env_config(instance, env).get('caches', [])
        return [cache for cache in resource_caches if cache.get('name') in whitelisted_names]

    def get_whitelisted_products(self, instance: str):
        """Get whitelisted API products."""
        whitelisted = self.instances[instance]['whitelist'].get('config', {}).get('products', [])
        products = self.instances[instance]['resources'].get('orgConfig', {}).get('apiProducts', {})
        return [products[p['name']] for p in whitelisted if p.get('name') and p['name'] in products]

    def get_whitelisted_developer_apps(self, instance: str):
        """Get whitelisted developer apps."""
        whitelisted = self.instances[instance]['whitelist'].get('config', {}).get('developerApps', [])
        apps = self.instances[instance]['resources'].get('orgConfig', {}).get('developerApps', {})
        return [apps[a['name']] for a in whitelisted if a.get('name') and a['name'] in apps]

    def get_whitelisted_references(self, instance: str, env: Optional[str] = None):
        """
        Get whitelisted references for the specified environment or organization.
        
        Args:
            instance: Instance name (e.g., 'default')
            env: Environment name (optional, if None then org-level references)
            
        Returns:
            List[Dict]: List of whitelisted references
        """
        if env:
            # Get environment-level references
            whitelisted = self._get_env_config(instance, env).get('references', [])
            references = self._get_resource_env_config(instance, env).get('references', [])
        else:
            # Get organization-level references
            whitelisted = self.instances[instance]['whitelist'].get('config', {}).get('references', [])
            references = self.instances[instance]['resources'].get('orgConfig', {}).get('references', [])
            
        # Return references that are in both whitelist and resources
        whitelisted_names = {r['name'] for r in whitelisted if r.get('name')}
        return [r for r in references if r.get('name') in whitelisted_names]
