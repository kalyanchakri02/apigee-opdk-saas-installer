from install.setup.Connection import Connection
from install.resources.EnvConfigResource import EnvConfigResource
from install.setup.logger_config import setup_logger, log_separator, log_file_separator
from install.resources.OrgResource import OrgResource

logger = setup_logger('Product')

class Product(OrgResource):
    """Class to manage API Products in Apigee."""

    def __init__(self, name: str, config: dict, connection: Connection):
        """Initialize Product with name, configuration and connection details."""
        super().__init__(name, config, connection)
        self.name = name
        self.config = config
        self.connection = connection
        log_file_separator(logger, f"API Product '{name}'")
        logger.info(f"Starting to set up API product '{name}'")

    def _exists(self):
        """Check if API Product exists."""
        response = self._make_request('get', f'apiproducts/{self.name}')
        return response is not None and response.status_code == 200

    def _create(self):
        """Create a new API Product."""
        payload = {
            "name": self.name,
            "displayName": self.config.get('displayName', self.name),
            "description": self.config.get('description', ''),
            "approvalType": self.config.get('approvalType', 'auto'),
            "attributes": self.config.get('attributes', []),
            "apiResources": self.config.get('apiResources', []),
            "environments": self.config.get('environments', []),
            "proxies": self.config.get('proxies', []),
            "quota": self.config.get('quota', ''),
            "quotaInterval": self.config.get('quotaInterval', ''),
            "quotaTimeUnit": self.config.get('quotaTimeUnit', '')
        }
        response = self._make_request('post', 'apiproducts', data=payload)
        
        if response and response.status_code == 201:
            self.logger.info(f"Successfully created API Product: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to create API Product {self.name}. Status: {response.status_code if response else 'No response'}")
            return False

    def _update(self):
        """Update an existing API Product."""
        payload = {
            "name": self.name,
            "displayName": self.config.get('displayName', self.name),
            "description": self.config.get('description', ''),
            "approvalType": self.config.get('approvalType', 'auto'),
            "attributes": self.config.get('attributes', []),
            "apiResources": self.config.get('apiResources', []),
            "environments": self.config.get('environments', []),
            "proxies": self.config.get('proxies', []),
            "quota": self.config.get('quota', ''),
            "quotaInterval": self.config.get('quotaInterval', ''),
            "quotaTimeUnit": self.config.get('quotaTimeUnit', '')
        }
        response = self._make_request('put', f'apiproducts/{self.name}', data=payload)
        
        if response and response.status_code in [200, 201]:
            self.logger.info(f"Successfully updated API Product: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to update API Product {self.name}. Status: {response.status_code if response else 'No response'}")
            return False

    def apply(self):
        """Apply the API Product configuration."""
        if self._exists():
            self.logger.info(f"API Product {self.name} already exists, updating")
            return self._update()
        else:
            self.logger.info(f"API Product {self.name} does not exist, creating")
            return self._create()

    def delete(self):
        """Delete the API Product."""
        response = self._make_request('delete', f'apiproducts/{self.name}')
        if response and response.status_code in [200, 204]:
            self.logger.info(f"Successfully deleted API Product: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to delete API Product {self.name}. Status: {response.status_code if response else 'No response'}")
            return False