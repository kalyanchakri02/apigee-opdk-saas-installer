class URLBuilder:
    """Base class for URL builders."""
    
    def __init__(self, host, org, env=None):
        """
        Initialize the URL builder.
        
        Args:
            host: Apigee host
            org: Organization name
            env: Environment name (optional)
        """
        self.host = host
        self.org = org
        self.env = env
    
    def build_base_url(self):
        """Build the base URL."""
        raise NotImplementedError("Subclasses must implement build_base_url")
    
    def build_url(self, endpoint):
        """
        Build a complete URL with the given endpoint.
        
        Args:
            endpoint: API endpoint to append to the base URL
            
        Returns:
            str: The complete URL
        """
        base = self.build_base_url()
        # Handle cases where endpoint might start with a slash
        if endpoint and endpoint.startswith('/'):
            endpoint = endpoint[1:]
        return f"{base}/{endpoint}" if endpoint else base


class OrgLevelURLBuilder(URLBuilder):
    """Builder for organization-level URLs."""
    
    def build_base_url(self):
        """Build the base URL for organization-level APIs."""
        return f"https://{self.host}/v1/organizations/{self.org}"


class EnvLevelURLBuilder(URLBuilder):
    """Builder for environment-level URLs."""
    
    def build_base_url(self):
        """Build the base URL for environment-level APIs."""
        if not self.env:
            raise ValueError("Environment name is required for environment-level URLs")
        return f"https://{self.host}/v1/organizations/{self.org}/environments/{self.env}"


class APILevelURLBuilder(URLBuilder):
    """Builder for API-level URLs (not tied to org or env)."""
    
    def build_base_url(self):
        """Build the base URL for general API calls."""
        return f"https://{self.host}"


class URLFactory:
    """Factory class to create appropriate URL builders for Apigee API calls."""
    
    @staticmethod
    def create_builder(url_type, host, org, env=None):
        """
        Create a URL builder based on the specified type.
        
        Args:
            url_type: Type of URL builder to create ('org', 'env', or 'api')
            host: Apigee host
            org: Organization name
            env: Environment name (required for env-level URLs)
            
        Returns:
            URLBuilder: The appropriate URL builder instance
        """
        if url_type == 'org':
            return OrgLevelURLBuilder(host, org)
        elif url_type == 'env':
            return EnvLevelURLBuilder(host, org, env)
        elif url_type == 'api':
            return APILevelURLBuilder(host, org)
        else:
            raise ValueError(f"Unknown URL type: {url_type}") 