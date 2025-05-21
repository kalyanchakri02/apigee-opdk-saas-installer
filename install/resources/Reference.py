from install.setup.Connection import OrgConnection, EnvConnection
from install.setup.logger_config import setup_logger, log_file_separator
from install.resources.Resource import Resource
import logging
from typing import Dict, Any, Optional

logger = setup_logger('Reference')

class Reference(Resource):
    """Class to manage API References in Apigee."""

    def __init__(self, name: str, config: Dict[str, Any], org: str, host: str, auth_header: str, env: Optional[str] = None):
        """
        Initialize Reference with name, configuration and connection details.
        
        Args:
            name: Name of the reference
            config: Reference configuration containing name, refers, and resourceType
            org: Apigee organization name
            host: Apigee host
            auth_header: Authorization header for API calls
            env: Environment name (optional, if None then org-level reference)
        """
        super().__init__(name, config)
        self.name = name
        self.config = config
        self.org = org
        self.host = host
        self.auth_header = auth_header
        self.env = env
        self.logger = logging.getLogger(__name__)
        log_file_separator(logger, f"API Reference '{name}'")
        logger.info(f"Starting to set up API reference '{name}' in {'environment ' + env if env else 'organization'}")

    def _get_connection(self):
        """
        Create a new connection based on whether this is an org or env reference.
        
        Returns:
            Connection: New connection instance
        """
        if self.env:
            return EnvConnection(
                org=self.org,
                env=self.env,
                host=self.host,
                auth_header=self.auth_header
            )
        else:
            return OrgConnection(
                org=self.org,
                host=self.host,
                auth_header=self.auth_header
            )

    def _exists(self, path: str) -> bool:
        """
        Check if Reference exists in the organization or environment.
        
        Args:
            path: API endpoint path
            
        Returns:
            bool: True if reference exists, False otherwise
        """
        connection = self._get_connection()
        response = self._make_request(connection, 'get', path)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            raise RuntimeError(f"Unexpected response status {response.status_code}: {response.text}")

    def _create(self) -> bool:
        """
        Create a new Reference in the organization or environment.
        
        Returns:
            bool: True if creation was successful
        """
        connection = self._get_connection()
        # Ensure required fields are present
        if not all(key in self.config for key in ['name', 'refers', 'resourceType']):
            self.logger.error(f"Missing required fields in reference configuration: {self.config}")
            return False

        response = self._make_request(connection, 'post', 'references', data=self.config)
        
        if response.status_code == 201 or response.status_code == 409:
            self.logger.info(f"Successfully created/Reference might have already exists: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to create Reference {self.name}. Status: {response.status_code}")
            return False

    def _update(self) -> bool:
        """
        Update an existing Reference in the organization or environment.
        
        Returns:
            bool: True if update was successful
        """
        connection = self._get_connection()
        # Ensure required fields are present
        if not all(key in self.config for key in ['name', 'refers', 'resourceType']):
            self.logger.error(f"Missing required fields in reference configuration: {self.config}")
            return False

        response = self._make_request(connection, 'put', f'references/{self.name}', data=self.config)
        
        if response.status_code == 200:
            self.logger.info(f"Successfully updated Reference: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to update Reference {self.name}. Status: {response.status_code}")
            return False

    def apply(self, env: Optional[str] = None) -> bool:
        """
        Apply the Reference configuration.
        
        Args:
            env: Environment name (optional, if None then org-level reference)
            
        Returns:
            bool: True if configuration was applied successfully
        """
        if env:
            self.env = env
            
        if self._exists(f'references/{self.name}'):
            self.logger.info(f"Reference {self.name} already exists, updating")
            return self._update()
        else:
            self.logger.info(f"Reference {self.name} does not exist, creating")
            return self._create()

    def delete(self) -> bool:
        """
        Delete the Reference.
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            connection = self._get_connection()
            response = connection.delete(f'references/{self.name}')
            if response and response.status_code in [200, 204]:
                self.logger.info(f"Successfully deleted Reference '{self.name}'")
                return True
            else:
                self.logger.error(f"Failed to delete Reference '{self.name}'. Status: {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.logger.error(f"Error deleting reference: {str(e)}")
            return False 