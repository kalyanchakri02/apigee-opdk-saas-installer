from install.resources.OrgResource import OrgResource
from install.setup.logger_config import setup_logger, log_separator

logger = setup_logger('DeveloperApp')

class DeveloperApp(OrgResource):
    """Class to manage Developer Apps in Apigee."""

    def __init__(self, name, config, connection):
        """Initialize DeveloperApp with name, configuration and connection details."""
        super().__init__(name, config, connection)
        self.name = name
        self.config = config
        self.connection = connection
        logger.info(f"Initializing Developer App '{name}'")

    def _exists(self, developer_id):
        """Check if Developer App exists."""
        response = self._make_request('get', f'developers/{developer_id}/apps/{self.name}')
        return response is not None and response.status_code == 200

    def _create(self, developer_id):
        """Create a new Developer App."""
        payload = {
            "name": self.name,
            "apiProducts": self.config.get('apiProducts', []),
            "attributes": self.config.get('attributes', [])
        }
        response = self._make_request('post', f'developers/{developer_id}/apps', data=payload)
        
        if response and response.status_code == 201:
            self.logger.info(f"Successfully created Developer App: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to create Developer App {self.name}. Status: {response.status_code if response else 'No response'}")
            return False

    def _update(self, developer_id):
        """Update an existing Developer App."""
        payload = {
            "name": self.name,
            "apiProducts": self.config.get('apiProducts', []),
            "attributes": self.config.get('attributes', [])
        }
        response = self._make_request('put', f'developers/{developer_id}/apps/{self.name}', data=payload)
        
        if response and response.status_code in [200, 201]:
            self.logger.info(f"Successfully updated Developer App: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to update Developer App {self.name}. Status: {response.status_code if response else 'No response'}")
            return False

    def apply(self):
        """Apply the Developer App configuration."""
        developer_id = self.config.get('developerId')
        if not developer_id:
            self.logger.error("Developer ID is required")
            return False

        if self._exists(developer_id):
            self.logger.info(f"Developer App {self.name} already exists, updating")
            return self._update(developer_id)
        else:
            self.logger.info(f"Developer App {self.name} does not exist, creating")
            return self._create(developer_id)

    def delete(self):
        """Delete the Developer App."""
        developer_id = self.config.get('developerId')
        if not developer_id:
            self.logger.error("Developer ID is required")
            return False

        response = self._make_request('delete', f'developers/{developer_id}/apps/{self.name}')
        if response and response.status_code in [200, 204]:
            self.logger.info(f"Successfully deleted Developer App: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to delete Developer App {self.name}. Status: {response.status_code if response else 'No response'}")
            return False

    def _deploy(self):
        """Deploy the Developer App."""
        log_separator(logger, f"Deploying Developer App '{self.name}'")
        try:
            self.client.deploy_proxy(self.config["name"])
            logger.info(f"Successfully deployed Developer App '{self.name}'")
            return True
        except Exception as e:
            logger.error(f"Problem deploying Developer App '{self.name}': {str(e)}")
            return None

    def _undeploy(self):
        """Undeploy the Developer App."""
        log_separator(logger, f"Undeploying Developer App '{self.name}'")
        try:
            self.client.undeploy_proxy(self.config["name"])
            logger.info(f"Successfully undeployed Developer App '{self.name}'")
            return True
        except Exception as e:
            logger.error(f"Problem undeploying Developer App '{self.name}': {str(e)}")
            return None