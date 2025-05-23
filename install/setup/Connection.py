# core/connection.py
import requests
from install.setup.logger_config import setup_logger
from install.setup.URLFactory import URLFactory
from abc import ABC, abstractmethod

logger = setup_logger('Connection')

class BaseConnection(ABC):
    """Base class for all Apigee connections."""
    
    def __init__(self, org: str, host: str, auth_header: str):
        """
        Initialize the base connection.
        
        Args:
            org: Apigee organization name
            host: Apigee host
            auth_header: Authorization header
        """
        self.org = org
        self.host = host
        self.headers = {
            "Authorization": auth_header
        }
        self.url_factory = URLFactory()
        logger.debug(f"Setting up connection to Apigee:")
        logger.debug(f"- Organization: {org}")
        logger.debug(f"- Host: {host}")

    def get(self, endpoint: str, content_type: str = 'application/json') -> requests.Response:
        """
        Perform a GET request.
        
        Args:
            endpoint: API endpoint
            content_type: Content type header (default: application/json)
            
        Returns:
            Response from the API
        """
        url = self._build_url(endpoint)
        headers = self._get_headers(content_type)
        logger.info(f"GET request to {url}")
        response = requests.get(url, headers=headers, verify=False)
        self._log_response(response)
        return response

    def post(self, endpoint: str, data: dict = None, content_type: str = 'application/json') -> requests.Response:
        """
        Perform a POST request.
        
        Args:
            endpoint: API endpoint
            data: Request data
            content_type: Content type header (default: application/json)
            
        Returns:
            Response from the API
        """
        url = self._build_url(endpoint)
        headers = self._get_headers(content_type)
        logger.info(f"POST request to {url}")
        response = requests.post(url, headers=headers, json=data, verify=False)
        self._log_response(response)
        return response
    
    def post_file(self, endpoint: str, files: dict, content_type: str = None) -> requests.Response:
        """
        Perform a POST request with file upload.
        
        Args:
            endpoint: API endpoint
            files: Files to upload
            content_type: Content type header (default: None for multipart/form-data)
            
        Returns:
            Response from the API
        """
        url = self._build_url(endpoint)
        headers = self._get_headers(content_type)
        logger.info(f"POST file request to {url}")
        response = requests.post(url, headers=headers, files=files, verify=False)
        self._log_response(response)
        return response

    def put(self, endpoint: str, data: dict = None, content_type: str = 'application/json') -> requests.Response:
        """
        Perform a PUT request.
        
        Args:
            endpoint: API endpoint
            data: Request data
            content_type: Content type header (default: application/json)
            
        Returns:
            Response from the API
        """
        url = self._build_url(endpoint)
        headers = self._get_headers(content_type)
        logger.info(f"PUT request to {url}")
        response = requests.put(url, headers=headers, json=data, verify=False)
        self._log_response(response)
        return response

    def delete(self, endpoint: str, content_type: str = 'application/json') -> requests.Response:
        """
        Perform a DELETE request.
        
        Args:
            endpoint: API endpoint
            content_type: Content type header (default: application/json)
            
        Returns:
            Response from the API
        """
        url = self._build_url(endpoint)
        headers = self._get_headers(content_type)
        logger.info(f"DELETE request to {url}")
        response = requests.delete(url, headers=headers, verify=False)
        self._log_response(response)
        return response

    def _get_headers(self, content_type: str = None) -> dict:
        """
        Get headers for the request.
        
        Args:
            content_type: Content type header (optional)
            
        Returns:
            dict: Headers for the request
        """
        headers = self.headers.copy()
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    @abstractmethod
    def _build_url(self, endpoint: str) -> str:
        """
        Build the complete URL for the request.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Complete URL string
        """
        pass

    def _log_response(self, response: requests.Response):
        """
        Log the response from an API request.
        
        Args:
            response: Response object from requests
        """
        if 200 <= response.status_code < 300:
            logger.info(f"Response status: {response.status_code}")
            try:
                if response.text:
                    logger.debug(f"Response body: {response.text}")
            except Exception as e:
                logger.warning(f"Could not log response body: {str(e)}")
        else:
            logger.error(f"Request failed with status {response.status_code}")
            try:
                if response.text:
                    logger.error(f"Error response: {response.text}")
            except Exception as e:
                logger.warning(f"Could not log error response: {str(e)}")

class OrgConnection(BaseConnection):
    """Connection for organization-level API operations."""
    
    def __init__(self, org: str, host: str, auth_header: str):
        """
        Initialize organization-level connection.
        
        Args:
            org: Apigee organization name
            host: Apigee host
            auth_header: Authorization header
        """
        super().__init__(org, host, auth_header)
        self.org_url_builder = self.url_factory.create_builder('org', host, org)
        logger.debug("Initialized organization-level connection")

    def _build_url(self, endpoint: str) -> str:
        """
        Build organization-level URL.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Complete URL string
        """
        return self.org_url_builder.build_url(endpoint)

class EnvConnection(BaseConnection):
    """Connection for environment-level API operations."""
    
    def __init__(self, org: str, host: str, env: str, auth_header: str):
        """
        Initialize environment-level connection.
        
        Args:
            org: Apigee organization name
            host: Apigee host
            env: Environment name
            auth_header: Authorization header
        """
        super().__init__(org, host, auth_header)
        self.env = env
        self.env_url_builder = self.url_factory.create_builder('env', host, org, env)
        logger.info(f"Initialized environment-level connection for {env}")

    def _build_url(self, endpoint: str) -> str:
        """
        Build environment-level URL.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Complete URL string
        """
        return self.env_url_builder.build_url(endpoint)
