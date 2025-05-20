from install.resources.Resource import Resource
from install.setup.Connection import EnvConnection
import logging


class KVM(Resource):
    """Class to manage Key Value Maps (KVMs) in Apigee."""

    def __init__(self, name: str, config: dict, org: str, host: str, auth_header: str):
        """
        Initialize KVM with name, configuration and connection details.
        
        Args:
            name: Name of the KVM
            config: KVM configuration
            org: Apigee organization name
            host: Apigee host
            auth_header: Authorization header for API calls
        """
        super().__init__(name, config)
        self.name = name
        self.config = config
        self.org = org
        self.host = host
        self.auth_header = auth_header
        self.logger = logging.getLogger(__name__)

    def _get_env_connection(self, env: str) -> EnvConnection:
        """
        Create a new environment-level connection.
        
        Args:
            env: Environment name
            
        Returns:
            EnvConnection: New environment-level connection
        """
        return EnvConnection(
            org=self.org,
            host=self.host,
            env=env,
            auth_header=self.auth_header
        )

    def _exists(self, path: str, env: str) -> bool:
        """
        Check if KVM or KVM entry exists in the environment.
        
        Args:
            path: API endpoint path
            env: Environment name
            
        Returns:
            bool: True if KVM exists, False otherwise
        """
        connection = self._get_env_connection(env)
        response = self._make_request(connection, 'get', path)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            raise RuntimeError(f"Unexpected response status {response.status_code}: {response.text}")

    def _create(self, env: str) -> bool:
        """
        Create a new KVM in the environment.
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if creation was successful
        """
        connection = self._get_env_connection(env)
        payload = {
            "name": self.name,
            "encrypted": self.config.get('encrypted', False)
        }
        response = self._make_request(connection, 'post', 'keyvaluemaps', data=payload)
        
        if response.status_code == 201 or response.status_code == 409:
            self.logger.info(f"Successfully created KVM/KVM might have already exists: {self.name}")
            self._update_entries(env)
            return True
        else:
            self.logger.error(f"Failed to create KVM {self.name}. Status: {response.status_code}")
            return False

    def _update(self, env: str) -> bool:
        """
        Update an existing KVM in the environment.
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if update was successful
        """
        return self._update_entries(env)

    def _update_entries(self, env: str) -> bool:
        """
        Update KVM entries in the environment.
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if update was successful
        """
        connection = self._get_env_connection(env)
        entries = self.config.get('entries', {})
        success = True

        for key, value in entries.items():
            payload = {
                "name": key,
                "value": value
            }
            response = self._make_request(connection, 'post', f'keyvaluemaps/{self.name}/entries', data=payload)
            
            if response.status_code not in [200, 201, 409]:
                self.logger.error(f"Failed to update KVM entry {key}. Status: {response.status_code}")
                success = False

        return success

    def apply(self, env: str) -> bool:
        """
        Apply the KVM configuration.
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if configuration was applied successfully
        """
        if self._exists(f'keyvaluemaps/{self.name}', env):
            self.logger.info(f"KVM {self.name} already exists, updating")
            return self._update(env)
        else:
            self.logger.info(f"KVM {self.name} does not exist, creating")
            return self._create(env)



