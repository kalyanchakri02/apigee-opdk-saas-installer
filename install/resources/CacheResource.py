from install.resources.Resource import Resource
from install.setup.Connection import EnvConnection
import logging

class CacheResource(Resource):
    """Class to manage Cache Resources in Apigee."""

    def __init__(self, name: str, config: dict, org: str, host: str, auth_header: str):
        """
        Initialize Cache Resource with name, configuration and connection details.
        
        Args:
            name: Name of the cache
            config: Cache configuration
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
        Check if Cache exists in the environment.
        
        Args:
            path: API endpoint path
            env: Environment name
            
        Returns:
            bool: True if cache exists, False otherwise
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
        Create a new Cache in the environment.
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if creation was successful
        """
        connection = self._get_env_connection(env)
        # Use the provided config directly, just ensure name is set
        payload = self.config.copy()
        payload['name'] = self.name

        response = self._make_request(connection, 'post', 'caches', data=payload)
        
        if response.status_code == 201 or response.status_code == 409:
            self.logger.info(f"Successfully created/Cache might have already exists: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to create Cache {self.name}. Status: {response.status_code}")
            return False

    def _update(self, env: str) -> bool:
        """
        Update an existing Cache in the environment.
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if update was successful
        """
        connection = self._get_env_connection(env)
        # Use the provided config directly, just ensure name is set
        payload = self.config.copy()
        payload['name'] = self.name

        response = self._make_request(connection, 'put', f'caches/{self.name}', data=payload)
        
        if response.status_code == 200:
            self.logger.info(f"Successfully updated Cache: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to update Cache {self.name}. Status: {response.status_code}")
            return False

    def apply(self, env: str) -> bool:
        """
        Apply the Cache configuration.
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if configuration was applied successfully
        """
        if self._exists(f'caches/{self.name}', env):
            self.logger.info(f"Cache {self.name} already exists, updating")
            return self._update(env)
        else:
            self.logger.info(f"Cache {self.name} does not exist, creating")
            return self._create(env)
