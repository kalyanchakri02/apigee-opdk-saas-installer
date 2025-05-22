import json
from typing import Dict
from install.resources.Resource import Resource
from install.setup.Connection import EnvConnection
from install.setup.logger_config import setup_logger

logger = setup_logger('KVM')

class KVM(Resource):
    """Class to manage Key Value Maps (KVMs) in Apigee."""

    def __init__(self, name: str, config: Dict, org: str, host: str, auth_header: str, instance_type: str = 'on-prem'):
        """
        Initialize KVM with name, configuration and connection details.
        
        Args:
            name: Name of the KVM
            config: KVM configuration
            org: Apigee organization name
            host: Apigee host
            auth_header: Authorization header for API calls
            instance_type: Type of instance ('cloud' or 'onprem')
        """
        super().__init__(name, config)
        self.name = name
        self.config = config
        self.org = org
        self.host = host
        self.auth_header = auth_header
        self.instance_type = instance_type.lower()
        logger.info(f"Initializing KVM: {name}")
        logger.debug(f"KVM config: {json.dumps(config, indent=2)}")

    def _get_env_connection(self, env: str) -> EnvConnection:
        """
        Create a new environment-level connection.
        
        Args:
            env: Environment name
            
        Returns:
            EnvConnection: New environment-level connection
        """
        logger.debug(f"Creating environment connection for {env}")
        return EnvConnection(
            org=self.org,
            host=self.host,
            env=env,
            auth_header=self.auth_header
        )

    def _exists(self, env: str) -> bool:
        """Check if KVM exists in the environment."""
        conn = self._get_env_connection(env)
        response = conn.get(f"keyvaluemaps/{self.name}")
        return response.status_code == 200

    def _create(self, env: str):
        """Create KVM in the environment."""
        conn = self._get_env_connection(env)
        data = {
            "name": self.name,
            "encrypted": self.config.get('encrypted', False)
        }
        response = conn.post(f"keyvaluemaps", data)
        if response.status_code not in [200, 201, 409]:
            logger.error(f"Failed to create KVM: {response.text}")
            raise Exception(f"Failed to create KVM: {response.text}")
        logger.info(f"Created KVM: {self.name} in environment: {env}")

    def _update_entries(self, env: str):
        """Update KVM entries based on instance type."""
        conn = self._get_env_connection(env)
        
        if self.instance_type == 'saas':
            self._update_entries_saas(conn, env)
        else:
            self._update_entries_onprem(conn, env)

    def _update_entries_saas(self, conn: EnvConnection, env: str):
        """Update KVM entries one by one for SaaS instance."""
        entries = self.config.get('entry', [])
        for entry in entries:
            name = entry['name']
            value = entry['value']
            data = {"name": name, "value": value}
            response = conn.post(f"keyvaluemaps/{self.name}/entries/{name}", data)
            if response.status_code not in [200, 201]:
                logger.error(f"Failed to update KVM entry {name}: {response.text}")
                raise Exception(f"Failed to update KVM entry {name}: {response.text}")
            logger.info(f"Updated KVM entry: {name}")

    def _update_entries_onprem(self, conn: EnvConnection, env: str):
        """Update entire KVM payload for on-prem instance."""
        # Get existing entries
        response = conn.get(f"keyvaluemaps/{self.name}/entries")
        if response.status_code != 200:
            logger.error(f"Failed to get KVM entries: {response.text}")
            raise Exception(f"Failed to get KVM entries: {response.text}")
        
        # Update entire KVM
        response = conn.put(f"keyvaluemaps/{self.name}", self.config)
        if response.status_code not in [200, 201]:
            logger.error(f"Failed to update KVM: {response.text}")
            raise Exception(f"Failed to update KVM: {response.text}")
        logger.info(f"Updated entire KVM: {self.name}")

    def apply(self, env: str):
        """
        Apply KVM configuration to the environment.
        
        Args:
            env: Target environment
        """
        logger.info(f"Applying KVM {self.name} to environment: {env}")
        
        try:
            if not self._exists(env):
                logger.info(f"KVM {self.name} does not exist, creating...")
                self._create(env)
            else:
                logger.info(f"KVM {self.name} already exists")
            
            # Update entries
            logger.info(f"Updating KVM entries for {self.name}")
            self._update_entries(env)
            logger.info(f"Successfully applied KVM {self.name} to environment: {env}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply KVM {self.name}: {str(e)}")
            raise



