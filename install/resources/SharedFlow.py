from install.resources.EnvConfigResource import EnvConfigResource
from install.setup.Connection import Connection
from install.setup.Zipper import Zipper
from install.setup.logger_config import setup_logger, log_separator, log_file_separator
import os

logger = setup_logger('SharedFlow')

class SharedFlow(EnvConfigResource):
    def __init__(self, name: str, config: dict, connection: Connection, instance_type: str):
        super().__init__(name, config, connection)
        self.name = name
        self.config = config
        self.connection = connection
        self.instance_type = instance_type
        self.zipper = Zipper()
        log_file_separator(logger, f"Shared Flow '{name}'")
        logger.info(f"Starting to set up shared flow '{name}'")

    def apply(self):
        """Apply the shared flow configuration and handle deployment."""
        log_separator(logger, f"Setting up shared flow '{self.name}'")
        try:
            if self._exists():
                logger.info(f"Shared flow '{self.name}' exists, updating")
                result = self._update()
            else:
                logger.info(f"Shared flow '{self.name}' doesn't exist, creating")
                result = self._create()
            
            # Handle deployment if needed
            if result is not None and self.config.get("deploy", False):
                logger.info(f"Deploying shared flow '{self.name}'")
                return self._deploy()
            return result
            
        except Exception as e:
            logger.error(f"Problem setting up shared flow '{self.name}': {str(e)}")
            return None

    def _get_flow_path(self):
        """Get the full path to the shared flow's sharedflowbundle directory."""
        return os.path.join(self.instance_type, 'shared_flows', self.name, 'sharedflowbundle')

    def _exists(self):
        """Check if the shared flow exists."""
        endpoint = f"sharedflows/{self.name}"
        log_separator(logger, f"Checking if shared flow '{self.name}' already exists")
        try:
            response = self.connection.get(endpoint)
            if response is not None:
                logger.info(f"Found existing shared flow '{self.name}'")
            else:
                logger.info(f"Shared flow '{self.name}' does not exist yet")
            return response is not None
        except Exception as e:
            logger.error(f"Problem checking shared flow '{self.name}': {str(e)}")
            return False

    def _create(self):
        """Create the shared flow."""
        log_separator(logger, f"Creating new shared flow '{self.name}'")
        try:
            # Get the flow path and verify it exists
            flow_path = self._get_flow_path()
            if not os.path.isdir(flow_path):
                logger.error(f"Shared flow directory not found at {flow_path}")
                return None

            # Zip the flow directory
            zip_path = self.zipper.zip_flow(flow_path)
            logger.info(f"Successfully zipped shared flow directory: {flow_path}")

            # Import the flow
            with open(zip_path, 'rb') as zip_file:
                files = {'file': zip_file}
                response = self.connection.post_file(f"sharedflows?name={self.name}", files=files)

            # Clean up the zip file
            self.zipper.cleanup(zip_path)
            logger.info(f"Cleaned up temporary zip file")

            if response is None:
                logger.warning(f"Could not create shared flow '{self.name}'. Will try again next time.")
            else:
                logger.info(f"Successfully created shared flow '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"Problem creating shared flow '{self.name}': {str(e)}")
            return None

    def _update(self):
        """Update the shared flow."""
        # For Apigee, shared flow import is idempotent, so we use create
        return self._create()

    def _deploy(self):
        """Deploy the shared flow."""
        log_separator(logger, f"Deploying shared flow '{self.name}'")
        try:
            # Get the latest revision
            revisions = self.connection.get(f"sharedflows/{self.name}/revisions")
            if not revisions:
                logger.error(f"No revisions found for shared flow '{self.name}'")
                return None

            latest_revision = max(int(rev) for rev in revisions)
            logger.info(f"Latest revision for shared flow '{self.name}' is {latest_revision}")

            # Deploy the latest revision
            response = self.connection.post(f"sharedflows/{self.name}/revisions/{latest_revision}/deployments", 
                                         {"name": self.name})
            
            if response is None:
                logger.warning(f"Could not deploy shared flow '{self.name}'. Will try again next time.")
            else:
                logger.info(f"Successfully deployed shared flow '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"Problem deploying shared flow '{self.name}': {str(e)}")
            return None

    def _undeploy(self):
        """Undeploy the shared flow."""
        log_separator(logger, f"Undeploying shared flow '{self.name}'")
        try:
            response = self.connection.delete(f"sharedflows/{self.name}/deployments")
            if response is None:
                logger.warning(f"Could not undeploy shared flow '{self.name}'. Will try again next time.")
            else:
                logger.info(f"Successfully undeployed shared flow '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"Problem undeploying shared flow '{self.name}': {str(e)}")
            return None

    def _delete(self):
        """Delete the shared flow."""
        log_separator(logger, f"Deleting shared flow '{self.name}'")
        try:
            # First undeploy if deployed
            self._undeploy()
            
            # Then delete the flow
            response = self.connection.delete(f"sharedflows/{self.name}")
            if response is None:
                logger.warning(f"Could not delete shared flow '{self.name}'. Will try again next time.")
            else:
                logger.info(f"Successfully deleted shared flow '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"Problem deleting shared flow '{self.name}': {str(e)}")
            return None 