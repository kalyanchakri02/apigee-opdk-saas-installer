from install.resources.Resource import Resource
import logging


class KVM(Resource):
    """Class to manage Key Value Maps (KVMs) in Apigee."""

    def __init__(self, name, config, connection):
        """Initialize KVM with name, configuration and connection details."""
        super().__init__(name, config, connection)
        self.logger = logging.getLogger(__name__)

    def _exists(self, path):
        """Check if KVM or KVM entry exists in the environment."""
        response = self._make_request('get', path)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            raise RuntimeError(f"Unexpected response status {response.status_code}: {response.text}")


    def _create(self):
        """Create a new KVM in the environment."""
        payload = {
            "name": self.name,
            "encrypted": self.config.get('encrypted', False)
        }
        response = self._make_request('post', 'keyvaluemaps', data=payload)
        
        if response.status_code == 201 or response.status_code == 409:
            self.logger.info(f"Successfully created KVM/KVM might have already exists: {self.name}")
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
        entries = self.config.get('entries', {})
        for key, value in entries.items():
            payload = {"name": key, "value": value}
            if self._exists(f'keyvaluemaps/{self.name}/entries/{key}'):
                response = self._make_request('post', f'keyvaluemaps/{self.name}/entries/{key}', data=payload)
                if response and response.status_code in [200, 201]:
                    self.logger.info(f"Successfully updated entry {key} in KVM {self.name}")
                else:
                    self.logger.error(f"Failed to update entry {key} in KVM {self.name}")
            else:
                self.logger.info(f"Entry {key} does not exist in KVM {self.name}, creating")
                response = self._make_request('post', f'keyvaluemaps/{self.name}/entries', data=payload)
                if response and response.status_code in [200, 201]:
                    self.logger.info(f"Successfully created entry {key} in KVM {self.name}")
                else:
                    self.logger.error(f"Failed to create entry {key} in KVM {self.name}")

    def apply(self):
        """Apply the KVM configuration."""
        if self._exists(f'keyvaluemaps/{self.name}'):
            self.logger.info(f"KVM {self.name} already exists, updating entries")
            self._update()
            return True
        else:
            self.logger.info(f"KVM {self.name} does not exist, creating")
            if self._create():
                self.logger.info(f"Successfully created and updated KVM {self.name}")
                return True
            else:
                self.logger.error(f"Failed to create KVM {self.name}")
                return False

    def delete(self):
        """Delete the KVM from the environment."""
        response = self._make_request('delete', f'keyvaluemaps/{self.name}')
        if response and response.status_code in [200, 204]:
            self.logger.info(f"Successfully deleted KVM: {self.name}")
            return True
        else:
            self.logger.error(f"Failed to delete KVM {self.name}. Status: {response.status_code if response else 'No response'}")
            return False



