from install.resources.EnvConfigResource import EnvConfigResource
import logging
import requests


class KVM(EnvConfigResource):
    """Class to manage Key Value Maps (KVMs) in Apigee."""

    def __init__(self, name, config, connection):
        """Initialize KVM with name, configuration and connection details."""
        super().__init__(name, config, connection)
        self.logger = logging.getLogger(__name__)

    def _exists(self, path):
        """Check if KVM or KVM entry exists in the environment."""
        response  = self.connection.get(path)
        if response.status_code == 200:
            return True
        return False

    def _create(self):
        """Create a new KVM in the environment."""
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

    def _update(self):
        """Update an existing KVM in the environment."""
        return self._update_entries()

    def _update_entries(self):
        """Update the entries in the KVM."""
        entries = self.config.get('entries', [])
        for key, value in entries.items():
            payload = {"name":key,"value":value}
            if self._exists(f'/keyvaluemaps/{self.name}/entries/{key}'):
                self.connection.post(f'/keyvaluemaps/{self.name}/entries/{key}',payload)
                self.logger.info(f"Successfully updated entry {key} in KVM {self.name}")
            else:
                self.logger.info(f"Entry {key} does not exist in KVM {self.name}, creating")
                self.connection.post(f'/keyvaluemaps/{self.name}/entries', payload)



    def apply(self):
        if self._exists(f'keyvaluemaps/{self.name}'):
            self.logger.info(f"KVM {self.name} already exists, updating entries")
            self._update()
        else:
            self.logger.info(f"KVM {self.name} does not exist, creating")
            if self._create():
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



