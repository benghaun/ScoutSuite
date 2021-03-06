from ScoutSuite.providers.aws.resources.resources import AWSResources
from ScoutSuite.providers.aws.utils import get_name


class Volumes(AWSResources):
    async def fetch_all(self, **kwargs):
        raw_volumes = await self.facade.ec2.get_volumes(self.scope['region'])
        for raw_volume in raw_volumes:
            name, resource = self._parse_volume(raw_volume)
            self[name] = resource

    def _parse_volume(self, raw_volume):
        raw_volume['id'] = raw_volume.pop('VolumeId')
        raw_volume['name'] = get_name(raw_volume, raw_volume, 'id')
        return raw_volume['id'], raw_volume
