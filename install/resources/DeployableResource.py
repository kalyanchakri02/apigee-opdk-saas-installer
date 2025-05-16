from install.resources.OrgResource import OrgResource

class DeployableResource(OrgResource):
    """Base class for resources that can be deployed to environments."""

    def deploy(self, environment):
        """
        Deploy the resource to an environment.
        
        Args:
            environment: Target environment name
            
        Returns:
            bool: True if deployment was successful
        """
        raise NotImplementedError("Subclasses must implement deploy method")

    def undeploy(self, environment):
        """
        Undeploy the resource from an environment.
        
        Args:
            environment: Target environment name
            
        Returns:
            bool: True if undeployment was successful
        """
        raise NotImplementedError("Subclasses must implement undeploy method")

    def _make_env_request(self, method, endpoint, data=None, files=None):
        """
        Make an API request at the environment level.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data (optional)
            files: Files to upload (optional)
            
        Returns:
            Response from the API
        """
        return super()._make_request(method, endpoint, data, files, level='env') 