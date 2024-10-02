from .bundle import Logbundle
import os
import logging
import re


class VCenterBundleBase(Logbundle):
    """
    VC Log bundle.
    This is going to be based on the appliance bundle first - with windows VC being a subclass.
    Starting /w 6.0 for consistency.

    :param path: Path is required - this is a directory which contains one or more files which constitute the log\
     bundle.
    """

    def __init__(self, path=None, **kwargs):
        super(self.__class__, self).__init__(path, **kwargs)
        self.bundleType = "vCenter"
        self._platform = "unknown"  # Windows vs Linux
        self._hostname = None
        self._logs = None

    @property
    def platform(self):
        """
        Which platform is this support bundle from?
        :return: String - name of platform.
        """
        if self._platform == "unknown":
            content = self.get_rel_dir_content('./')
            if ('ProgramData' in content) and ('Windows' in content):
                self._platform = 'Windows'
            elif ('var' in content) and ('etc' in content):
                self._platform = 'Linux'
            else:
                self._platform = 'unknown'

        return self._platform

    @property
    def hostname(self):
        """
        fqdn of the vCenter server.
        :return: string - FQDN
        """
        if self._hostname is None:
            if self.platform == 'Windows':
                with self.get_file('commands/systeminfo.txt') as f:
                    # Get first couple lines:
                    start = f.readlines()[:4]
                    for line in start:
                        if line.startswith('Host Name'):
                            try:
                                self._hostname = line.split(':')[1].strip()
                                return self._hostname
                            except IndexError:
                                self._hostname = 'unknown'
            elif self.platform == 'Linux':
                with self.get_file('commands/uname_-a.txt') as f:
                    data = f.readlines()
                try:
                    parts = data[0].rstrip().split(' ')
                    if parts[0] == 'Linux':
                        self._hostname = parts[1]
                except IndexError:
                    self._hostname = 'unknown'
        return self._hostname

    @property
    def logs(self):
        """
        * K:V pairs of available logs.
        * V's are a list of relative paths ordered .log -> .0 -> .1 etc
        :return: dict
        """
        SKIP_LOGS = ('')
        SOURCES = []  # Empty list as fallback for unknown platform.
        log_filename_regex = re.compile(r'(?P<logname>.*?)(?P<suffix>-[0-9]+)?\.log')
        if self._logs is None:
            self._logs = {}
            if self.platform == 'Windows':
                SOURCES = ['ProgramData/VMware/vCenterServer/logs/vmware-vpx']
            elif self.platform == 'Linux':
                SOURCES = ['var/log/vmware/vpxd']

            for source in SOURCES:
                try:
                    dir_content = self.get_rel_dir_content(source)
                    for item in dir_content:
                        match = log_filename_regex.match(item)
                        if match:
                            try:
                                self.logs[match.groupdict().get('logname')].append(os.path.join(source, item))
                            except KeyError:
                                self.logs[match.groupdict().get('logname')] = []
                                self.logs[match.groupdict().get('logname')].append(os.path.join(source, item))
                except (IOError, OSError) as e:
                    logging.warning('Problem opening {0}'.format(source))
        return self._logs
