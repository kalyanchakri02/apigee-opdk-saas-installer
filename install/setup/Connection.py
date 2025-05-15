# core/connection.py
import requests
from install.setup.logger_config import setup_logger, log_separator

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
        self.base_url = f"https://{host}/v1/organizations/{org}/environments/{env}"
        self.headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }
        logger.info(f"Setting up connection to Apigee:")
        logger.info(f"- Organization: {org}")
        logger.info(f"- Environment: {env}")
        logger.info(f"- Host: {host}")

    def get(self, endpoint):
        """
        Perform a GET request to the given endpoint.
        :param endpoint: The API endpoint to send the request to.
        :return: Response JSON from the API or None if request failed.
        """
        url = f"{self.base_url}/{endpoint}"
        logger.info(f"GET request to {url}")
        response = requests.get(url, headers=self.headers)
        logger.info(f"Response: {response.json()}, status_code {response.status_code}")
        return response

    def post(self, endpoint, data):
        """
        Perform a POST request to the given endpoint.
        :param endpoint: The API endpoint to send the request to.
        :param data: The data to send in the body of the POST request.
        :return: Response JSON from the API or None if request failed.
        """
        url = f"{self.base_url}/{endpoint}"
        logger.info(f"POST request to {url}")
        response = requests.post(url, headers=self.headers, json=data)
        logger.info(f"Response: {response.json()}")
        return response
    
    def post_file(self, endpoint, files):
        """
        Perform a POST request with file upload to the given endpoint.
        :param endpoint: The API endpoint to send the request to.
        :param files: Dictionary of files to upload.
        :return: Response JSON from the API or None if request failed.
        """
        url = f"{self.base_url}/{endpoint}"
        logger.info(f"POST request to {url}")
        headers = self.headers.copy()
        headers.pop("Content-Type", None)
        response = requests.post(url, headers=headers, files=files)
        logger.info(f"Response: {response.json()}")
        return response

    def put(self, endpoint, data):
        """
        Perform a PUT request to the given endpoint.
        :param endpoint: The API endpoint to send the request to.
        :param data: The data to send in the body of the PUT request.
        :return: Response JSON from the API or None if request failed.
        """
        url = f"{self.base_url}/{endpoint}"
        logger.info(f"PUT request to {url}")
        response = requests.put(url, headers=self.headers, json=data)
        logger.info(f"Response: {response.json()}")
        return response

    def delete(self, endpoint):
        """
        Perform a DELETE request to the given endpoint.
        :param endpoint: The API endpoint to send the request to.
        :return: Response JSON from the API or None if request failed.
        """
        url = f"{self.base_url}/{endpoint}"
        logger.info(f"DELETE request to {url}")
        response = requests.delete(url, headers=self.headers, json=data)
        logger.info(f"Response: {response.json()}")
        return response
