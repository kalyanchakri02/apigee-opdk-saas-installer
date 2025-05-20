from install.setup.Connection import OrgConnection
from install.setup.logger_config import setup_logger, log_separator, log_file_separator
from install.resources.Resource import Resource
import logging

logger = setup_logger('DeveloperApp')

class DeveloperApp(Resource):
    """Class to manage Developer Apps in Apigee."""

    def __init__(self, name: str, config: dict, org: str, host: str, auth_header: str):
        """
        Initialize Developer App with name, configuration and connection details.
        
        Args:
            name: Name of the developer app
            config: App configuration
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
        log_file_separator(logger, f"Developer App '{name}'")
        logger.info(f"Starting to set up Developer app '{name}'")

    def _get_org_connection(self) -> OrgConnection:
        """
        Create a new organization-level connection.
        
        Returns:
            OrgConnection: New organization-level connection
        """
        return OrgConnection(
            org=self.org,
            host=self.host,
            auth_header=self.auth_header
        )

    def _exists(self, path: str) -> bool:
        """
        Check if Developer App exists in the organization.
        
        Args:
            path: API endpoint path
            
        Returns:
            bool: True if app exists, False otherwise
        """
        connection = self._get_org_connection()
        response = self._make_request(connection, 'get', path)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            raise RuntimeError(f"Unexpected response status {response.status_code}: {response.text}")

    def _create(self) -> bool:
        """
        Create a new Developer App in the organization.
        
        Returns:
            bool: True if creation was successful
        """
        connection = self._get_org_connection()
        # Use the provided config directly, just ensure name is set
        payload = self.config.copy()
        payload['name'] = self.name

        response = self._make_request(connection, 'post', 'apps', data=payload)
        
        if response.status_code == 201 or response.status_code == 409:
            self.logger.info(f"Successfully created/Developer App might have already exists: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to create Developer App {self.name}. Status: {response.status_code}")
            return False

    def _update(self) -> bool:
        """
        Update an existing Developer App in the organization.
        
        Returns:
            bool: True if update was successful
        """
        connection = self._get_org_connection()
        # Use the provided config directly, just ensure name is set
        payload = self.config.copy()
        payload['name'] = self.name

        response = self._make_request(connection, 'put', f'apps/{self.name}', data=payload)
        
        if response.status_code == 200:
            self.logger.info(f"Successfully updated Developer App: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to update Developer App {self.name}. Status: {response.status_code}")
            return False

    def apply(self) -> bool:
        """
        Apply the Developer App configuration.
        
        Returns:
            bool: True if configuration was applied successfully
        """
        if self._exists(f'apps/{self.name}'):
            self.logger.info(f"Developer App {self.name} already exists, updating")
            return self._update()
        else:
            self.logger.info(f"Developer App {self.name} does not exist, creating")
            return self._create()