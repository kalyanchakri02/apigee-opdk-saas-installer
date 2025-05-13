from install.resources.EnvConfigResource import EnvConfigResource
import logging
import json
import requests


class CacheResource(EnvConfigResource):
    """Class to manage Cache Resources in Apigee."""

    def __init__(self, name, config, connection):
        """Initialize Cache Resource with name, configuration and connection details."""
        super().__init__(name, config, connection)
        self.logger = logging.getLogger(__name__)

    def exists(self):
        """Check if Cache exists in the environment."""
        try:
            response = self.connection.get(f'/v1/organizations/{self.connection.org}'
                                        f'/environments/{self.connection.env}/caches/{self.name}')
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error checking if Cache {self.name} exists: {str(e)}")
            return False

    def create(self):
        """Create a new Cache in the environment."""
        try:
            payload = {
                "name": self.name,
                "description": self.config.get('description', f'Cache resource {self.name}'),
                "expirySettings": {
                    "timeoutInSec": {
                        "value": self.config.get('timeoutInSec', 3600)
                    },
                    "valuesNull": self.config.get('valuesNull', False)
                },
                "overflowToDisk": self.config.get('overflowToDisk', False),
                "skipCacheIfElementSizeInKBExceeds": self.config.get('maxElementSizeInKB', 128),
                "maxElementsInMemory": self.config.get('maxElementsInMemory', 1000),
                "maxElementsOnDisk": self.config.get('maxElementsOnDisk', 1000),
                "persistent": self.config.get('persistent', False)
            }

            response = self.connection.post(
                f'/v1/organizations/{self.connection.org}/environments/{self.connection.env}/caches',
                json.dumps(payload)
            )
            
            if response.status_code == 201:
                self.logger.info(f"Successfully created Cache: {self.name}")
                return True
            else:
                self.logger.error(f"Failed to create Cache {self.name}. Status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error creating Cache {self.name}: {str(e)}")
            return False

    def update(self):
        """Update an existing Cache in the environment."""
        try:
            # For caches, we need to delete and recreate as there's no update API
            if self.exists():
                if self.delete():
                    return self.create()
                return False
            return self.create()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error updating Cache {self.name}: {str(e)}")
            return False

    def delete(self):
        """Delete the Cache from the environment."""
        try:
            response = self.connection.delete(
                f'/v1/organizations/{self.connection.org}/environments/{self.connection.env}/caches/{self.name}'
            )
            if response.status_code == 200:
                self.logger.info(f"Successfully deleted Cache: {self.name}")
                return True
            else:
                self.logger.error(f"Failed to delete Cache {self.name}. Status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error deleting Cache {self.name}: {str(e)}")
            return False
