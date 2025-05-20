import os
import base64
from typing import Optional, Dict, List
from install.WhitelistManager import WhitelistManager
from install.resources.Proxy import Proxy
from install.resources.SharedFlow import SharedFlow
from install.resources.Product import Product
from install.resources.TargetServer import TargetServer
from install.resources.KVM import KVM
from install.resources.CacheResource import CacheResource
from install.resources.DeveloperApp import DeveloperApp
from install.resources.Reference import Reference
from install.setup.logger_config import setup_logger, log_separator

logger = setup_logger('ApigeeInstaller')

class ApigeeInstaller:
    def __init__(self, 
                 username: str,
                 password: str,
                 org: str,
                 host: str,
                 resource_file: str,
                 whitelist_file: str,
                 proxy_base_path: Optional[str] = None,
                 shared_flow_base_path: Optional[str] = None):
        """
        Initialize the Apigee resource installer.
        
        Args:
            username: Apigee username
            password: Apigee password
            org: Apigee organization
            host: Apigee host
            resource_file: Path to the resource configuration JSON file
            whitelist_file: Path to the whitelist YAML file
            proxy_base_path: Base directory containing API proxies (optional)
            shared_flow_base_path: Base directory containing shared flows (optional)
        """
        self.org = org
        self.host = host
        self.auth_header = f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode('utf-8')}"
        self.proxy_base_path = proxy_base_path
        self.shared_flow_base_path = shared_flow_base_path
        
        # Initialize whitelist manager
        self.wm = WhitelistManager()
        self.wm.load_instance('default', resource_file, whitelist_file)

    def _update_resource_paths(self, resources: List[Dict], base_path: str) -> List[Dict]:
        """Update resource paths to be absolute based on the base path."""
        if not base_path or not resources:
            return resources
        
        updated_resources = []
        for resource in resources:
            if resource.get('path'):
                resource['path'] = os.path.join(base_path, resource['path'])
            updated_resources.append(resource)
        return updated_resources

    def install_environment(self, env: str):
        """
        Install all whitelisted resources for a specific environment.
        
        Args:
            env: The target environment (e.g., 'test', 'prod')
        """
        log_separator(logger, f"Installing resources for environment: {env}")

        # Install target servers
        target_servers = self.wm.get_whitelisted_target_servers('default', env)
        for ts_config in target_servers:
            ts = TargetServer(ts_config['name'], ts_config, self.org, self.host, self.auth_header)
            ts.apply(env)

        # Install KVMs
        kvms = self.wm.get_whitelisted_kvms('default', env)
        for kvm_config in kvms:
            kvm = KVM(kvm_config['name'], kvm_config, self.org, self.host, self.auth_header)
            kvm.apply(env)

        # Install caches
        caches = self.wm.get_whitelisted_caches('default', env)
        for cache_config in caches:
            cache = CacheResource(cache_config['name'], cache_config, self.org, self.host, self.auth_header)
            cache.apply(env)

        # Install environment-level references
        references = self.wm.get_whitelisted_references('default', env)
        for reference_config in references:
            reference = Reference(reference_config['name'], reference_config, self.org, self.host, self.auth_header, env)
            reference.apply(env)

        # Install proxies
        proxies = self.wm.get_whitelisted_proxies('default', env)
        proxies = self._update_resource_paths(proxies, self.proxy_base_path)
        for proxy_config in proxies:
            proxy = Proxy(proxy_config['name'], proxy_config, self.org, self.host, self.auth_header,
                         self.wm.instance_type, [env], self.proxy_base_path)
            proxy.apply()
            if proxy_config.get('deploy', True):
                proxy.deploy([env])

        # Install shared flows
        shared_flows = self.wm.get_whitelisted_shared_flows('default', env)
        shared_flows = self._update_resource_paths(shared_flows, self.shared_flow_base_path)
        for sf_config in shared_flows:
            sf = SharedFlow(sf_config['name'], sf_config, self.org, self.host, self.auth_header,
                           self.wm.instance_type, [env], self.shared_flow_base_path)
            sf.apply()
            if sf_config.get('deploy', True):
                sf.deploy([env])

    def install_org_resources(self):
        """Install organization-level resources (products, developers, apps, references)."""
        log_separator(logger, "Installing organization-level resources")

        # Install API products
        products = self.wm.get_whitelisted_products('default')
        for product_config in products:
            product = Product(product_config['name'], product_config, self.org, self.host, self.auth_header)
            product.apply()

        # Install developer apps
        apps = self.wm.get_whitelisted_developer_apps('default')
        for app_config in apps:
            app = DeveloperApp(app_config['name'], app_config, self.org, self.host, self.auth_header)
            app.apply()

        # Install organization-level references
        references = self.wm.get_whitelisted_references('default')
        for reference_config in references:
            reference = Reference(reference_config['name'], reference_config, self.org, self.host, self.auth_header)
            reference.apply()

    def install_all(self, environments: List[str]):
        """
        Install all resources for all specified environments.
        
        Args:
            environments: List of environments to install resources in
        """
        logger.info("Starting Apigee resource installation")
        
        # First install org-level resources
        self.install_org_resources()
        
        # Then install environment-specific resources
        for env in environments:
            self.install_environment(env)
        
        logger.info("Completed Apigee resource installation") 