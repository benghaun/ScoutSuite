from ScoutSuite.providers.aws.resources.resources import AWSResources


class Snapshots(AWSResources):
    async def fetch_all(self, **kwargs):
        raw_snapshots = await self.facade.rds.get_snapshots(self.scope['region'], self.scope['vpc'])
        for raw_snapshot in raw_snapshots:
            name, resource = self._parse_snapshot(raw_snapshot)
            self[name] = resource

    def _parse_snapshot(self, raw_snapshot):
        snapshot_id = raw_snapshot.pop('DBSnapshotIdentifier')
        snapshot = {}
        snapshot['arn'] = raw_snapshot.pop('DBSnapshotArn')
        snapshot['id'] = snapshot_id,
        snapshot['name'] = snapshot_id,
        snapshot['vpc_id'] = raw_snapshot['VpcId']
        snapshot['attributes'] = raw_snapshot['Attributes']

        attributes = [
            'DBInstanceIdentifier',
            'SnapshotCreateTime',
            'Encrypted',
            'OptionGroupName'
        ]
        for attribute in attributes:
            snapshot[attribute] = raw_snapshot[attribute] if attribute in raw_snapshot else None

        return snapshot_id, snapshot
