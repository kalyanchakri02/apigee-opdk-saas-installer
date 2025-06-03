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
        self.is_encrypted = config.get('encrypted', False)
        logger.info(f"Initializing KVM: {name}")
        logger.debug(f"KVM config: {self._get_safe_config()}")

    def _get_safe_config(self) -> Dict:
        """Get a safe version of the config for logging."""
        safe_config = self.config.copy()
        if self.is_encrypted and 'entry' in safe_config:
            safe_config['entry'] = [{'name': entry['name'], 'value': '***REDACTED***'} 
                                  for entry in safe_config['entry']]
        return safe_config

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
            "encrypted": self.is_encrypted
        }
        response = conn.post(f"keyvaluemaps", data)
        if response.status_code not in [200, 201, 409]:
            logger.error(f"Failed to create KVM: {response.text}")
            raise Exception(f"Failed to create KVM: {response.text}")
        logger.info(f"Created KVM: {self.name} in environment: {env}")

    def _update_entries(self, env: str):
        """Update KVM entries based on instance type."""
        conn = self._get_env_connection(env)
        
        if self.instance_type.lower() == 'saas':
            self._update_entries_saas(env)
        else:
            self._update_entries_onprem(conn, env)

    def _update_entries_saas(self, env: str) -> None:
        """Update KVM entries one by one for SaaS instances."""
        conn = self._get_env_connection(env)
        for entry in self.config.get('entry', []):
            key = entry.get('name')
            value = entry.get('value')
            if not key or not value:
                logger.warning(f"Skipping invalid entry in KVM {self.name}: missing key or value")
                continue

            # Check if entry exists
            url = f"keyvaluemaps/{self.name}/entries/{key}"
            response = conn.get(url)
            
            if response.status_code == 404:
                # Entry doesn't exist, create it
                logger.info(f"Creating new entry '{key}' in KVM {self.name}")
                create_url = f"keyvaluemaps/{self.name}/entries"
                create_payload = {
                    "name": key,
                    "value": value
                }
                create_response = conn.post(create_url, create_payload)
                if create_response.status_code not in [200, 201]:
                    logger.error(f"Failed to create entry '{key}' in KVM {self.name}: {create_response.text}")
                    continue
                logger.info(f"Successfully created entry '{key}' in KVM {self.name}")
            elif response.status_code == 200:
                # Entry exists, get old value and update it
                old_value = response.json().get('value', '')
                logger.info(f"Updating existing entry '{key}' in KVM {self.name}")
                logger.info(f"Old value: {old_value}")
                update_payload = {
                    "name": key,
                    "value": value
                }
                update_response = conn.post(url, update_payload)
                if update_response.status_code != 200:
                    logger.error(f"Failed to update entry '{key}' in KVM {self.name}: {update_response.text}")
                    continue
                logger.info(f"Successfully updated entry '{key}' in KVM {self.name}")
            else:
                logger.error(f"Failed to check entry '{key}' in KVM {self.name}: {response.text}")
                continue

    def _update_entries_onprem(self, conn: EnvConnection, env: str):
        """Update entire KVM payload for on-prem instance."""
        # Get existing entries
        response = conn.get(f"keyvaluemaps/{self.name}/entries")
        if response.status_code != 200:
            logger.error(f"Failed to get KVM entries: {response.text}")
            raise Exception(f"Failed to get KVM entries: {response.text}")
        
        # Log old values before update
        existing_entries = response.json()
        for entry in self.config.get('entry', []):
            key = entry.get('name')
            new_value = entry.get('value')
            old_entry = next((e for e in existing_entries if e.get('name') == key), None)
            if old_entry:
                old_value = old_entry.get('value', '')
                logger.info(f"Updating entry '{key}' in KVM {self.name}")
                logger.info(f"Old value: {old_value}")
            else:
                logger.info(f"Creating new entry '{key}' in KVM {self.name}")
        
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



