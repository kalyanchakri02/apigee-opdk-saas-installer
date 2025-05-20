from install.setup.Connection import OrgConnection
from install.setup.logger_config import setup_logger, log_separator, log_file_separator
from install.resources.Resource import Resource
import logging

logger = setup_logger('Product')

class Product(Resource):
    """Class to manage API Products in Apigee."""

    def __init__(self, name: str, config: dict, org: str, host: str, auth_header: str):
        """
        Initialize API Product with name, configuration and connection details.
        
        Args:
            name: Name of the API product
            config: Product configuration
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
        log_file_separator(logger, f"API Product '{name}'")
        logger.info(f"Starting to set up API product '{name}'")

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
        Check if API Product exists in the organization.
        
        Args:
            path: API endpoint path
            
        Returns:
            bool: True if product exists, False otherwise
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
        Create a new API Product in the organization.
        
        Returns:
            bool: True if creation was successful
        """
        connection = self._get_org_connection()
        # Use the provided config directly, just ensure name is set
        payload = self.config.copy()
        payload['name'] = self.name

        response = self._make_request(connection, 'post', 'apiproducts', data=payload)
        
        if response.status_code == 201 or response.status_code == 409:
            self.logger.info(f"Successfully created/API Product might have already exists: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to create API Product {self.name}. Status: {response.status_code}")
            return False

    def _update(self) -> bool:
        """
        Update an existing API Product in the organization.
        
        Returns:
            bool: True if update was successful
        """
        connection = self._get_org_connection()
        # Use the provided config directly, just ensure name is set
        payload = self.config.copy()
        payload['name'] = self.name

        response = self._make_request(connection, 'put', f'apiproducts/{self.name}', data=payload)
        
        if response.status_code == 200:
            self.logger.info(f"Successfully updated API Product: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to update API Product {self.name}. Status: {response.status_code}")
            return False

    def apply(self) -> bool:
        """
        Apply the API Product configuration.
        
        Returns:
            bool: True if configuration was applied successfully
        """
        if self._exists(f'apiproducts/{self.name}'):
            self.logger.info(f"API Product {self.name} already exists, updating")
            return self._update()
        else:
            self.logger.info(f"API Product {self.name} does not exist, creating")
            return self._create()