from install.resources.DeployableResource import DeployableResource
from install.setup.Connection import Connection
from install.setup.Zipper import Zipper
from install.setup.logger_config import setup_logger, log_separator, log_file_separator
import os

logger = setup_logger('SharedFlow')

class SharedFlow(DeployableResource):
    """Class to manage Shared Flows in Apigee."""

    def __init__(self, name: str, config: dict, connection: Connection, instance_type: str):
        """Initialize SharedFlow with name, configuration and connection details."""
        super().__init__(name, config, connection)
        self.name = name
        self.config = config
        self.connection = connection
        self.instance_type = instance_type
        self.zipper = Zipper()
        log_file_separator(logger, f"Shared Flow '{name}'")
        logger.info(f"Starting to set up shared flow '{name}'")

    def apply(self):
        """Apply the Shared Flow configuration."""
        if self._exists():
            self.logger.info(f"Shared Flow {self.name} already exists, updating")
            return self._update()
        else:
            self.logger.info(f"Shared Flow {self.name} does not exist, creating")
            return self._create()

    def _get_flow_path(self):
        """Get the full path to the shared flow's sharedflowbundle directory."""
        return os.path.join(self.instance_type, 'shared_flows', self.name, 'sharedflowbundle')

    def _exists(self):
        """Check if Shared Flow exists."""
        response = self._make_request('get', f'sharedflows/{self.name}')
        return response is not None and response.status_code == 200

    def _create(self):
        """Create a new Shared Flow."""
        # First, create the shared flow
        payload = {
            "name": self.name,
            "description": self.config.get('description', '')
        }
        response = self._make_request('post', 'sharedflows', data=payload)
        
        if not response or response.status_code != 201:
            self.logger.error(f"Failed to create Shared Flow {self.name}. Status: {response.status_code if response else 'No response'}")
            return False

        # Then, import the shared flow bundle
        bundle_path = self.config.get('bundlePath')
        if not bundle_path or not os.path.exists(bundle_path):
            self.logger.error(f"Bundle path not found: {bundle_path}")
            return False

        with open(bundle_path, 'rb') as bundle:
            files = {'file': (os.path.basename(bundle_path), bundle, 'application/zip')}
            response = self._make_request('post_file', f'sharedflows/{self.name}/revisions/1', files=files)

        if response and response.status_code in [200, 201]:
            self.logger.info(f"Successfully created and imported Shared Flow: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to import Shared Flow bundle for {self.name}. Status: {response.status_code if response else 'No response'}")
            return False

    def _update(self):
        """Update an existing Shared Flow."""
        # Import new revision
        bundle_path = self.config.get('bundlePath')
        if not bundle_path or not os.path.exists(bundle_path):
            self.logger.error(f"Bundle path not found: {bundle_path}")
            return False

        # Get current revision
        response = self._make_request('get', f'sharedflows/{self.name}/revisions')
        if not response or response.status_code != 200:
            self.logger.error(f"Failed to get current revision for {self.name}")
            return False

        current_revision = len(response.json())
        new_revision = current_revision + 1

        # Import new revision
        with open(bundle_path, 'rb') as bundle:
            files = {'file': (os.path.basename(bundle_path), bundle, 'application/zip')}
            response = self._make_request('post_file', f'sharedflows/{self.name}/revisions/{new_revision}', files=files)

        if response and response.status_code in [200, 201]:
            self.logger.info(f"Successfully updated Shared Flow: {self.name} to revision {new_revision}")
            return True
        else:
            self.logger.error(f"Failed to update Shared Flow {self.name}. Status: {response.status_code if response else 'No response'}")
            return False

    def delete(self):
        """Delete the Shared Flow."""
        response = self._make_request('delete', f'sharedflows/{self.name}')
        if response and response.status_code in [200, 204]:
            self.logger.info(f"Successfully deleted Shared Flow: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to delete Shared Flow {self.name}. Status: {response.status_code if response else 'No response'}")
            return False

    def deploy(self, environment):
        """Deploy the Shared Flow to an environment."""
        # Get latest revision
        response = self._make_request('get', f'sharedflows/{self.name}/revisions')
        if not response or response.status_code != 200:
            self.logger.error(f"Failed to get revisions for {self.name}")
            return False

        latest_revision = len(response.json())
        
        # Deploy the latest revision
        payload = {
            "name": self.name,
            "revision": str(latest_revision)
        }
        response = self._make_env_request('post', f'deployments', data=payload)
        
        if response and response.status_code in [200, 201]:
            self.logger.info(f"Successfully deployed Shared Flow {self.name} to {environment}")
            return True
        else:
            self.logger.error(f"Failed to deploy Shared Flow {self.name} to {environment}. Status: {response.status_code if response else 'No response'}")
            return False

    def undeploy(self, environment):
        """Undeploy the Shared Flow from an environment."""
        response = self._make_env_request('delete', f'deployments/{self.name}')
        if response and response.status_code in [200, 204]:
            self.logger.info(f"Successfully undeployed Shared Flow {self.name} from {environment}")
            return True
        else:
            self.logger.error(f"Failed to undeploy Shared Flow {self.name} from {environment}. Status: {response.status_code if response else 'No response'}")
            return False 