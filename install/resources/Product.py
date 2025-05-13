from install.setup.Connection import Connection
from install.resources.EnvConfigResource import EnvConfigResource
from install.setup.logger_config import setup_logger, log_separator, log_file_separator

logger = setup_logger('Product')

class Product(EnvConfigResource):
    def __init__(self, name: str, config: dict, connection: Connection):
        super().__init__(name, config, connection)
        self.name = name
        self.config = config
        self.connection = connection
        log_file_separator(logger, f"API Product '{name}'")
        logger.info(f"Starting to set up API product '{name}'")

    def exists(self) -> bool:
        endpoint = f"apiproducts/{self.name}"
        log_separator(logger, f"Checking if API product '{self.name}' already exists")
        try:
            response = self.connection.get(endpoint)
            if response is not None:
                logger.info(f"Found existing API product '{self.name}'")
            else:
                logger.info(f"API product '{self.name}' does not exist yet")
            return response is not None
        except Exception as e:
            logger.error(f"Problem checking API product '{self.name}': {str(e)}")
            return False

    def create(self):
        log_separator(logger, f"Creating new API product '{self.name}'")
        logger.info(f"Setting up API product details for '{self.name}':")
        logger.info(f"- Display Name: {self.config.get('displayName', 'not specified')}")
        logger.info(f"- Environments: {', '.join(self.config.get('environments', []))}")
        logger.info(f"- Proxies: {', '.join(self.config.get('proxies', []))}")
        logger.info(f"- Quota: {self.config.get('quota', 'not specified')} per {self.config.get('quotaTimeUnit', 'not specified')}")
        
        response = self.connection.post("apiproducts", self.config)
        if response is None:
            logger.warning(f"Could not create API product '{self.name}'. Will try again next time.")
        else:
            logger.info(f"Successfully created API product '{self.name}'")
        return response

    def update(self):
        log_separator(logger, f"Updating existing API product '{self.name}'")
        logger.info(f"Updating API product details for '{self.name}':")
        logger.info(f"- Display Name: {self.config.get('displayName', 'not specified')}")
        logger.info(f"- Environments: {', '.join(self.config.get('environments', []))}")
        logger.info(f"- Proxies: {', '.join(self.config.get('proxies', []))}")
        logger.info(f"- Quota: {self.config.get('quota', 'not specified')} per {self.config.get('quotaTimeUnit', 'not specified')}")
        
        response = self.connection.put(f"apiproducts/{self.name}", self.config)
        if response is None:
            logger.warning(f"Could not update API product '{self.name}'. Will try again next time.")
        else:
            logger.info(f"Successfully updated API product '{self.name}'")
        return response

    def apply(self):
        log_separator(logger, f"Setting up API product '{self.name}'")
        try:
            if self.exists():
                logger.info(f"API product '{self.name}' exists, updating its settings")
                return self.update()
            else:
                logger.info(f"API product '{self.name}' doesn't exist, creating it new")
                return self.create()
        except Exception as e:
            logger.error(f"Problem setting up API product '{self.name}': {str(e)}")
            return None

    def delete(self):
        log_separator(logger, f"Deleting API product '{self.name}'")
        try:
            response = self.connection.delete(f"apiproducts/{self.name}")
            if response is None:
                logger.warning(f"Could not delete API product '{self.name}'. Will try again next time.")
            else:
                logger.info(f"Successfully deleted API product '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"Problem deleting API product '{self.name}': {str(e)}")
            return None