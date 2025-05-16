# core/connection.py
import requests
from install.setup.logger_config import setup_logger, log_separator
from install.setup.URLFactory import URLFactory

logger = setup_logger('Connection')

class Connection:
    def __init__(self, org, host, env, auth_header):
        """
        Initializes the connection with required parameters.
        :param org: Apigee organization name.
        :param env: Apigee environment name.
        :param auth_header: Complete authorization header (e.g. "Basic base64encoded" or "Bearer token")
        """
        self.org = org
        self.env = env
        self.host = host
        
        # Create URL builders for different API levels
        self.url_factory = URLFactory()
        self.org_url_builder = self.url_factory.create_builder('org', host, org)
        self.env_url_builder = self.url_factory.create_builder('env', host, org, env)
        self.api_url_builder = self.url_factory.create_builder('api', host, org)
        
        # Headers for API requests
        self.headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }
        
        logger.info(f"Setting up connection to Apigee:")
        logger.info(f"- Organization: {org}")
        logger.info(f"- Environment: {env}")
        logger.info(f"- Host: {host}")

    def get(self, endpoint, level='env'):
        """
        Perform a GET request to the given endpoint.
        :param endpoint: The API endpoint to send the request to.
        :param level: API level ('org', 'env', or 'api')
        :return: Response from the API.
        """
        url = self._build_url(endpoint, level)
        logger.info(f"GET request to {url}")
        response = requests.get(url, headers=self.headers)
        self._log_response(response)
        return response

    def post(self, endpoint, data, level='env'):
        """
        Perform a POST request to the given endpoint.
        :param endpoint: The API endpoint to send the request to.
        :param data: The data to send in the body of the POST request.
        :param level: API level ('org', 'env', or 'api')
        :return: Response from the API.
        """
        url = self._build_url(endpoint, level)
        logger.info(f"POST request to {url}")
        response = requests.post(url, headers=self.headers, json=data)
        self._log_response(response)
        return response
    
    def post_file(self, endpoint, files, level='env'):
        """
        Perform a POST request with file upload to the given endpoint.
        :param endpoint: The API endpoint to send the request to.
        :param files: Dictionary of files to upload.
        :param level: API level ('org', 'env', or 'api')
        :return: Response from the API.
        """
        url = self._build_url(endpoint, level)
        logger.info(f"POST file request to {url}")
        headers = self.headers.copy()
        headers.pop("Content-Type", None)
        response = requests.post(url, headers=headers, files=files)
        self._log_response(response)
        return response

    def put(self, endpoint, data, level='env'):
        """
        Perform a PUT request to the given endpoint.
        :param endpoint: The API endpoint to send the request to.
        :param data: The data to send in the body of the PUT request.
        :param level: API level ('org', 'env', or 'api')
        :return: Response from the API.
        """
        url = self._build_url(endpoint, level)
        logger.info(f"PUT request to {url}")
        response = requests.put(url, headers=self.headers, json=data)
        self._log_response(response)
        return response

    def delete(self, endpoint, level='env'):
        """
        Perform a DELETE request to the given endpoint.
        :param endpoint: The API endpoint to send the request to.
        :param level: API level ('org', 'env', or 'api')
        :return: Response from the API.
        """
        url = self._build_url(endpoint, level)
        logger.info(f"DELETE request to {url}")
        response = requests.delete(url, headers=self.headers)
        self._log_response(response)
        return response
    
    def _build_url(self, endpoint, level):
        """
        Build a URL for the given endpoint and API level.
        :param endpoint: The API endpoint.
        :param level: API level ('org', 'env', or 'api')
        :return: Complete URL string.
        """
        if level == 'org':
            return self.org_url_builder.build_url(endpoint)
        elif level == 'env':
            return self.env_url_builder.build_url(endpoint)
        elif level == 'api':
            return self.api_url_builder.build_url(endpoint)
        else:
            raise ValueError(f"Unknown API level: {level}")
    
    def _log_response(self, response):
        """
        Log the response from an API request.
        :param response: Response object from requests.
        """
        if 200 <= response.status_code < 300:
            logger.info(f"Response status: {response.status_code}")
            try:
                if response.text:
                    logger.debug(f"Response body: {response.text[:500]}...")
            except Exception:
                pass
        else:
            logger.error(f"Error response: {response.status_code}")
            try:
                if response.text:
                    logger.error(f"Error details: {response.text[:500]}...")
            except Exception:
                pass
