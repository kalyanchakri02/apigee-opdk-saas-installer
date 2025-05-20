from abc import ABC, abstractmethod
import logging
from install.setup.Connection import BaseConnection

class Resource(ABC):
    """Base class for all Apigee resources."""

    def __init__(self, name, config):
        """
        Initialize the resource.
        
        Args:
            name: Name of the resource
            config: Resource configuration
        """
        self.name = name
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def apply(self):
        """Apply the resource configuration."""
        pass

    def _make_request(self, connection: BaseConnection, method: str, endpoint: str, data: dict = None, files: dict = None):
        """
        Make an API request using the connection.
        
        Args:
            connection: Connection instance for API calls
            method: HTTP method ('get', 'post', 'put', 'delete')
            endpoint: API endpoint
            data: Request data (optional)
            files: Files to upload (optional)
            
        Returns:
            Response from the API
        """
        method_map = {
            'get': connection.get,
            'post': connection.post,
            'put': connection.put,
            'delete': connection.delete,
            'post_file': connection.post_file
        }

        if method not in method_map:
            raise ValueError(f"Unsupported HTTP method: {method}")

        func = method_map[method]
        
        if method == 'post_file':
            return func(endpoint, files=files)
        elif method in ['post', 'put']:
            return func(endpoint, data=data)
        else:
            return func(endpoint) 