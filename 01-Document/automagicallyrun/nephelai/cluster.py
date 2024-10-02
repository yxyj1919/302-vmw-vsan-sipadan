from .bundle import *
from itertools import chain


class ClusterBase(object):
    """
    Basic definition of a 'cluster' defined as a group of log bundles (Things of class LogBundle)
    """

    members = []

    def __init__(self, bundle_list=None, **kwargs):
        if not bundle_list:
            bundle_list = []
        self.uuid = ''  # Clusters should have a UUID to represent the cluster.
        self.version = ''  # Clusters should have a version
        self.members = []
        for member in bundle_list:
            self.add_member(member)

    def add_member(self, bundle):
        """
        Add a bundle to the list of members.
        Bundle validation happens here.
        :param bundle:
        :return:
        """
        return None


class VSANCluster(ClusterBase):
    """
    Base VSAN Cluster class - version unknown
    """
    def __init__(self, bundle_list=list(), **kwargs):
        super(self.__class__, self).__init__(bundle_list, **kwargs)
        self.validate()
        self._master = None
        self._backup = None
        self._agents = None

    def add_member(self, bundle):
        if isinstance(bundle, ESXBundleBase):
            if bundle.is_vsan_enabled():
                self.members.append(bundle)

    def validate(self):
        uuid = ''
        problem_members = []
        for member in self.members:
            try:
                if member.vsan_cluster_info['Local Node State'] == 'MASTER':
                    uuid = member.vsan_cluster_info.get('Sub-Cluster UUID')
                    self.uuid = uuid
                    # print('Detected {0} as cluster uuid'.format(uuid))
            except KeyError:  # problem with a node.
               problem_members.append(member)

        for member in problem_members:  # Cleanup problems
            self.members.remove(member)

        if uuid == '':  # No master pick first one.
            try:
                uuid = self.members[0].vsan_cluster_info.get('Sub-Cluster UUID')
                self.uuid = uuid
            except IndexError:
                raise NephelaiValidateException('Problem finding cluster UUID')  # TODO this whole block should change.
        if uuid != '':
            for member in self.members:  # Prune members from different clusters
                if member.vsan_cluster_info.get('Sub-Cluster UUID') != uuid:
                    self.members.remove(member)

    @property
    def vm_list(self):
        return list(chain(*[x.vm_list for x in self.members]))

    @property
    def master(self):
        """
        Master ESXBundle Object.
        :return: Single ESXBundle Instance
        :raises NephelaiParseException: - raised if != 1 Master node found.
        """
        if not self._master:
            results = [node for node in self.members
                       if node.vsan_cluster_info.get('Local Node State', 'unknown') == 'MASTER']
            if len(results) == 1:
                self._master = results[0]
                return self._master
            else:
                return None
                # raise NephelaiParseException('Unexpected number of MASTER nodes? {0}'.format(results))
        else:
            return self._master

    @property
    def backup(self):
        """
        Master ESXBundle Object.
        :return: Single ESXBundle Instance
        :raises NephelaiParseException: - raised if != 1 Backup node found.
        """
        if not self._backup:
            results = [node for node in self.members
                       if node.vsan_cluster_info.get('Local Node State', 'unknown') == 'BACKUP']
            if len(results) == 1:
                self._backup = results[0]
                return self._backup
            else:
                return None
                # raise NephelaiParseException('Unexpected number of BACKUP nodes? {0}'.format(results))
        else:
            return self._backup

    @property
    def agents(self):
        """
        Master ESXBundle Object.
        :return: list of ESXBundle instances
        """
        if not self._agents:
            results = [node for node in self.members
                       if node.vsan_cluster_info.get('Local Node State', 'unknown') == 'AGENT']
            self._agents = results
            return self._agents
        else:
            return self._agents
