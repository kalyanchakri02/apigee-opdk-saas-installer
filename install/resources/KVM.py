from install.resources.EnvConfigResource import EnvConfigResource
import logging
import json
import requests


class KVM(EnvConfigResource):
    """Class to manage Key Value Maps (KVMs) in Apigee."""

    def __init__(self, name, config, connection):
        """Initialize KVM with name, configuration and connection details."""
        super().__init__(name, config, connection)
        self.logger = logging.getLogger(__name__)

    def exists(self):
        """Check if KVM exists in the environment."""
        try:
            response = self.connection.get(f'keyvaluemaps/{self.name}')
            if response is None or response.status_code != 200:
                return False
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error checking if KVM {self.name} exists: {str(e)}")
            return False

    def create(self):
        """Create a new KVM in the environment."""
        try:
            payload = {
                "name": self.name,
                "encrypted": self.config.get('encrypted', False)
            }
            response = self.connection.post(
                f'keyvaluemaps',
                payload
            )
            if response.status_code == 201:
                self.logger.info(f"Successfully created KVM: {self.name}")
                self._update_entries()
                return True
            else:
                self.logger.error(f"Failed to create KVM {self.name}. Status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error creating KVM {self.name}: {str(e)}")
            return False

    def update(self):
        """Update an existing KVM in the environment."""
        try:
            return self._update_entries()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error updating KVM {self.name}: {str(e)}")
            return False

    def _update_entries(self, encrypted=False):
        """Update the entries in the KVM."""
        entries = self.config.get('entries', {})
        payload = {
            "name" : self.name,
            "entry":[
                entries
            ],
            "encrypted" :  encrypted
        }
        try:
            response = self.connection.post(
                f'keyvaluemaps/{self.name}',
                payload
            )
            if response.status_code not in [200, 201]:
                self.logger.error(f"Failed to update entry {key} in KVM {self.name}. Status: {response.status_code}")
            else:
                self.logger.info(f"Successfully updated all entries in KVM {self.name}")
                return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error updating entry {key} in KVM {self.name}: {str(e)}")
        return False
    
    def apply(self):
        if self.exists():
            self.logger.info(f"KVM {self.name} already exists, updating entries")
            self.update()
        else:
            self.logger.info(f"KVM {self.name} does not exist, creating")
            if self.create():
                self.logger.info(f"Successfully created KVM {self.name}")
                self.logger.info(f"Updating entries for KVM {self.name}")
                self._update_entries()
                self.logger.info(f"Successfully updated entries for KVM {self.name}")
            else:
                self.logger.error(f"Failed to create KVM {self.name}")
                return False
        return True



    def delete(self):
        """Delete the KVM from the environment."""
        try:
            response = self.connection.delete(
                f'/v1/organizations/{self.connection.org}/environments/{self.connection.env}/keyvaluemaps/{self.name}'
            )
            if response.status_code == 200:
                self.logger.info(f"Successfully deleted KVM: {self.name}")
                return True
            else:
                self.logger.error(f"Failed to delete KVM {self.name}. Status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error deleting KVM {self.name}: {str(e)}")
            return False



