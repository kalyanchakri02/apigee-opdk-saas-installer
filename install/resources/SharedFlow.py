from install.resources.DeployableResource import DeployableResource
from install.setup.Connection import OrgConnection, EnvConnection
from install.setup.Zipper import Zipper
from install.setup.logger_config import setup_logger, log_separator, log_file_separator
import os
import logging
from typing import List, Optional, Dict, Any

logger = setup_logger('SharedFlow')

class SharedFlow(DeployableResource):
    """Class to manage Shared Flows in Apigee."""

    def __init__(self, name: str, config: Dict[str, Any], org: str, host: str, auth_header: str, 
                 instance_type: str, environments: List[str], project_root: Optional[str] = None):
        """
        Initialize SharedFlow with name, configuration and connection details.
        
        Args:
            name: Name of the shared flow
            config: Shared flow configuration
            org: Apigee organization name
            host: Apigee host
            auth_header: Authorization header for API calls
            instance_type: Type of instance ('cloud' or 'on-prem')
            environments: List of environments to deploy to
            project_root: Root directory of the project (optional)
        """
        super().__init__(name, config)
        self.name = name
        self.config = config
        self.org = org
        self.host = host
        self.auth_header = auth_header
        self.instance_type = instance_type
        self.project_root = project_root or os.getcwd()
        self.zipper = Zipper()
        self.environments = environments
        self.logger = logging.getLogger(__name__)
        log_file_separator(logger, f"Shared Flow '{name}'")
        logger.info(f"Starting to set up shared flow '{name}'")

    def _get_org_connection(self) -> OrgConnection:
        """
        Create a new organization-level connection.
        
        Returns:
            OrgConnection: New organization-level connection
        """
        return OrgConnection(
            org=self.org,
            host=self.host,
            auth_header=self.auth_header
        )

    def _get_env_connection(self, env: str) -> EnvConnection:
        """
        Create a new environment-level connection.
        
        Args:
            env: Environment name
            
        Returns:
            EnvConnection: New environment-level connection
        """
        return EnvConnection(
            org=self.org,
            host=self.host,
            env=env,
            auth_header=self.auth_header
        )

    def _get_flow_path(self) -> str:
        """
        Get the full path to the shared flow's sharedflowbundle directory.
        
        Returns:
            str: Full path to the shared flow directory
        """
        instance_path = os.path.join(self.project_root, self.instance_type, 'shared_flows', self.name, 'sharedflowbundle')
        if not os.path.exists(instance_path):
            self.logger.warning(f"Shared flow path not found: {instance_path}")
        return instance_path

    def _exists(self, path: str) -> bool:
        """
        Check if Shared Flow exists.
        
        Args:
            path: API endpoint path
            
        Returns:
            bool: True if shared flow exists, False otherwise
        """
        try:
            connection = self._get_org_connection()
            response = self._make_request(connection, 'get', path)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Error checking if shared flow exists: {str(e)}")
            return False

    def _deploy_to_env(self, env: str) -> bool:
        """
        Deploy the Shared Flow to an environment.
        
        Args:
            env: Target environment name
            
        Returns:
            bool: True if deployment was successful
        """
        try:
            connection = self._get_org_connection()
            self.logger.info(f"Deploying to environment: {env}")
            
            # Get latest revision
            response = connection.get(f'sharedflows/{self.name}/revisions')
            if not response or response.status_code != 200:
                self.logger.error(f"Failed to get revisions for {self.name}")
                return False

            latest_revision = len(response.json())
            self.logger.info(f"Latest revision for Shared Flow '{self.name}' is {latest_revision}")
            env_connection = self._get_env_connection(env)
            
            # Deploy the latest revision
            endpoint = f'sharedflows/{self.name}/revisions/{latest_revision}/deployments?delay=5&override=true'
            response = env_connection.post(endpoint, data={}, content_type='application/x-www-form-urlencoded')
            
            if response and response.status_code in [200, 201]:
                self.logger.info(f"Successfully deployed Shared Flow {self.name} revision {latest_revision} to {env}")
                return True
            else:
                self.logger.error(f"Failed to deploy Shared Flow {self.name} to {env}. Status: {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.logger.error(f"Error deploying shared flow to {env}: {str(e)}")
            return False

    def apply(self) -> bool:
        """
        Apply the Shared Flow configuration and deploy to specified environments.
        
        Returns:
            bool: True if all operations were successful
        """
        try:
            # Get shared flow path and validate
            flow_path = self._get_flow_path()
            if not os.path.exists(flow_path):
                self.logger.error(f"Shared flow path not found: {flow_path}")
                return False

            # Zip the shared flow bundle
            zip_path = self.zipper.zip_bundle(flow_path, self.name)
            if not zip_path:
                self.logger.error("Failed to create shared flow bundle")
                return False

            # Create/Update shared flow with bundle
            connection = self._get_org_connection()
            with open(zip_path, 'rb') as bundle:
                files = {'file': (f'{self.name}.zip', bundle, 'application/zip')}
                response = connection.post_file(f'sharedflows?action=import&name={self.name}', files=files)

            if not response or response.status_code not in [200, 201]:
                self.logger.error(f"Failed to create/update Shared Flow {self.name}. Status: {response.status_code if response else 'No response'}")
                return False

            self.logger.info(f"Successfully created/updated Shared Flow: {self.name}")
            self.zipper.cleanup(zip_path)
            
            # Deploy to all specified environments
            if not self.environments:
                self.logger.warning(f"No environments specified for deployment of {self.name}")
                return True

            result = self.deploy(self.environments)

            self.zipper.cleanup_all()

            return result

        except Exception as e:
            self.logger.error(f"Error in shared flow apply: {str(e)}")
            return False

    def delete(self) -> bool:
        """
        Delete the shared flow and all its deployments.
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            # First undeploy from all environments
            for env in self.environments:
                try:
                    # Create new connection for this environment
                    env_connection = self._get_env_connection(env)
                    
                    # Get all deployments for this shared flow
                    response = env_connection.get(f'sharedflows/{self.name}/deployments')
                    if response and response.status_code == 200:
                        deployments = response.json()
                        for deployment in deployments:
                            # Undeploy each revision
                            rev = deployment.get('revision')
                            if rev:
                                env_connection.delete(f'sharedflows/{self.name}/revisions/{rev}/deployments')
                                self.logger.info(f"Undeployed revision {rev} from {env}")
                except Exception as e:
                    self.logger.warning(f"Error undeploying from {env}: {str(e)}")
            
            # Then delete the shared flow
            connection = self._get_org_connection()
            response = connection.delete(f'sharedflows/{self.name}')
            if response and response.status_code in [200, 204]:
                self.logger.info(f"Successfully deleted shared flow '{self.name}'")
                return True
            else:
                self.logger.error(f"Failed to delete shared flow '{self.name}'. Status: {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.logger.error(f"Error deleting shared flow: {str(e)}")
            return False 