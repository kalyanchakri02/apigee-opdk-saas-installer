from install.setup.Connection import EnvConnection
from install.setup.logger_config import setup_logger, log_file_separator
from install.resources.Resource import Resource
import logging

logger = setup_logger('TargetServer')

class TargetServer(Resource):
    """Class to manage Target Servers in Apigee."""

    def __init__(self, name: str, config: dict, org: str, host: str, auth_header: str):
        """
        Initialize TargetServer with name, configuration and connection details.
        
        Args:
            name: Name of the target server
            config: Target server configuration
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
        log_file_separator(logger, f"Target Server '{name}'")
        logger.info(f"Starting to set up target server '{name}'")

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
        Check if Target Server exists in the environment.
        
        Args:
            path: API endpoint path
            env: Environment name
            
        Returns:
            bool: True if target server exists, False otherwise
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
        Create a new Target Server in the environment.
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if creation was successful
        """
        connection = self._get_env_connection(env)
        response = self._make_request(connection, 'post', 'targetservers', data=self.config)
        if response.status_code == 201 or response.status_code == 409:
            self.logger.info(f"Successfully created/Target Server might have already exists: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to create Target Server {self.name}. Status: {response.status_code}")
            return False

    def apply(self, env: str) -> bool:
        """
        Apply the Target Server configuration.
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if configuration was applied successfully
        """
        if self._exists(f'targetservers/{self.name}', env):
            self.logger.info(f"Target Server {self.name} already exists, updating")
            return self._update(env)
        else:
            self.logger.info(f"Target Server {self.name} does not exist, creating")
            return self._create(env)

    def _update(self, env: str) -> bool:
        """
        Update an existing Target Server in the environment.
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if update was successful
        """
        connection = self._get_env_connection(env)
        response = self._make_request(connection, 'put', f'targetservers/{self.name}', data=self.config)
        if response.status_code == 200:
            self.logger.info(f"Successfully updated Target Server: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to update Target Server {self.name}. Status: {response.status_code}")
            return False
