from install.resources.EnvConfigResource import EnvConfigResource
from install.setup.logger_config import setup_logger, log_separator

logger = setup_logger('DeveloperApp')

class DeveloperApp(EnvConfigResource):
    def __init__(self, name: str, config: dict, connection):
        super().__init__(name, config, connection)
        self.name = name
        self.config = config
        self.connection = connection
        logger.info(f"Initializing Developer App '{name}'")

    def apply(self):
        """Apply the Developer App configuration."""
        log_separator(logger, f"Setting up Developer App '{self.name}'")
        try:
            if self._exists():
                logger.info(f"Developer App '{self.name}' exists, updating")
                result = self._update()
            else:
                logger.info(f"Developer App '{self.name}' doesn't exist, creating")
                result = self._create()
            
            # Handle deployment if needed
            if result is not None and self.config.get("deploy", False):
                logger.info(f"Deploying Developer App '{self.name}'")
                return self._deploy()
            return result
            
        except Exception as e:
            logger.error(f"Problem setting up Developer App '{self.name}': {str(e)}")
            return None

    def _exists(self):
        """Check if the Developer App exists."""
        log_separator(logger, f"Checking if Developer App '{self.name}' exists")
        try:
            response = self.connection.get(f"apps/{self.name}")
            exists = response is not None
            logger.info(f"Developer App '{self.name}' exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Problem checking Developer App '{self.name}': {str(e)}")
            return False

    def _create(self):
        """Create the Developer App."""
        log_separator(logger, f"Creating Developer App '{self.name}'")
        try:
            response = self.connection.post("apps", self.config)
            if response is None:
                logger.warning(f"Could not create Developer App '{self.name}'. Will try again next time.")
            else:
                logger.info(f"Successfully created Developer App '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"Problem creating Developer App '{self.name}': {str(e)}")
            return None

    def _update(self):
        """Update the Developer App."""
        log_separator(logger, f"Updating Developer App '{self.name}'")
        try:
            response = self.connection.put(f"apps/{self.name}", self.config)
            if response is None:
                logger.warning(f"Could not update Developer App '{self.name}'. Will try again next time.")
            else:
                logger.info(f"Successfully updated Developer App '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"Problem updating Developer App '{self.name}': {str(e)}")
            return None

    def _delete(self):
        """Delete the Developer App."""
        log_separator(logger, f"Deleting Developer App '{self.name}'")
        try:
            response = self.connection.delete(f"apps/{self.name}")
            if response is None:
                logger.warning(f"Could not delete Developer App '{self.name}'. Will try again next time.")
            else:
                logger.info(f"Successfully deleted Developer App '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"Problem deleting Developer App '{self.name}': {str(e)}")
            return None

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