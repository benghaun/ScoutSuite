from ScoutSuite.providers.aws.facade.facade import AWSFacade
from ScoutSuite.providers.aws.resources.regions import Regions
from ScoutSuite.providers.aws.resources.resources import AWSResources


class Connections(AWSResources):
    async def fetch_all(self, **kwargs):
        raw_connections  = await self.facade.directconnect.get_connections(self.scope['region'])
        for raw_connection in raw_connections:
            name, resource = self._parse_function(raw_connection)
            self[name] = resource

    def _parse_function(self, raw_connection):
        raw_connection['id'] = raw_connection.pop('connectionId')
        raw_connection['name'] = raw_connection.pop('connectionName')
        return raw_connection['id'], raw_connection


class DirectConnect(Regions):
    _children = [
        (Connections, 'connections')
    ]

    def __init__(self):
        super(DirectConnect, self).__init__('directconnect')
