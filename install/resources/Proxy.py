# resources/Proxy.py
from install.resources.DeployableResource import DeployableResource
from install.setup.Connection import Connection
from install.setup.Zipper import Zipper
from install.setup.logger_config import setup_logger, log_separator, log_file_separator
import os

logger = setup_logger('Proxy')

class Proxy(DeployableResource):
    """Class to manage API Proxies in Apigee."""

    def __init__(self, name: str, config: dict, connection: Connection, instance_type: str):
        """Initialize Proxy with name, configuration and connection details."""
        super().__init__(name, config, connection)
        self.name = name
        self.config = config
        self.connection = connection
        self.instance_type = instance_type
        self.zipper = Zipper()
        log_file_separator(logger, f"API Proxy '{name}'")
        logger.info(f"Starting to set up API proxy '{name}'")

    def _exists(self):
        """Check if API Proxy exists."""
        response = self._make_request('get', f'apis/{self.name}')
        return response is not None and response.status_code == 200

    def _create(self):
        """Create a new API Proxy."""
        # First, create the proxy
        payload = {
            "name": self.name,
            "basepaths": self.config.get('basepaths', []),
            "description": self.config.get('description', '')
        }
        response = self._make_request('post', 'apis', data=payload)
        
        if not response or response.status_code != 201:
            self.logger.error(f"Failed to create API Proxy {self.name}. Status: {response.status_code if response else 'No response'}")
            return False

        # Then, import the proxy bundle
        bundle_path = self.config.get('bundlePath')
        if not bundle_path or not os.path.exists(bundle_path):
            self.logger.error(f"Bundle path not found: {bundle_path}")
            return False

        with open(bundle_path, 'rb') as bundle:
            files = {'file': (os.path.basename(bundle_path), bundle, 'application/zip')}
            response = self._make_request('post_file', f'apis/{self.name}/revisions/1', files=files)

        if response and response.status_code in [200, 201]:
            self.logger.info(f"Successfully created and imported API Proxy: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to import API Proxy bundle for {self.name}. Status: {response.status_code if response else 'No response'}")
            return False

    def _update(self):
        """Update an existing API Proxy."""
        # Import new revision
        bundle_path = self.config.get('bundlePath')
        if not bundle_path or not os.path.exists(bundle_path):
            self.logger.error(f"Bundle path not found: {bundle_path}")
            return False

        # Get current revision
        response = self._make_request('get', f'apis/{self.name}/revisions')
        if not response or response.status_code != 200:
            self.logger.error(f"Failed to get current revision for {self.name}")
            return False

        current_revision = len(response.json())
        new_revision = current_revision + 1

        # Import new revision
        with open(bundle_path, 'rb') as bundle:
            files = {'file': (os.path.basename(bundle_path), bundle, 'application/zip')}
            response = self._make_request('post_file', f'apis/{self.name}/revisions/{new_revision}', files=files)

        if response and response.status_code in [200, 201]:
            self.logger.info(f"Successfully updated API Proxy: {self.name} to revision {new_revision}")
            return True
        else:
            self.logger.error(f"Failed to update API Proxy {self.name}. Status: {response.status_code if response else 'No response'}")
            return False

    def apply(self):
        """Apply the API Proxy configuration."""
        if self._exists():
            self.logger.info(f"API Proxy {self.name} already exists, updating")
            return self._update()
        else:
            self.logger.info(f"API Proxy {self.name} does not exist, creating")
            return self._create()

    def delete(self):
        """Delete the API Proxy."""
        response = self._make_request('delete', f'apis/{self.name}')
        if response and response.status_code in [200, 204]:
            self.logger.info(f"Successfully deleted API Proxy: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to delete API Proxy {self.name}. Status: {response.status_code if response else 'No response'}")
            return False

    def deploy(self, environment):
        """Deploy the API Proxy to an environment."""
        # Get latest revision
        response = self._make_request('get', f'apis/{self.name}/revisions')
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
            self.logger.info(f"Successfully deployed API Proxy {self.name} to {environment}")
            return True
        else:
            self.logger.error(f"Failed to deploy API Proxy {self.name} to {environment}. Status: {response.status_code if response else 'No response'}")
            return False

    def undeploy(self, environment):
        """Undeploy the API Proxy from an environment."""
        response = self._make_env_request('delete', f'deployments/{self.name}')
        if response and response.status_code in [200, 204]:
            self.logger.info(f"Successfully undeployed API Proxy {self.name} from {environment}")
            return True
        else:
            self.logger.error(f"Failed to undeploy API Proxy {self.name} from {environment}. Status: {response.status_code if response else 'No response'}")
            return False

    def _get_proxy_path(self):
        """Get the full path to the proxy's api_proxy directory."""
        return os.path.join(self.instance_type, 'api_proxies', self.name, 'api_proxy')

    def _deploy(self):
        """Deploy the proxy."""
        log_separator(logger, f"Deploying API proxy '{self.name}'")
        try:
            # Get the latest revision
            revisions = self.connection.get(f"apis/{self.name}/revisions")
            if not revisions:
                logger.error(f"No revisions found for API proxy '{self.name}'")
                return None

            latest_revision = max(int(rev) for rev in revisions)
            logger.info(f"Latest revision for API proxy '{self.name}' is {latest_revision}")

            # Deploy the latest revision
            response = self.connection.post(f"apis/{self.name}/revisions/{latest_revision}/deployments", 
                                         {"name": self.name})
            
            if response is None:
                logger.warning(f"Could not deploy API proxy '{self.name}'. Will try again next time.")
            else:
                logger.info(f"Successfully deployed API proxy '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"Problem deploying API proxy '{self.name}': {str(e)}")
            return None

    def _undeploy(self):
        """Undeploy the proxy."""
        log_separator(logger, f"Undeploying API proxy '{self.name}'")
        try:
            response = self.connection.delete(f"apis/{self.name}/deployments")
            if response is None:
                logger.warning(f"Could not undeploy API proxy '{self.name}'. Will try again next time.")
            else:
                logger.info(f"Successfully undeployed API proxy '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"Problem undeploying API proxy '{self.name}': {str(e)}")
            return None

    def _delete(self):
        """Delete the proxy."""
        log_separator(logger, f"Deleting API proxy '{self.name}'")
        try:
            # First undeploy if deployed
            self._undeploy()
            
            # Then delete the proxy
            response = self.connection.delete(f"apis/{self.name}")
            if response is None:
                logger.warning(f"Could not delete API proxy '{self.name}'. Will try again next time.")
            else:
                logger.info(f"Successfully deleted API proxy '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"Problem deleting API proxy '{self.name}': {str(e)}")
            return None
