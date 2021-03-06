from ScoutSuite.providers.aws.resources.regions import Regions
from ScoutSuite.providers.aws.resources.resources import AWSResources

from ScoutSuite.providers.utils import get_non_provider_id
from ScoutSuite.providers.aws.facade.facade import AWSFacade


class Alarms(AWSResources):
    async def fetch_all(self, **kwargs):
        raw_alarms = await self.facade.cloudwatch.get_alarms(self.scope['region'])
        for raw_alarm in raw_alarms:
            name, resource = self._parse_alarm(raw_alarm)
            self[name] = resource

    def _parse_alarm(self, raw_alarm):
        raw_alarm['arn'] = raw_alarm.pop('AlarmArn')
        raw_alarm['name'] = raw_alarm.pop('AlarmName')

        # Drop some data
        for key in ['AlarmConfigurationUpdatedTimestamp', 'StateReason', 'StateReasonData', 'StateUpdatedTimestamp']:
            if key in raw_alarm:
                raw_alarm.pop(key)

        alarm_id = get_non_provider_id(raw_alarm['arn'])
        return alarm_id, raw_alarm


class CloudWatch(Regions):
    _children = [
        (Alarms, 'alarms')
    ]

    def __init__(self, facade: AWSFacade):
        super(CloudWatch, self).__init__('cloudwatch', facade)
