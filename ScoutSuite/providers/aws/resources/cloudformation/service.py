import re

from ScoutSuite.providers.aws.resources.regions import Regions
from ScoutSuite.providers.aws.resources.resources import AWSResources
from ScoutSuite.providers.aws.facade.facade import AWSFacade


class Stacks(AWSResources):
    async def fetch_all(self, **kwargs):
        raw_stacks  = await self.facade.cloudformation.get_stacks(self.scope['region'])
        for raw_stack in raw_stacks:
            name, stack = self._parse_stack(raw_stack)
            self[name] = stack

    def _parse_stack(self, raw_stack):
        raw_stack['id'] = raw_stack.pop('StackId')
        raw_stack['name'] = raw_stack.pop('StackName')
        raw_stack['drifted'] = raw_stack.pop('DriftInformation')['StackDriftStatus'] == 'DRIFTED'
        raw_stack['termination_protection'] = raw_stack['EnableTerminationProtection']

        template = raw_stack.pop('template')
        raw_stack['deletion_policy'] = self.has_deletion_policy(template)

        if hasattr(template, 'keys'):
            for group in template.keys():
                if 'DeletionPolicy' in template[group]:
                    raw_stack['deletion_policy'] = template[group]['DeletionPolicy']
                    break

        return raw_stack['name'], raw_stack

    @staticmethod
    def has_deletion_policy(template):
        """
        Return region to be used for global calls such as list bucket and get bucket location
        :param template:                    The api response containing the stack's template
        :return:
        """
        has_dp = True
        # If a ressource is found to not have a deletion policy or have it to delete, the boolean is switched to
        # false to indicate that the ressource will be deleted once the stack is deleted
        if isinstance(template, dict):
            template = template['Resources']
            for group in template.keys():
                if 'DeletionPolicy' in template[group]:
                    if template[group]['DeletionPolicy'] is 'Delete':
                        has_dp = False
                else:
                    has_dp = False
        if isinstance(template, str):
            if re.match(r'\"DeletionPolicy\"\s*:\s*\"Delete\"', template):
                has_dp = False
            elif not re.match(r'\"DeletionPolicy\"', template):
                has_dp = False
        return has_dp


class CloudFormation(Regions):
    _children = [
        (Stacks, 'stacks')
    ]

    def __init__(self, facade: AWSFacade):
        super(CloudFormation, self).__init__('cloudformation', facade)
