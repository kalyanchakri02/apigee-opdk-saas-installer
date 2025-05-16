from install.setup.Connection import Connection
from install.setup.logger_config import setup_logger, log_file_separator
from install.resources.Resource import Resource
import logging

logger = setup_logger('TargetServer')

class TargetServer(Resource):
    """Class to manage Target Servers in Apigee."""

    def __init__(self, name: str, config: dict, connection: Connection):
        """Initialize TargetServer with name, configuration and connection details."""
        super().__init__(name, config, connection)
        self.name = name
        self.config = config
        self.connection = connection
        self.logger = logging.getLogger(__name__)
        log_file_separator(logger, f"Target Server '{name}'")
        logger.info(f"Starting to set up target server '{name}'")

    def _exists(self, path):
        """Check if Target Server exists in the environment."""
        response = self._make_request('get', path)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            raise RuntimeError(f"Unexpected response status {response.status_code}: {response.text}")

    def _create(self):
        """Create a new Target Server in the environment."""
        response = self._make_request('post', 'targetservers', data=self.config)
        if response.status_code == 201 or response.status_code == 409:
            self.logger.info(f"Successfully created/Target Server might have already exists: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to create Target Server {self.name}. Status: {response.status_code}")
            return False

    def _update(self):
        """Update an existing Target Server in the environment."""
        response = self._make_request('put', f'targetservers/{self.name}', data=self.config)
        if response.status_code in [200, 201]:
            self.logger.info(f"Successfully updated Target Server: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to update Target Server {self.name}. Status: {response.status_code}")
            return False

    def apply(self):
        """Apply the Target Server configuration."""
        if self._exists(f'targetservers/{self.name}'):
            self.logger.info(f"Target Server {self.name} already exists, updating")
            return self._update()
        else:
            self.logger.info(f"Target Server {self.name} does not exist, creating")
            return self._create()

    def delete(self):
        """Delete the Target Server from the environment."""
        response = self._make_request('delete', f'targetservers/{self.name}')
        if response.status_code in [200, 204]:
            self.logger.info(f"Successfully deleted Target Server: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to delete Target Server {self.name}. Status: {response.status_code}")
            return False
