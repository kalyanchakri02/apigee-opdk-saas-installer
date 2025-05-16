from install.resources.Resource import Resource

class OrgResource(Resource):
    """Base class for organization-level resources."""

    def _make_request(self, method, endpoint, data=None, files=None, level='org'):
        """
        Make an API request using the connection.
        Default to org-level for organization resources.
        """
        return super()._make_request(method, endpoint, data, files, level) 