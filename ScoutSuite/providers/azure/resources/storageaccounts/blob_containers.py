from ScoutSuite.providers.base.configs.resources import Resources


class BlobContainers(Resources):

    def __init__(self, resource_group_name, storage_account_name, facade):
        self.resource_group_name = resource_group_name
        self.storage_account_name = storage_account_name
        self.facade = facade

    async def fetch_all(self):
        raw_blob_containers = await self.facade.get_blob_containers(
            self.resource_group_name, self.storage_account_name
        )
        for raw_blob_container in raw_blob_containers:
            id, blob_container = self._parse(raw_blob_container)
            self[id] = blob_container

    def _parse(self, raw_blob_container):
        blob_container = {}
        blob_container['id'] = raw_blob_container.name
        blob_container['public_access_allowed'] = raw_blob_container.public_access != "None"

        return blob_container['id'], blob_container
