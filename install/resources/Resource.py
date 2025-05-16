from abc import ABC, abstractmethod
import logging

class Resource(ABC):
    """Base class for all Apigee resources."""

    def __init__(self, name, config, connection):
        """
        Initialize the resource.
        
        Args:
            name: Name of the resource
            config: Resource configuration
            connection: Connection instance for API calls
        """
        self.name = name
        self.config = config
        self.connection = connection
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def apply(self):
        """Apply the resource configuration."""
        pass

    @abstractmethod
    def delete(self):
        """Delete the resource."""
        pass

    def _make_request(self, method, endpoint, data=None, files=None, level='env'):
        """
        Make an API request using the connection.
        
        Args:
            method: HTTP method ('get', 'post', 'put', 'delete')
            endpoint: API endpoint
            data: Request data (optional)
            files: Files to upload (optional)
            level: API level ('org', 'env', 'api')
            
        Returns:
            Response from the API
        """
        method_map = {
            'get': self.connection.get,
            'post': self.connection.post,
            'put': self.connection.put,
            'delete': self.connection.delete,
            'post_file': self.connection.post_file
        }

        if method not in method_map:
            raise ValueError(f"Unsupported HTTP method: {method}")

        func = method_map[method]
        
        if method == 'post_file':
            return func(endpoint, files=files, level=level)
        elif method in ['post', 'put']:
            return func(endpoint, data=data, level=level)
        else:
            return func(endpoint, level=level) 