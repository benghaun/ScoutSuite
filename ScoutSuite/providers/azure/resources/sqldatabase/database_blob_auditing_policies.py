from ScoutSuite.providers.azure.facade.base import AzureFacade
from ScoutSuite.providers.base.configs.resources import Resources


class DatabaseBlobAuditingPolicies(Resources):

    def __init__(self, resource_group_name, server_name, database_name, facade: AzureFacade):
        self.resource_group_name = resource_group_name
        self.server_name = server_name
        self.database_name = database_name
        self.facade = facade

    async def fetch_all(self):
        policies = await self.facade.sqldatabase.get_database_blob_auditing_policies(
            self.resource_group_name, self.server_name, self.database_name)
        self._parse_policies(policies)

    def _parse_policies(self, policies):
        self.update({
            'auditing_enabled': policies.state == "Enabled",
            'retention_days': policies.retention_days
        })
