from install.setup.Connection import Connection
from install.resources.EnvConfigResource import EnvConfigResource
from install.setup.logger_config import setup_logger, log_separator, log_file_separator

logger = setup_logger('TargetServer')

class TargetServer(EnvConfigResource):

    def __init__(self, name: str, config: dict, connection: Connection):
        super().__init__(name, config, connection)
        self.name = name
        self.config = config
        self.connection = connection
        log_file_separator(logger, f"Target Server '{name}'")
        logger.info(f"Starting to set up target server '{name}'")

    def exists(self) -> bool:
        endpoint = f"targetservers/{self.name}"
        log_separator(logger, f"Checking if target server '{self.name}' already exists")
        try:
            response = self.connection.get(endpoint)
            if response is not None:
                logger.info(f"Found existing target server '{self.name}'")
            else:
                logger.info(f"Target server '{self.name}' does not exist yet")
            return response is not None
        except Exception as e:
            logger.error(f"Problem checking target server '{self.name}': {str(e)}")
            return False

    def create(self):
        log_separator(logger, f"Creating new target server '{self.name}'")
        logger.info(f"Setting up connection details for '{self.name}':")
        logger.info(f"- Host: {self.config.get('host', 'not specified')}")
        logger.info(f"- Port: {self.config.get('port', 'not specified')}")
        logger.info(f"- SSL Enabled: {self.config.get('sSLInfo', {}).get('enabled', 'not specified')}")
        
        response = self.connection.post("targetservers", self.config)
        if response is None:
            logger.warning(f"Could not create target server '{self.name}'. Will try again next time.")
        else:
            logger.info(f"Successfully created target server '{self.name}'")
        return response

    def update(self):
        log_separator(logger, f"Updating existing target server '{self.name}'")
        logger.info(f"Updating connection details for '{self.name}':")
        logger.info(f"- Host: {self.config.get('host', 'not specified')}")
        logger.info(f"- Port: {self.config.get('port', 'not specified')}")
        logger.info(f"- SSL Enabled: {self.config.get('sSLInfo', {}).get('enabled', 'not specified')}")
        
        response = self.connection.put(f"targetservers/{self.name}", self.config)
        if response is None:
            logger.warning(f"Could not update target server '{self.name}'. Will try again next time.")
        else:
            logger.info(f"Successfully updated target server '{self.name}'")
        return response

    def apply(self):
        log_separator(logger, f"Setting up target server '{self.name}'")
        try:
            if self.exists():
                logger.info(f"Target server '{self.name}' exists, updating its settings")
                return self.update()
            else:
                logger.info(f"Target server '{self.name}' doesn't exist, creating it new")
                return self.create()
        except Exception as e:
            logger.error(f"Problem setting up target server '{self.name}': {str(e)}")
            return None
