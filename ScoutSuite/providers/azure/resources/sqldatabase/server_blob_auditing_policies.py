from ScoutSuite.providers.base.configs.resources import Resources


class ServerBlobAuditingPolicies(Resources):

    def __init__(self, resource_group_name, server_name, facade):
        self.resource_group_name = resource_group_name
        self.server_name = server_name
        self.facade = facade

    async def fetch_all(self):
        policies = await self.facade.sqldatabase.get_server_blob_auditing_policies(
            self.resource_group_name, self.server_name)
        self._parse_policies(policies)

    def _parse_policies(self, policies):
        self.update({
            'auditing_enabled': policies.state == "Enabled",
            'retention_days': policies.retention_days
        })
