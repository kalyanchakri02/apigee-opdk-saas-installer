from install.resources.Resource import Resource
from install.setup.Connection import EnvConnection
from install.setup.logger_config import setup_logger


class KVM(Resource):
    """Class to manage Key Value Maps (KVMs) in Apigee."""

    def __init__(self, name: str, config: dict, org: str, host: str, auth_header: str, instance_type: str = 'cloud'):
        """
        Initialize KVM with name, configuration and connection details.
        
        Args:
            name: Name of the KVM
            config: KVM configuration
            org: Apigee organization name
            host: Apigee host
            auth_header: Authorization header for API calls
            instance_type: Type of instance ('cloud' or 'onprem')
        """
        super().__init__(name, config)
        self.name = name
        self.config = config
        self.org = org
        self.host = host
        self.auth_header = auth_header
        self.instance_type = instance_type.lower()
        self.logger = setup_logger('KVM')
        self.logger.info(f"Initializing KVM: {name} for {self.instance_type} instance")
        self.logger.debug(f"KVM configuration: {config}")

    def _get_env_connection(self, env: str) -> EnvConnection:
        """
        Create a new environment-level connection.
        
        Args:
            env: Environment name
            
        Returns:
            EnvConnection: New environment-level connection
        """
        self.logger.debug(f"Creating environment connection for {env}")
        return EnvConnection(
            org=self.org,
            host=self.host,
            env=env,
            auth_header=self.auth_header
        )

    def _exists(self, path: str, env: str) -> bool:
        """
        Check if KVM or KVM entry exists in the environment.
        
        Args:
            path: API endpoint path
            env: Environment name
            
        Returns:
            bool: True if KVM exists, False otherwise
        """
        self.logger.info(f"Checking if KVM exists: {self.name} in environment {env}")
        connection = self._get_env_connection(env)
        response = self._make_request(connection, 'get', path)
        if response.status_code == 200:
            self.logger.info(f"KVM {self.name} exists in environment {env}")
            return True
        elif response.status_code == 404:
            self.logger.info(f"KVM {self.name} does not exist in environment {env}")
            return False
        else:
            error_msg = f"Unexpected response status {response.status_code}: {response.text}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _create(self, env: str) -> bool:
        """
        Create a new KVM in the environment.
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if creation was successful
        """
        self.logger.info(f"Creating KVM {self.name} in environment {env}")
        connection = self._get_env_connection(env)
        payload = {
            "name": self.name,
            "encrypted": self.config.get('encrypted', False)
        }
        self.logger.debug(f"KVM creation payload: {payload}")
        response = self._make_request(connection, 'post', 'keyvaluemaps', data=payload)
        
        if response.status_code == 201:
            self.logger.info(f"Successfully created KVM {self.name} in environment {env}")
            self._update_entries(env)
            return True
        elif response.status_code == 409:
            self.logger.info(f"KVM {self.name} already exists in environment {env}, proceeding with update")
            self._update_entries(env)
            return True
        else:
            error_msg = f"Failed to create KVM {self.name} in environment {env}. Status: {response.status_code}, Response: {response.text}"
            self.logger.error(error_msg)
            return False

    def _update(self, env: str) -> bool:
        """
        Update an existing KVM in the environment.
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if update was successful
        """
        self.logger.info(f"Updating KVM {self.name} in environment {env}")
        return self._update_entries(env)

    def _update_entries(self, env: str) -> bool:
        """
        Update KVM entries in the environment.
        For cloud: Updates each entry individually
        For on-prem: Updates all entries in a single call
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if update was successful
        """
        self.logger.info(f"Updating entries for KVM {self.name} in environment {env}")
        connection = self._get_env_connection(env)
        entries = self.config.get('entries', {})
        self.logger.debug(f"KVM entries to update: {entries}")

        if self.instance_type == 'onprem':
            return self._update_entries_onprem(connection, entries, env)
        else:
            return self._update_entries_cloud(connection, entries, env)

    def _update_entries_cloud(self, connection: EnvConnection, entries: dict, env: str) -> bool:
        """
        Update KVM entries individually (cloud instance).
        
        Args:
            connection: Environment connection
            entries: Dictionary of entries to update
            env: Environment name
            
        Returns:
            bool: True if all updates were successful
        """
        success = True
        for key, value in entries.items():
            self.logger.info(f"Updating KVM entry: {key}")
            payload = {
                "name": key,
                "value": value
            }
            response = self._make_request(connection, 'post', f'keyvaluemaps/{self.name}/entries', data=payload)
            
            if response.status_code in [200, 201]:
                self.logger.info(f"Successfully updated KVM entry {key}")
            elif response.status_code == 409:
                self.logger.info(f"KVM entry {key} already exists, skipping")
            else:
                error_msg = f"Failed to update KVM entry {key}. Status: {response.status_code}, Response: {response.text}"
                self.logger.error(error_msg)
                success = False

        if success:
            self.logger.info(f"Successfully updated all entries for KVM {self.name}")
        else:
            self.logger.warning(f"Some entries failed to update for KVM {self.name}")
        return success

    def _update_entries_onprem(self, connection: EnvConnection, entries: dict, env: str) -> bool:
        """
        Update all KVM entries in a single call (on-prem instance).
        
        Args:
            connection: Environment connection
            entries: Dictionary of entries to update
            env: Environment name
            
        Returns:
            bool: True if update was successful
        """
        self.logger.info(f"Updating all KVM entries in a single call for {self.name}")
        payload = {
            "entry": [
                {"name": key, "value": value}
                for key, value in entries.items()
            ]
        }
        self.logger.debug(f"KVM bulk update payload: {payload}")
        
        response = self._make_request(connection, 'post', f'keyvaluemaps/{self.name}/entries', data=payload)
        
        if response.status_code in [200, 201]:
            self.logger.info(f"Successfully updated all entries for KVM {self.name}")
            return True
        else:
            error_msg = f"Failed to update KVM entries. Status: {response.status_code}, Response: {response.text}"
            self.logger.error(error_msg)
            return False

    def apply(self, env: str) -> bool:
        """
        Apply the KVM configuration.
        
        Args:
            env: Environment name
            
        Returns:
            bool: True if configuration was applied successfully
        """
        self.logger.info(f"Applying KVM configuration for {self.name} in environment {env}")
        if self._exists(f'keyvaluemaps/{self.name}', env):
            self.logger.info(f"KVM {self.name} exists in environment {env}, proceeding with update")
            return self._update(env)
        else:
            self.logger.info(f"KVM {self.name} does not exist in environment {env}, proceeding with creation")
            return self._create(env)



