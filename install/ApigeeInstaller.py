import os
import base64
import argparse
import getpass

from typing import List
from install.WhitelistManager import WhitelistManager
from install.resources.Proxy import Proxy
from install.resources.SharedFlow import SharedFlow
from install.resources.Product import Product
from install.resources.TargetServer import TargetServer
from install.resources.KVM import KVM
from install.resources.CacheResource import CacheResource
from install.resources.DeveloperApp import DeveloperApp
from install.resources.Reference import Reference
from install.setup.logger_config import setup_logger, log_separator, log_file_separator

logger = setup_logger('ApigeeInstaller')

class ApigeeInstaller:
    def __init__(self, 
                 username: str,
                 password: str,
                 org: str,
                 host: str,
                 instance_type: str = 'onprem',
                 project_root_dir: str = None,
                 resource_file: str = None,
                 whitelist_file: str = None):
        """
        Initialize the Apigee resource installer.
        
        Args:
            username: Apigee username
            password: Apigee password
            org: Apigee organization
            host: Apigee host
            instance_type: Type of instance ('SaaS' or 'on-prem')
        """
        self.org = org
        self.host = host
        self.instance_type = instance_type
        self.auth_header = f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode('utf-8')}"
        
        # Determine project root and config paths
        self.project_root = project_root_dir
        self.config_dir = self._get_config_dir()
        self.resource_file = self.config_dir + '/' + resource_file
        self.whitelist_file = self.config_dir + '/' + whitelist_file
        
        logger.info(f"Initialized ApigeeInstaller for organization: {org}")
        logger.info(f"Instance type: {self.instance_type}")
        logger.info(f"Project root directory: {self.project_root}")
        logger.info(f"Config directory: {self.config_dir}")
        logger.info(f"- Resource file: {self.resource_file}")
        logger.info(f"- Whitelist file: {self.whitelist_file}")
        logger.info(f"username: {username}")

        # Initialize whitelist manager
        self.wm = WhitelistManager()
        self.wm.load_instance(instance_type, self.resource_file, self.whitelist_file)


    def _get_config_dir(self) -> str:
        """Get the config directory based on instance type."""
        logger.debug(f"Instance type: {self.instance_type}")
        config_type = 'SaaS' if self.instance_type.lower() == 'saas' else 'on-prem'
        config_dir = os.path.join(self.project_root, config_type, 'config')
        if not os.path.exists(config_dir):
            raise FileNotFoundError(f"Config directory not found: {config_dir}")
        return config_dir

    def install_shared_flows(self):
        """Install all shared flows once and deploy to environments based on whitelist."""
        log_separator(logger, "Installing Shared Flows")
        
        # Get all shared flows from whitelist
        shared_flows = self.wm.get_whitelisted_shared_flows(self.instance_type)

        logger.info(f"shared flows: {shared_flows}")
        
        for sf_config in shared_flows:
            log_file_separator(logger, f"Shared Flow: {sf_config['name']}")
            sf = SharedFlow(sf_config['name'], sf_config, self.org, self.host, self.auth_header,
                           self.instance_type, [], self.project_root)
            sf.apply()
            
            # Get deployment environments from whitelist
            deploy_envs = sf_config.get('deploy', [])
            if deploy_envs:
                logger.info(f"Deploying shared flow to environments: {', '.join(deploy_envs)}")
                sf.deploy(deploy_envs)
        log_separator(logger, "Completed Installing Shared Flows")

    def install_proxies(self):
        """Install all proxies once and deploy to environments based on whitelist."""
        log_separator(logger, "Installing API Proxies")
        
        # Get all proxies from whitelist
        proxies = self.wm.get_whitelisted_proxies(self.instance_type)

        logger.info(f"Proxies: {proxies}")
        
        for proxy_config in proxies:
            log_file_separator(logger, f"API Proxy: {proxy_config['name']}")
            proxy = Proxy(proxy_config['name'], proxy_config, self.org, self.host, self.auth_header,
                         self.instance_type, [], self.project_root)
            proxy.apply()
            
            # Get deployment environments from whitelist
            deploy_envs = proxy_config.get('deploy', [])
            if deploy_envs:
                logger.info(f"Deploying proxy to environments: {', '.join(deploy_envs)}")
                proxy.deploy(deploy_envs)
        log_separator(logger, "Completed Installing API Proxies")

    def install_environment(self, env: str):
        """
        Install all whitelisted resources for a specific environment.
        
        Args:
            env: The target environment (e.g., 'test', 'prod')
        """
        log_separator(logger, f"Installing resources for environment: {env}")

        # 1. Install KVMs
        log_file_separator(logger, "Key Value Maps (KVMs)")
        kvms = self.wm.get_whitelisted_kvms(self.instance_type, env)
        for kvm_config in kvms:
            kvm = KVM(kvm_config['name'], kvm_config, self.org, self.host, self.auth_header, self.instance_type)
            kvm.apply(env)
        log_separator(logger, "Completed Installing KVMs")

        # 2. Install References
        log_file_separator(logger, "References")
        references = self.wm.get_whitelisted_references(self.instance_type, env)
        for reference_config in references:
            reference = Reference(reference_config['name'], reference_config, self.org, self.host, self.auth_header, env)
            reference.apply(env)
        log_separator(logger, "Completed Installing References")


        # 3. Install Target Servers
        log_file_separator(logger, "Target Servers")
        target_servers = self.wm.get_whitelisted_target_servers(self.instance_type, env)
        for ts_config in target_servers:
            ts = TargetServer(ts_config['name'], ts_config, self.org, self.host, self.auth_header)
            ts.apply(env)
        log_separator(logger, "Completed Installing Target Servers")

        # 4. Install Caches
        log_file_separator(logger, "Cache Resources")
        caches = self.wm.get_whitelisted_caches(self.instance_type, env)
        for cache_config in caches:
            cache = CacheResource(cache_config['name'], cache_config, self.org, self.host, self.auth_header)
            cache.apply(env)
        log_separator(logger, "Completed Installing Cache Resources")

        log_separator(logger, "Completed Installing Resources for Environment: {env}")

    def install_org_resources(self):
        """Install organization-level resources (products, developers, apps, references)."""
        log_separator(logger, "Installing organization-level resources")

        # 1. Install API Products
        log_file_separator(logger, "API Products")
        products = self.wm.get_whitelisted_products(self.instance_type)
        logger.info(f"products: {products}")
        for product_config in products:
            product = Product(product_config['name'], product_config, self.org, self.host, self.auth_header)
            product.apply()
        log_separator(logger, "Completed Installing API Products")

        # 2. Install Developer Apps
        log_file_separator(logger, "Developer Apps")
        # apps = self.wm.get_whitelisted_developer_apps(self.instance_type)
        # for app_config in apps:
        #     app = DeveloperApp(app_config['name'], app_config, self.org, self.host, self.auth_header)
        #     app.apply()
        log_separator(logger, "framework does not support developer apps")

    def install_all(self, environments: List[str]):
        """
        Install all resources for all specified environments.
        
        Args:
            environments: List of environments to install resources in
        """
        logger.info("Starting Apigee resource installation")
        logger.info(f"Environments to process: {', '.join(environments)}")
        
        # First install environment-specific resources
        for env in environments:
            self.install_environment(env)

        # then, install shared flows and proxies (uploaded once)
        self.install_shared_flows()
        self.install_proxies()

        # Finally install org-level resources
        self.install_org_resources()
        
        logger.info("Completed Apigee resource installation")

def main():
    """Main function to run the Apigee resource installer."""
    parser = argparse.ArgumentParser(description='Install Apigee resources based on configuration and whitelist.')
    
    # Required arguments
    parser.add_argument('--org', required=True, help='Apigee organization name')
    parser.add_argument('--host', required=True, help='Apigee host URL')
    parser.add_argument('--instance-type', required=True, choices=['SaaS', 'on-prem'],
                      help='Type of Apigee instance (SaaS or on-prem)')
    parser.add_argument('--project-root-dir', required=True, help='Project root directory')
    parser.add_argument('--config-file', required=True, help='resource config file')
    parser.add_argument('--whitelist-file', required=True, help='whitelist file')
    
    args = parser.parse_args()
    
    try:
        # Get username and password
        username = input("Enter Apigee username: ")
        password = getpass.getpass("Enter Apigee password: ")
        
        if not username or not password:
            raise ValueError("Username and password are required")
        
        # Initialize the installer
        installer = ApigeeInstaller(
            username=username,
            password=password,
            org=args.org,
            host=args.host,
            instance_type=args.instance_type,
            project_root_dir=args.project_root_dir,
            resource_file=args.config_file,
            whitelist_file=args.whitelist_file
        )
        
        # Get environments from whitelist configuration
        environments = list(installer.wm.instances[installer.instance_type]['whitelist'].get('config', {}).get('envConfig', {}).keys())
        logger.info(f"environments found in whitelist: {', '.join(environments)}")
        if not environments:
            raise ValueError(f"No environments found in whitelist for instance type: {installer.instance_type}")
        
        
        # Install resources
        installer.install_all(environments)
        
    except Exception as e:
        logger.error(f"Installation failed: {str(e)}")
        raise

if __name__ == '__main__':
    main() 