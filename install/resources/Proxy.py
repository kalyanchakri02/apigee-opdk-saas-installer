# resources/Proxy.py
from install.resources.EnvConfigResource import EnvConfigResource
from install.setup.Connection import Connection
from install.setup.Zipper import Zipper
from install.setup.logger_config import setup_logger, log_separator, log_file_separator
import os

logger = setup_logger('Proxy')

class Proxy(EnvConfigResource):
    def __init__(self, name: str, config: dict, connection: Connection, instance_type: str):
        super().__init__(name, config, connection)
        self.name = name
        self.config = config
        self.connection = connection
        self.instance_type = instance_type
        self.zipper = Zipper()
        log_file_separator(logger, f"API Proxy '{name}'")
        logger.info(f"Starting to set up API proxy '{name}'")

    def apply(self):
        """Apply the proxy configuration and handle deployment."""
        log_separator(logger, f"Setting up API proxy '{self.name}'")
        try:
            if self._exists():
                logger.info(f"API proxy '{self.name}' exists, updating")
                result = self._update()
            else:
                logger.info(f"API proxy '{self.name}' doesn't exist, creating")
                result = self._create()
            
            # Handle deployment if needed
            if result is not None and self.config.get("deploy", False):
                logger.info(f"Deploying API proxy '{self.name}'")
                return self._deploy()
            return result
            
        except Exception as e:
            logger.error(f"Problem setting up API proxy '{self.name}': {str(e)}")
            return None

    def _get_proxy_path(self):
        """Get the full path to the proxy's api_proxy directory."""
        return os.path.join(self.instance_type, 'api_proxies', self.name, 'api_proxy')

    def _exists(self):
        """Check if the proxy exists."""
        endpoint = f"apis/{self.name}"
        log_separator(logger, f"Checking if API proxy '{self.name}' already exists")
        try:
            response = self.connection.get(endpoint)
            if response is not None:
                logger.info(f"Found existing API proxy '{self.name}'")
            else:
                logger.info(f"API proxy '{self.name}' does not exist yet")
            return response is not None
        except Exception as e:
            logger.error(f"Problem checking API proxy '{self.name}': {str(e)}")
            return False

    def _create(self):
        """Create the proxy."""
        log_separator(logger, f"Creating new API proxy '{self.name}'")
        try:
            # Get the proxy path and verify it exists
            proxy_path = self._get_proxy_path()
            if not os.path.isdir(proxy_path):
                logger.error(f"Proxy directory not found at {proxy_path}")
                return None

            # Zip the proxy directory
            zip_path = self.zipper.zip_proxy(proxy_path)
            logger.info(f"Successfully zipped proxy directory: {proxy_path}")

            # Import the proxy
            with open(zip_path, 'rb') as zip_file:
                files = {'file': zip_file}
                response = self.connection.post_file(f"apis?name={self.name}", files=files)

            # Clean up the zip file
            self.zipper.cleanup(zip_path)
            logger.info(f"Cleaned up temporary zip file")

            if response is None:
                logger.warning(f"Could not create API proxy '{self.name}'. Will try again next time.")
            else:
                logger.info(f"Successfully created API proxy '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"Problem creating API proxy '{self.name}': {str(e)}")
            return None

    def _update(self):
        """Update the proxy."""
        # For Apigee, proxy import is idempotent, so we use create
        return self._create()

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
