from install.resources.Resource import Resource
from install.setup.Connection import BaseConnection
from typing import List

class DeployableResource(Resource):
    """Base class for resources that can be deployed to environments."""

    def deploy(self, environments: List[str], override: bool = True, delay: int = 3) -> bool:
        """
        Deploy the resource to multiple environments.
        
        Args:
            environments: List of environments to deploy to
            override: Whether to override existing deployments (default: True)
            delay: Delay in seconds between deployments (default: 3)
            
        Returns:
            bool: True if all deployments were successful
        """
        if not environments:
            self.logger.warning("No environments specified for deployment")
            return True

        self.logger.info(f"Deploying to environments: {environments}")
        deployment_success = True
        
        for env in environments:
            try:
                if not self._deploy_to_env(env):
                    deployment_success = False
                    self.logger.error(f"Failed to deploy to environment: {env}")
            except Exception as e:
                deployment_success = False
                self.logger.error(f"Error deploying to environment {env}: {str(e)}")
        
        return deployment_success

    def _deploy_to_env(self, env: str) -> bool:
        """
        Deploy the resource to a specific environment.
        Must be implemented by subclasses.
        
        Args:
            env: Target environment name
            override: Whether to override existing deployments (default: True)
            delay: Delay in seconds between deployments (default: 3)
            
        Returns:
            bool: True if deployment was successful
        """
        raise NotImplementedError("Subclasses must implement _deploy_to_env method")

    def _make_env_request(self, connection: BaseConnection, method: str, endpoint: str, data: dict = None, files: dict = None, env: str = None):
        """
        Make an API request at the environment level.
        
        Args:
            connection: Connection instance for API calls
            method: HTTP method
            endpoint: API endpoint
            data: Request data (optional)
            files: Files to upload (optional)
            env: Environment name (optional)
            
        Returns:
            Response from the API
        """
        if env:
            # If environment is specified in the endpoint, use it
            if 'environments/' in endpoint:
                return super()._make_request(connection, method, endpoint, data, files)
            # Otherwise, prepend the environment to the endpoint
            endpoint = f'environments/{env}/{endpoint}'
        return super()._make_request(connection, method, endpoint, data, files) 