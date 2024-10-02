#!/usr/bin/env python3

"""
Nephelai is a Library for classifying VMware support bundles.

It is written for the GSS audience.

Nephelai assumes scripts-data NFS back-end infrastructure is where it is operating,
so it may do silly things like blind opens without checking (To avoid attribute cache related races).

Also by default operates in a method that a) Makes data available but doesn't read it unless requestsed. Upon read -
data is cached. Ie: operates to minimize I/O required for a given task.
"""
from .util import CachingDict
from .exceptions import NephelaiBaseException, NephelaiValidateException, NephelaiParseException
from .exceptions import NephelaiUnavailException, NephelaiVersionException, NephelaiDisabledException
import os
import re
import json
from ast import literal_eval
import bz2
import gzip
import logging
from functools import partial
from itertools import chain
import xml.etree.cElementTree as ET
import datetime
from functools import reduce

__author__ = 'rmurray'


class Logbundle(object):
    """
    Base class for log bundle.

    It provides a base for building product specific classes on top of.

    :param path: Path is required - this is a directory which contains one or more files which constitute the log\
     bundle.

    :param Expand_Filenames: Defaults to True. Set to false to disable automatic 'guessing' of filenames to deal with \
    data-at-rest compression from EMC Isilon NFS storage.

    :raise:
        :NephelaiValidateException: When instantiated the class is unable to validate the log bundle (validate()
                                    function returns false).
    """

    path = ''
    bundleType = "Unknown"
    EXPANDFILENAMES = False
    FILEXTNS = ('.gz', '.bz2')  # File xtns that are handled.

    def __init__(self, path=None, **kwargs):
        self.path = path
        self.bundleType = "Unknown"
        if not self.validate():
            raise NephelaiValidateException('Unable to validate bundle at ' + path)
        self.EXPANDFILENAMES = kwargs.get('Expand_Filenames', True)

    def __str__(self):
        return self.bundleType + " bundle at " + self.path

    def _open_file(self, abspath, mode='rt', recurse=True, encoding='utf-8'):
        """
        Given absolute path - return filelike object
        Handles compressed files
        :param abspath:  Absolute path to file.
        :return: File Objects
        Can Raise exceptions - handle downstream.
        """
        """
        Right now - just file suffix for detection. Not overly smart.
        """
        try:
            logging.debug('Opening file {0}'.format(abspath))
            if abspath.endswith('.gz'):
                return gzip.open(abspath, mode, encoding=encoding, errors='surrogateescape')
            elif abspath.endswith('.bz2'):
                return bz2.open(abspath, mode, encoding=encoding, errors='surrogateescape')
            else:
                return open(abspath, mode, encoding=encoding, errors='surrogateescape')
        except FileNotFoundError as e:
            logging.debug("Problem opening file {0}".format(abspath), exc_info=True)
            if self.EXPANDFILENAMES and recurse:
                logging.debug("Looking for compressed versions of {0}".format(abspath))
                if not abspath.endswith('.gz'):
                    try:
                        return self._open_file(abspath + '.gz', mode, recurse=False)
                    except:
                        pass  # Skip errors - don't care
                if not abspath.endswith('.bz2'):
                    try:
                        return self._open_file(abspath + '.bz2', mode, recurse=False)
                    except:
                        pass
            raise e  # This isn't reached if returns above succeed.

    def validate(self):
        """
        Test to see if bundle is clean bundle of bundle type.

        Base implementation just checks for existance. There is the possibility of false-negative here due to NFS \
        races.

        :return: True / False
        """
        return os.path.exists(self.path)

    def get_file_content(self, relpath, encoding=None):
        """
        Open file at relative path. Handles decompression automatically.

        :param relpath: Bundle-Relative path to the file which should be opened.
        :param encoding: Optional param - encoding to use when reading the file(s) defaults to 'utf-8'

        :raise:
            :OSError: Permissions related file access problems can be raised for awareness.

            :IOError: Can be raised if a file is not found.

        :return: content of the file.
        """
        try:
            if encoding:
                with self._open_file(os.path.join(self.path, relpath), encoding=encoding) as f:
                    return f.read()
            else:
                with self._open_file(os.path.join(self.path, relpath)) as f:
                    return f.read()
        except OSError as e:
            logging.debug("Problem opening file {0}".format(os.path.join(self.path, relpath)), exc_info=True)
            raise e
        except Exception as e:
            logging.warning("Unexpected problem opening file {0}".format(os.path.join(self.path, relpath)),
                            exc_info=True)
            raise e

    def get_file_gen(self, relpath, encoding=None):
        """
        return generator object of a file at relative path within bundle. Handles decompression automatically.
        note - yielded lines have \n removed.
        :param relpath: relative path to the file which should be opened.
        :param encoding: optional param - defaults to utf-8
        :return:
        """
        with self.get_file(relpath=relpath, encoding=encoding) as f:
            for line in f.readlines():
                yield line.rstrip()

    def get_file(self, relpath, encoding=None):
        """
        return file-like object of file at relative path. Handles decompression automatically.

        :param relpath: Bundle-Relative path to the file which should be opened.
        :param encoding: Optional param - encoding to use when reading the file(s) defaults to 'utf-8'

        :raise:
            :OSError: Permissions related file access problems can be raised for awareness.

            :IOError: Can be raised if a file is not found.

        :return: file-like object
        """
        try:
            if encoding:
                return self._open_file(os.path.join(self.path, relpath), encoding=encoding)
            else:
                return self._open_file(os.path.join(self.path, relpath))
        except OSError as e:
            logging.debug("Problem opening file {0}".format(os.path.join(self.path, relpath)), exc_info=True)
            raise e
        except Exception as e:
            logging.warning("Unexpected problem opening file {0}".format(os.path.join(self.path, relpath)),
                            exc_info=True)
            raise e

    def get_file_lines_iter(self, relpath, encoding=None):
        """
        Generator - yields line by line content from relpath as a generator.

        :param relpath: Bundle-Relative path to the file which should be opened.
        :param encoding: Optional param - encoding to use when reading the file(s) defaults to 'ascii'

        :raise:
            :OSError: Permissions related file access problems can be raised for awareness.

            :IOError: Can be raised if a file is not found.

        :return: iterator of lines contained in file.
        """
        try:
            if encoding:
                with self._open_file(os.path.join(self.path, relpath), encoding=encoding) as f:
                    for line in f.readlines():
                        yield line
            else:
                with self._open_file(os.path.join(self.path, relpath)) as f:
                    for line in f.readlines():
                        yield line
        except OSError as e:
            logging.debug("Problem opening file {0}".format(os.path.join(self.path, relpath)), exc_info=True)
            raise e
        except Exception as e:
            logging.warning("Unexpected problem opening file {0}".format(os.path.join(self.path, relpath)),
                            exc_info=True)
            raise e

    def _mask_compressed_filename(self, filename):
        """
        Given filename return same name minus self.FILEXTNS
        :return:
        """
        for xtn in self.FILEXTNS:
            if filename.endswith(xtn):
                return filename[:filename.rfind(xtn)]
        return filename

    def get_rel_dir_content(self, relpath):
        """
        Get contents of directory at relative path in log bundle. \
        removes '.gz' / '.bz2' extensions from reported filenames if Expand_Filenames is True \
        (See Isilon compression at rest behaviour). This means the same 'filename' may appear twice in the list.

        :param relpath: Bundle-Relative path to the directory which should be listed.

        :raise:
            :OSError: Permissions related directory access problems can be raised for awareness.

            :IOError: Can be raised if a directory is not found.

        :return: list of files at path.
        """
        if self.EXPANDFILENAMES:
            try:
                dir_listing = [self._mask_compressed_filename(x) for x in
                               os.listdir(os.path.join(self.path, relpath.lstrip(os.path.sep)))]
                return dir_listing
            except:
                raise
        else:
            try:
                return os.listdir(os.path.join(self.path, relpath.lstrip(os.path.sep)))
            except:
                raise


class VMBundle(Logbundle):
    """
    VM Log bundle - note could be subdir of larger ESXi bundle.

    Defined as a directory which contains a .vmx file (validate() will fail if this isn't true).

    :param path: Path is required - this is a directory which contains one or more files which constitute the log\
     bundle.

    :param rootBundle: rootBundle is used to link this VMBundle object to a root LogBundle object if one is present.\
    Can access this via VMBundle.rootBundle - useful for looking up host specific configuration details.
    """

    def __init__(self, path=None, rootBundle=None, vmx_name=None, **kwargs):
        self.bundleType = "Virtual Machine"
        self._vmx_name = None
        self._vmCfg = None
        self._vmdks = None
        self._dirContent = None
        if isinstance(rootBundle, Logbundle):
            self.rootBundle = rootBundle
        else:
            self.rootBundle = None
        if vmx_name:
            self._vmx_name = vmx_name
        super().__init__(path, **kwargs)

    def __str__(self):
        return self.bundleType + " configuration directory at " + self.path

    def validate(self):
        """
        tests to see if the 'bundle' is a Virtual Machine configuration directory.
        Specifically looking for a file ending with '.vmx'

        :return: True / False
        """
        try:
            # Look for *.vmx file in the self.path
            files = self.dir_content
            if len([x for x in files if x.endswith('.vmx')]) > 0:  # Are there any files that end in .vmx in this dir?
                return True
        except:
            return False
        return False

    @property
    def dir_content(self):
        """
        List of files in vmx config - cached to avoid extra work.

        :return: list of filenames contained within
        """
        if self._dirContent:
            return self._dirContent
        else:
            self._dirContent = os.listdir(self.path)
            return self._dirContent

    @property
    def vmx_name(self):
        """
        .vmx filename

        :return: string which corresponds to the filename of the .vmx file.
        """
        if self._vmx_name:
            return self._vmx_name
        else:  # Go find it
            vmx_files = [item for item in self.dir_content if item.endswith('.vmx')]
            if len(vmx_files) == 1:  # One and only one
                self._vmx_name = vmx_files[0]
                return self._vmx_name
            elif len(vmx_files) > 1:  # More than one .vmx file
                logging.warning("More than one .vmx file located in {0} {1}".format(self.path, vmx_files))
                return None
            else:
                logging.warning("Problems locating .vmx file in {0}".format(self.path))
                return None

    @property
    def vmCfg(self):
        """
        Cached when accessed for the first time.

        :return: Dict of the K:V configuration options defined in the .vmx file.
        """
        if self._vmCfg:
            return self._vmCfg
        else:
            self._vmCfg = self.get_vmCfg()
            return self._vmCfg

    @property
    def vmdks(self):
        """
        List of vmdk's related to the VM - calls get_vmdk_list() to build.

        :return: list of vmdk file paths.
        """
        if self._vmdks:
            return self._vmdks
        else:
            self._vmdks = self.get_vmdk_list()
            return self._vmdks

    def get_vmdk_list(self):
        """
        parse vmCfg get list of vmdks

        :return: list of paths to vmdk files.
        """
        logging.debug("Generating vmdk list for {0}".format(self.path))
        disk_key_list = [x for x in list(self.vmCfg.keys()) if x.endswith('fileName')]
        disks = []
        out_list = []
        for dk in disk_key_list:
            if self.vmCfg[dk].endswith('vmdk'):
                try:
                    if self.vmCfg[dk.split('.')[0] + '.present'] == 'TRUE':
                        disks.append(self.vmCfg[dk])
                except KeyError:
                    pass

        # Try and read the contents
        for d in disks:
            disk_dict = {}
            match = re.search(r'/vmfs/volumes/.*vmdk', d)
            if match:  # Abs path
                disk_dict['path'] = os.path.join(self.rootBundle.path, d.lstrip(os.path.sep))
            else:
                disk_dict['path'] = os.path.join(self.path, d)
            try:
                if not os.stat(disk_dict.get(
                        'path')).st_size == 1024:  # Skip chunks - in the future perhaps read partition tables?
                    disk_dict.update(self._get_vmdk_dict(disk_dict.get('path')))
                    disk_dict['fileName'] = d
                    out_list.append(disk_dict)
            except FileNotFoundError:
                logging.warning('Unable to read {0} - cannot find the file'.format(disk_dict.get('path')))
                pass  # Skip
        return out_list

    def _get_vmdk_dict(self, path):
        disk_dict = {'backing': tuple()}
        extents = []
        for line in self.get_file_lines_iter(path):
            if line.startswith('RW'):
                # Extent description
                # RW <blocks> <type> <extent>
                tmpdict = {'blocks': line.split()[1],
                           'type': line.split()[2],
                           'extent': line.split('"')[1].rstrip()}
                extents.append(tmpdict)
            else:
                l_split = line.split('=')
                if len(l_split) == 2:
                    disk_dict[l_split[0].strip()] = l_split[1].strip().strip('"')
        disk_dict['backing'] = tuple(extents)
        return disk_dict

    def get_vmCfg(self):
        """
        :return: dict of VM Configuration
        """
        logging.debug("Reading .vmx configuration data for {0}".format(self.path))
        outdict = {}
        try:
            for vmx_content in self.get_file_lines_iter(self.vmx_name):
                split_c = vmx_content.split('=', 1)
                if len(split_c) >= 2:
                    outdict[split_c[0].strip()] = ''.join(split_c[1:]).strip().strip('"')
        except TypeError:  # vmx_name can be None
            return {}
        return outdict


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
class ESXBundleBase(Logbundle):
    """
    ESXi log bundle. At the time of writing this covers ESXi 5.5 -> 6.0 and vsphere-2016 beta.

    :param path: Path is required - this is a directory which contains one or more files which constitute the log\
     bundle.

    :param Expand_Filenames: Defaults to True. Set to false to disable automatic 'guessing' of filenames to deal with \
    data-at-rest compression from EMC Isilon NFS storage.

    :raise:
        :NephelaiValidateException: When instantiated the class is unable to validate the log bundle (validate()
                                    function returns false).
    """

    def __init__(self, path=None, **kwargs):
        super().__init__(path, **kwargs)
        self.bundleType = "ESXi"
        self._VALID_IP_PROTO = ('IPv4', 'IPv6')
        self._vm_list = None
        self._vsan_cluster_info = None
        self._avail_localcli = None
        self._cmmds_content = None
        self._bundleInfo = None
        self._nicinfo = None
        self._nics = None
        self._switches = None
        self._logs = None
        self._version = None
        self._hostname = None
        self._esxcfg_info = None
        self._esx_conf = None
        self._vimdump = None
        self._vsan_health = None

    @property
    def hostname(self):
        """
        This ESXi host's FQDN - choosing to pull this detail from *commands/uname_-a.txt* \
         /etc/hosts is harder to parse as can include extra hand crafted data.\
         Also FDM not always enabled so isn't a good source of data.\
        While esxcfg-info would be a good source it is too much of a cost to parse for this alone.

        :return: string (hostname)
        """
        if self._hostname is None:
            with self.get_file('commands/uname_-a.txt') as f:
                data = f.readlines()
            parts = data[0].rstrip().split(' ')
            if parts[0] == 'VMkernel':
                self._hostname = parts[1]
        return self._hostname

    @property
    def version(self):
        """
        property - parses *commands/vmware_-vl.txt* to build a dict of the ESXi version.

        * 'Friendly', is the human readable string.
        * 'major','minor','maint','buildnumber' are numeric parts of the version string.

        :return: dict representing the ESXi version of the bundle.
        """
        if self._version is None:
            output = {}
            with self.get_file('commands/vmware_-vl.txt') as f:
                data = f.readlines()
            output['Friendly'] = data[1].rstrip()
            z = data[0].rstrip()
            parts = z.split()
            if (parts[0] == 'VMware') and (parts[1] == 'ESXi'):
                try:
                    output['major'], output['minor'], output['maint'] = [int(x) for x in parts[2].split('.')]
                except ValueError:
                    output['major'], output['minor'], output['maint'] = 0, 0, 0
                try:
                    output['buildnumber'] = int(parts[3].split('-')[1])
                except ValueError:
                    output['buildnumber'] = 'unknown'
            self._version = output
        return self._version

    @property
    def esxcfg_info(self):
        """
        ElementTree representation of esxcfg-info xml output. Expect this to disappear alongside esxcfg-info itself as
        it is deprecated in later ESXi versions.

        :note: This can be expensive on larger hosts.

        :return: ElementTree object - see https://docs.python.org/2/library/xml.etree.elementtree.html
        """
        if self._esxcfg_info is None:
            try:
                with self.get_file('commands/esxcfg-info_-a--F-xml.txt') as f:
                    self._esxcfg_info = ET.parse(f)
            except:
                raise
        return self._esxcfg_info

    @property
    def nics(self):
        """
        Dictionary of all network interfaces (both vmkernel and physical)

        Built from *commands/nicinfo.sh.txt* and *commands/esxcfg-vmknic_-l.txt*

        :return: dict - keys are interface names ie: 'vmk#' or 'vmnic#'
        """
        if self._nics is None:
            self._nics = self._parse_nicinfo()
            self._nics.update(self._parse_esxcfg_vmknic())
        return self._nics

    @property
    def switches(self):
        """
        vSwitches and DVS switches defined on this host.

        Built from *commands/esxcfg-vswitch_-l.txt*

        :return: dict of switches (keys are switch names)
        """
        if self._switches is None:
            self._switches = self._parse_esxcfg_vswitch()
            try:
                net_dvs = self._parse_netdvs()
                for switch in self._switches:
                    if self._switches.get(switch).get('type') == 'DVS':
                        uplink_map = {}
                        dvs_data = [(x,y) for x, y in net_dvs.items() if y.get('name') == switch]  # lookup specific sw
                        if len(dvs_data) == 1:
                            self._switches[switch]['uuid'], sw_data = list(dvs_data)[0]

                            port_to_vmnic = dict([
                                                  (port, list(data.get('client').keys())[0])
                                                    for port, data in [ (p, d) for p, d in
                                                        self._switches.get(switch).get('dvports').items()
                                                        if type(d.get('client')) is dict
                                                      ]  # detects vmk / vmnic ports
                                                  if list(data.get('client').keys())[0].startswith('vmnic')
                            ])  # {'36': 'vmnic2', '37': 'vmnic3', '38': 'vmnic4', '39': 'vmnic5'}
                            for port, nic in port_to_vmnic.items():
                                uplink_name = sw_data.get(port, {}).get('uplink_name')
                                if uplink_name:
                                    uplink_map[uplink_name] = nic
                            # Now have k:v map.
                            for port, data in self._switches.get(switch).get('dvports').items():
                                
                                active = [uplink_map.get(item) for item in sw_data.get(port, {}).get('active', [])]
                                standby = [uplink_map.get(item) for item in sw_data.get(port, {}).get('standby', [])]
                                data.update({
                                    'active_ifaces': active,
                                    'standby_ifaces': standby
                                })

                        else:
                            raise NephelaiUnavailException  # Bail - something doesn't make sense.

            except NephelaiUnavailException:
                pass
        return self._switches

    @property
    def bundleInfo(self):
        """
        Content of the README file in a vm-support - which manifests etc were ran during bundle creation etc.

        :return: dict representation of the content of *README* file in vm-support.
        """
        if self._bundleInfo is None:
            try:
                output = {}
                with self.get_file('README') as f:
                    content = f.readlines()
                for line in content[:5]:
                    try:
                        key, value = line.rstrip().split(':', 1)
                        value = value.lstrip()
                        if key == 'Options':
                            value = literal_eval(value)
                            if 'manifests' in value:
                                value['manifests'] = value.get('manifests', '').split(' ')
                        elif key == 'Captured on':
                            try:
                                value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
                            except:
                                pass
                        output[key] = value
                    except ValueError:
                        pass
                self._bundleInfo = output
                return self._bundleInfo
            except:
                self._bundleInfo = {}
                logging.debug('Problem building bundleInfo.', exc_info=True)
        else:
            return self._bundleInfo

    @property
    def cmmds(self):
        """
        cmmds property - contains expanded dump of cmmds's state parses *commands/cmmds-tool_find--f-python.txt*

        :raise:
            :NephelaiDisabledException: If VSAN is disabled raise Feature Disabled Exception (NephelaiDisabledException)

        :return: list of dictionaries - each dict is expanded ( 'content' is parsed ) dump of object state.
        """
        if self._cmmds_content is None:
            # Not cached - lets go get the data.
            if self.is_vsan_enabled():
                try:
                    with self.get_file('commands/cmmds-tool_find--f-python.txt') as f:
                        workingset = literal_eval(f.read())
                    for item in workingset:
                        if item.get('content', '') != '':  # if there is content.
                            item['content'] = literal_eval(item.get('content', None))
                        else:
                            item['content'] = None

                    self._cmmds_content = workingset
                    return self._cmmds_content
                except:
                    raise NephelaiParseException('Error parsing cmmds data.')
            else:
                raise NephelaiDisabledException('VSAN is disabled.')
        else:
            return self._cmmds_content

    @property
    def localcli(self):
        """
        Localcli property - k:v pairs (returns dict) K is available localcli resource v is pythonic content.

        v is setup as functools.partial() callout to a function to retreive the requested information. Mostly json
        But also unique parsers for data not in the json directory of a support bundle.

        Essentially - by default 100% of the json/ directory is available - additional parsers available defined in \
        *._get_localcli_parsers()* are also made available.

        :return: dict keys are available localcli data sources.
        """
        if self._avail_localcli is None:
            self._avail_localcli = CachingDict()
            self._avail_localcli.update(self._get_localcli_parsers())  # Set the parsers first - so that json overrides.
            try:
                # Pull all the files in the json/ dir that end in .json
                json_files = [x for x in self.get_rel_dir_content('json/') if x.endswith('.json')]
                # keys = [x[:-5] for x in json_files]  #Strip '.json' suffix
                for item in json_files:  # Add a key per json file, setup partial() to pull json data on first access.
                    self._avail_localcli[item[:-5]] = partial(self._read_json, os.path.join('json', item))
            except:  # Handle lack of jsondir
                pass
            return self._avail_localcli
        else:
            return self._avail_localcli

    @property
    def logs(self):
        """
        * K:V pairs of available logs.
        * K's generated from the union of the set of filenames from var/log and var/run/log
        * V's are a list of relative paths, ordered .log -> .0 -> .1 etc

        :return: dict - keys are available log 'sources' - v is list of relative paths.
        """
        SKIP_LOGS = ('vsantraces', '')
        if self._logs is None:
            self._logs = {}
            runlog = self.get_rel_dir_content('var/run/log')
            varlog = self.get_rel_dir_content('var/log')
            run_set = set([log.split('.')[0] for log in runlog])
            var_set = set([log.split('.')[0] for log in varlog])
            for item in SKIP_LOGS:
                run_set.discard(item)
                var_set.discard(item)
            if '.vmsyslogd.err' in varlog:
                var_set.add('.vmsyslogd.err')  # Special case.

            log_set = set.union(run_set, var_set)

            def sorting_key(filename):
                try:
                    tail = filename.split('.')[1]
                    if tail == 'log':
                        return -1
                    elif tail.isdigit():
                        return int(tail)
                    else:
                        return tail
                except:
                    return filename

            for log in log_set:
                self._logs[log] = []  # Make empty list in key.
                blacklist = []
                for item in runlog:
                    if item.split('.')[0] == log:
                        self._logs[log].append(os.path.join('var/run/log', item))
                        blacklist.append(item)
                for item in varlog:
                    if item.split('.')[0] == log and not item in blacklist:  # Skip stuff from var/run/log
                        self._logs[log].append(os.path.join('var/log', item))
                if log == '.vmsyslogd.err':
                    self._logs[log].append(os.path.join('var/log', '.vmsyslogd.err'))
                self._logs[log].sort(key=sorting_key)

        return self._logs

    @property
    def vm_list(self):
        """
        List of known VMs built by calling find_vmxs()

        :todo: Currently this uses an expensive search method - parsing etc/vmware/hostd/vmInventory.xml may be wiser.
        :return: list of VMBundle objects one per identified VM.
        """
        if self._vm_list is None:
            self._vm_list = self.find_vmxs()
        return self._vm_list

    @property
    def vsan_cluster_info(self):
        """
        Parses *commands/localcli_vsan-cluster-list.txt*

        :return: dict
        """
        if self.is_vsan_enabled():
            if not self._vsan_cluster_info:
                self._vsan_cluster_info = self._parse_localcli_vsan_cluster_list()
            return self._vsan_cluster_info
        else:  # VSAN disabled
            raise NephelaiDisabledException('VSAN Disabled.')

    @property
    def esx_conf(self):
        """
        Parses the etc/vmware/esx.conf file and returns a dict of the contents.

        :return: dict
        """
        if self._esx_conf is None:
            with self.get_file('etc/vmware/esx.conf') as f:
                outdict = {}
                for line in f.readlines():
                    try:
                        k, v = line.rstrip().split('=')
                        k = k.strip()
                        v = self._normalize_localcli(v.strip().strip('"'))
                        if k not in list(outdict.keys()):
                            outdict[k] = v
                        else:
                            logging.debug('Duplicate keys {0} in esx.conf'.format(k))
                            pass  # Don't overwrite...
                    except ValueError:
                        logging.debug('Issue parsing {0} in esx.conf'.format(line))
                        pass
            self._esx_conf = outdict

        return self._esx_conf

    @property
    def vimdump(self):
        """
        parses vmware-vimdump and returns dict of the contents.
        :return: dict
        """
        if self._vimdump is None:
            with self.get_file('commands/vmware-vimdump_-o----U-dcui.txt') as f:
                outdict = {}

                def vimdump_gen(fobj):
                    """
                    Generator for vimdump
                    :param fobj: file-like object
                    :return:
                    """
                    for line in fobj.readlines():
                        yield line.rstrip()

                outdict = self._parse_vmodl(vimdump_gen(f))
            self._vimdump = outdict

        return self._vimdump

    @property
    def vsan_health(self):
        """
        pull data fromm VSAN Health service.
        :return:
        """
        if not self._vsan_health and self.is_vsan_enabled():
            try:
                outdict = {}
                with self.get_file('commands/python_usrlibvmwarevsanbinvsan-health-statuspyc.txt') as f:
                    # Health status
                    for line in f.readlines():

                        if line.startswith('Health service version:'):
                            try:
                                outdict['version'] = line.split(':')[1].lstrip().rstrip()
                            except IndexError:
                                pass
                            break
                        else:
                            pass  # loop

                    vmodl_sections = [
                        'VSAN HCL related hardware info:',
                        'Limits summary:',
                        'Network summary (without any peer-checks):'
                    ]

                    end_section = ['}', ']']

                    def health_status_gen(fobj):
                        """
                        Generator for health service.
                        :param fobj:
                        :return:
                        """
                        bVMODLData = False
                        for line in fobj.readlines():
                            if not bVMODLData:
                                if line.rstrip() in vmodl_sections:
                                    bVMODLData = True
                                    yield '=== 1. ' + line.rstrip().rstrip(':') + ' ==='
                                else:
                                    pass
                            else:
                                if line.rstrip() in end_section:
                                    bVMODLData = False
                                yield line.rstrip()

                    outdict.update(self._parse_vmodl(health_status_gen(f)))

                def process_lsom_health(f):
                    heaps = {}
                    bHeaps = False
                    for line in f.readlines():
                        # Right now just interested in heap stats
                        if not bHeaps:
                            if line.rstrip() == 'Heap Stats:':
                                bHeaps = True
                        else:
                            if line.rstrip() == '===========================================================':
                                bHeaps = False
                            elif line.rstrip() == '-----------------------------------------------------------':
                                pass
                            else:
                                try:
                                    key, values = line.rstrip().split(':', 1)
                                    heaps[key] = {}
                                    for item in values.split(','):
                                        k, v = item.split(':')
                                        heaps[key].update(
                                            {k.lstrip(): v.lstrip()}
                                        )
                                except IndexError:
                                    bHeaps = False
                    outdict.update({'Heap_Stats': heaps})

                try:
                    with self.get_file('commands/python_usrlibvmwarevsanperfsvcVsanLsomHealthpyc.txt') as f:
                        # Different format because reasons!
                        process_lsom_health(f)
                except FileNotFoundError:
                    try:
                        with self.get_file(
                                'commands/python_libpython27site-packagespyMovimvsanVsanLsomHealthpyc.txt') as f:
                            process_lsom_health(f)
                    except FileNotFoundError:
                        pass

                try:
                    with self.get_file(
                            'commands/python_usrlibvmwarevsanperfsvcvsan-perfsvc-statuspyc-svc_info.txt') as f:
                        def perf_service_gen(fobj):
                            """
                            generator for perf service.
                            :param fobj:
                            :return:
                            """
                            bVMODLData = False
                            for line in fobj.readlines():
                                if not bVMODLData:
                                    if line.rstrip() == '--------Perf Service Node Information--------':
                                        bVMODLData = True
                                        yield '=== 1. Perf Service Node Inforomation ==='
                                else:
                                    if line.rstrip() in [']', '}']:
                                        bVMODLData = False
                                    yield line.rstrip()

                        outdict.update(self._parse_vmodl(perf_service_gen(f)))
                except FileNotFoundError:
                    pass  # Skip errors here.
                self._vsan_health = outdict
            except FileNotFoundError:
                raise NephelaiUnavailException('VSAN Health toolkit data seems to be unavailable.')
        return self._vsan_health

    def _get_localcli_parsers(self):
        """
        return K:V pairs of 'localcli filename' : func
        Override / extend this to add additional parsers.
        :return: dict
        """
        output = {}
        if self.is_vsan_enabled():  # Only bother adding these in if vsan is enabled.
            output['localcli_vsan-network-list'] = self._parse_localcli_vsan_network_list
            output['localcli_vsan-storage-list'] = self._parse_localcli_vsan_storage_list
        return output

    def get_vsan_pnics(self):
        """
        if VSAN is enabled returns the Physical interfaces on this host passing VSAN traffic.
        Returns the full understanding of the NIC (/w stats)
        relies on *switches* and *nics* functioning.

        If VSAN is disabled - return None.

        :todo: perhaps raising exception instead of returning None is correct here.
        :return: list of physical network interfaces which have the potential to carry VSAN network traffic. Or 'None'\
        if VSAN is disabled.
        """
        if self.is_vsan_enabled():
            vsan_vmknics = list(self.localcli.get('localcli_vsan-network-list', {}).keys())
            mappings = self._vmknic_to_pnic()
            # return the unique list of pnics used by VSAN vmkernel ports.
            return list(set(chain(*[mappings.get(vmknic) for vmknic in vsan_vmknics])))
        else:  # VSAN is disabled.
            return None

    def _vmknic_to_pnic(self):
        """
        return dict of vmk interfaces with value set to list of pNics being used.
        :return:
        """
        output = {}
        # setup output dict to contain a list per vmknic
        for nic in [x for x in self.nics if x.startswith('vmk')]:
            output[nic] = []

        for switch in self.switches:
            if self.switches.get(switch, {}).get('type', None) == 'vSwitch':
                # Regular vSwitch
                for portgroup in list(self.switches.get(switch).get('portgroups', {}).keys()):
                    # Is there a vmknic using this port group?
                    vmknics = []
                    for proto in self._VALID_IP_PROTO:
                        vmknics = vmknics + [nic for nic in self.nics
                                             if self.nics.get(nic).get(proto, {}).get('portgroup') == portgroup]
                    vmknics = set(vmknics)  # Remove duplicates.
                    if len(vmknics) > 0:
                        # So there are one or more vmknics using this port group.
                        pnics = list(
                            self.switches.get(switch).get('portgroups').get(portgroup).get('uplinks', {}).keys())
                        for nic in vmknics:
                            output[nic] = output[nic] + pnics
                    else:
                        pass  # Skip this port group.
            elif self.switches.get(switch, {}).get('type', None) == 'DVS':
                # distributed virtual switch.
                for dvportid in list(self.switches.get(switch).get('dvports', {}).keys()):
                    # Get the list of clients which are vmkernel interfaces.
                    vmknics = [x for x in self.switches.get(switch).get('dvports', {}).get(dvportid).get('client')
                               if x.startswith('vmk') and x in self.nics]
                    if len(vmknics) > 0:
                        for nic in vmknics:
                            output[nic] = output[nic] + list(self.switches.get(switch, {}).get('uplinks', {}).keys())
        return output

    def _vmknic_to_switch(self):
        """
        return list of tuples where x,y x = vmk interface y = switch name.
        :return:
        """
        output = []
        nics = [x for x in self.nics if x.startswith('vmk')]

        for switch in self.switches:
            if self.switches.get(switch, {}).get('type', None) == 'vSwitch':
                # Regular vSwitch
                for portgroup in list(self.switches.get(switch).get('portgroups', {}).keys()):
                    # Is there a vmknic using this port group?
                    vmknics = []
                    for proto in self._VALID_IP_PROTO:
                        vmknics = vmknics + [nic for nic in self.nics
                                             if self.nics.get(nic).get(proto, {}).get('portgroup') == portgroup]
                    vmknics = set(vmknics)  # Remove duplicates.
                    if len(vmknics) > 0:
                        # So there are one or more vmknics using this port group.
                        pnics = list(
                            self.switches.get(switch).get('portgroups').get(portgroup).get('uplinks', {}).keys())
                        for nic in vmknics:
                            output.append((nic, switch))
                    else:
                        pass  # Skip this port group.
            elif self.switches.get(switch, {}).get('type', None) == 'DVS':
                # distributed virtual switch.
                for dvportid in list(self.switches.get(switch).get('dvports', {}).keys()):
                    # Get the list of clients which are vmkernel interfaces.
                    vmknics = [x for x in self.switches.get(switch).get('dvports', {}).get(dvportid).get('client')
                               if x.startswith('vmk') and x in self.nics]
                    if len(vmknics) > 0:
                        for nic in vmknics:
                            output.append((nic, switch))
        return output

    def _link_network_dev(self, dictionary):
        """
        given dictionary return dict where uplinks or client is replaced with link to pNIC dict where possible.
        :return: dict
        """
        if 'client' in dictionary:  # Dvswitch
            if dictionary.get('client') in list(self.nics.keys()):
                dictionary['client'] = {dictionary.get('client'): self.nics.get(dictionary.get('client'))}
        elif 'uplinks' in dictionary:
            if dictionary.get('uplinks') is None:
                dictionary.pop('uplinks')
            else:
                uplinks = dictionary.get('uplinks').split(',')
                uplink_dict = {}
                for uplink in uplinks:
                    if uplink in self.nics:
                        uplink_dict.update({uplink: self.nics.get(uplink)})
                if len(uplink_dict) > 0:
                    dictionary['uplinks'] = uplink_dict
        return dictionary

    def _parse_esxcfg_vmknic(self):
        """
        parses the content of commands/esxcfg-vmknic_-l.txt
        :return:
        """
        with self.get_file('commands/esxcfg-vmknic_-l.txt') as f:
            content = f.readlines()
        content = [x.rstrip() for x in content]
        """
        Following regex covers ESXi 5.5 / 6.0 esxcfg-vmknic interface formatting.
        both broadcast and netstack fields are optional.
        """
        vmknic_regex = re.compile(
            '(?P<vmk>vmk[0-9]+)\s+' +  # This matches 'vmk' Followed by any sequence of base10
            '(?P<portgroup>.*?)\s+' +  # This matches *Anything* minimally (So maximizing the number of spaces which
            # Follow between it and the next field).
            '(?P<ipversion>IPv[0-9]+)\s+' +  # This matches 'IPv' followed by any sequence of base10
            '(?P<ipaddr>[0-9a-f.:]+)\s+' +  # This matches any sequence of hex and '.:' chars (IPv4 / IPv6) addrs very generically.
            '(?P<netmask>[0-9.]+)\s+' +  # This matches IPv4 or numeric
            '(?P<broadcast>[0-9.]+)?\s+' +  # OPTIONAL (not present in ipv6) matches ipv4 addrs or numeric
            '(?P<macaddr>([0-9a-f]{2}:){5}[0-9a-f]{2})\s+' +  # This matches 6 pairs of 2 hex digits split by ':'
            '(?P<mtu>\d+)\s+(?P<tsomss>\d+)\s+' +  # mtu and tsomss are integers only
            '(?P<enabled>true|false)\s+' +  # This matches either the string 'true' or 'false' only.
            '(?P<type>[A-Z]+(, )?[A-Z]+)' +  # This matches all uppercase string optionally split by ', ' (once)
            '(\s+(?P<netstack>[^\s]+))?'  # OPTIONAL vmkernel tcpstack matches anything but spaces
        )
        # First line is a header - and a give-away as far as version (NetStack field)
        output = {}
        """
        output like:
        { vmk0: { ipv4: {}, ipv6: {}}}
        """
        if content[0].startswith('Interface') and len(content) > 1:
            for line in content[1:]:
                match = vmknic_regex.search(line)
                if match:
                    tmp = match.groupdict()
                    if tmp.get('vmk') not in output:
                        output[tmp.get('vmk')] = {}
                    if tmp.get('ipversion') not in output.get(tmp.get('vmk')):
                        output[tmp.get('vmk')][tmp.get('ipversion')] = {}
                    output[tmp.get('vmk')][tmp.get('ipversion')] = tmp

        return output

    def _parse_esxcfg_vswitch(self):
        """
        Parses the content of commands/esxcfg-vswitch_-l.txt
        :return:
        """
        # Read content
        SWITCH_HEADER_PREFIXS = ('Switch Name', 'DVS Name')
        PORTGROUP_HEADER_PREFIXS = ('PortGroup Name', 'DVPort ID')
        with self.get_file('commands/esxcfg-vswitch_-l.txt') as f:
            content = f.readlines()
        content = [x.rstrip() for x in content]

        switch_regex = re.compile(
            '^(?P<switchname>.*?)\s+(?P<numports>\d+)\s+(?P<usedports>\d+)\s+(?P<configuredports>\d+)\s+(?P<mtu>\d+)(\s+' +
            '(?P<uplinks>[^\s]+))?'
        )
        dvs_pg_regex = re.compile(
            '\s{2}(?P<dvportid>\d+)\s+(?P<inuse>\d+)\s+(?P<client>.*)$'
        )
        vswitch_pg_regex = re.compile(
            '\s{2}(?P<portgroupname>.*?)\s+(?P<vlanid>\d+)\s+(?P<usedports>\d+)\s+(?P<uplinks>[^\s]+)$'
        )
        output = {}
        # Parse content
        tmpSwitch = {'name': None, 'type': None}
        for line in content:
            if line.startswith(SWITCH_HEADER_PREFIXS):
                if line.startswith('Switch Name'):
                    tmpSwitch['type'] = 'vSwitch'
                elif line.startswith('DVS Name'):
                    tmpSwitch['type'] = 'DVS'
                else:
                    logging.debug('Unknown switch type {0}'.format(line))
                    tmpSwitch['type'] = 'Unknown'
            elif not (line == '') and not (line[0].isspace()):
                match = switch_regex.search(line)
                if match:
                    output[match.groupdict().get('switchname')] = self._link_network_dev(match.groupdict())
                    if tmpSwitch.get('type', None) == 'vSwitch':
                        output[match.groupdict().get('switchname')]['portgroups'] = {}
                        output[match.groupdict().get('switchname')]['type'] = 'vSwitch'
                    elif tmpSwitch.get('type', None) == 'DVS':
                        output[match.groupdict().get('switchname')]['dvports'] = {}
                        output[match.groupdict().get('switchname')]['type'] = 'DVS'
                    tmpSwitch['name'] = match.groupdict().get('switchname', None)
                else:
                    logging.debug('Problem parsing esxcfg-vswitch Problem line "{0}"'.format(line))
                    raise NephelaiParseException('Problem parsing esxcfg-vswith')
            elif line[2:].startswith(PORTGROUP_HEADER_PREFIXS):
                pass  # Port group headers - skip
            elif line == '':
                pass  # Blank line - skip
            else:
                # This should be a portgroup.
                try:
                    if tmpSwitch.get('type', None) == 'vSwitch':
                        match = vswitch_pg_regex.search(line)
                        if match:
                            output[tmpSwitch.get('name', {})]['portgroups'][
                                match.groupdict().get('portgroupname', 'unknown')] = self._link_network_dev(
                                match.groupdict())
                    elif tmpSwitch.get('type', None) == 'DVS':
                        match = dvs_pg_regex.search(line)
                        if match:
                            output[tmpSwitch.get('name', {})]['dvports'][match.groupdict().get(
                                'dvportid')] = self._link_network_dev(match.groupdict())
                except KeyError:
                    logging.debug('Something went wrong decoding PG / dvports skipping line', exc_info=True)
        return output

    def _parse_netdvs(self):
        """
        Parses content of commands/net-dvs-l.txt - file may not be present or useful  if dvsSwitches not being used.
        :return:  dict
        """
        switch_regex = re.compile(r'switch (?P<uuid>([0-9a-f]{2}[- ])+)\(etherswitch\)')

        def numSpaces(line):
            return len(line) - len(line.lstrip())

        try:
            gen = self.get_file_gen('commands/net-dvs_-l.txt')
            current_switch = ''
            current_port = ''
            output = {}
            for line in gen:
                depth = numSpaces(line)  # Num tabs
                if depth == 0:
                    sw_match = switch_regex.match(line)
                    if sw_match:
                        output[sw_match.groupdict().get('uuid').rstrip()] = {}  # New empty dict.
                        current_switch = sw_match.groupdict().get('uuid').rstrip()
                        current_port = ''  # Reset
                elif depth == 1:
                    if line.lstrip().startswith('port'):
                        tmp = line.lstrip().rstrip().rstrip(':')
                        portid = tmp.split(' ')[1]
                        current_port = portid
                        output[current_switch][current_port] = {}
                elif depth == 2:
                    if line.lstrip().startswith('com.vmware.common.port.alias'):
                        # "com.vmware.common.port.alias = Uplink 2 , 	propType = CONFIG"
                        k, v = line.split('=', 1)
                        uplink_name = v.split(',', 1)[0].lstrip().rstrip()
                        if uplink_name != '':
                            output[current_switch][current_port]['uplink_name'] = uplink_name
                    elif line.lstrip().startswith('com.vmware.common.alias') and current_port == '':
                        k, v = line.split('=', 1)
                        dvswitch_name = v.split(',', 1)[0].lstrip().rstrip()
                        if dvswitch_name != '':
                            output[current_switch]['name'] = dvswitch_name
                elif depth == 3 and current_port != '':
                    if line.lstrip().startswith('active') and not output[current_switch][current_port].get('uplink_name'):
                        k, v = line.split('=', 1)
                        uplink_list = [uplink.lstrip() for uplink in v.split(';') if uplink != '']
                        output[current_switch][current_port]['active'] = uplink_list
                    elif line.lstrip().startswith('standby') and not output[current_switch][current_port].get('uplink_name'):
                        k, v = line.split('=', 1)
                        uplink_list = [uplink.lstrip() for uplink in v.split(';') if uplink != '']
                        output[current_switch][current_port]['standby'] = uplink_list
            return output
        except FileNotFoundError:
            raise NephelaiUnavailException('Cannot find net-dvs file')

    def _parse_vmodl(self, gen):
        """
        Parses serialized vmodl datastructures into native python objects (where possible)
        "<unset>" == None
        "false" == False
        "true" == True
        "[0-9]+L" == int
        everything else is a string.
        Expects vmware-vimdump format - generator should convolve input into that format
        :param gen: generator we are reading from.
        :return: dict / list
        """

        key_regex = re.compile(r'(?P<key>[^ ]+) =[^=]')
        vmodl_regex = re.compile(r'(\((?P<vmodltype>.*)\) ((?P<listchar>\[)|(?P<dictchar>{)))')
        value_regex = re.compile(r'= (?P<value>.*)')
        title_regex = re.compile(r'==+ [0-9]+\. (?P<title>.*) ==+')
        output = {}
        stack = [output]
        breadcrumbs = []  # Not sure I need this yet - but will be useful for taking different actions per vmodl type

        def normalize_value(input_value):
            """
            Function specific to vmodl parsing
            :param input_value: string
            :return: None / False / True / int / string or input value.
            """
            output_value = input_value
            if input_value == '<unset>':
                output_value = None
            elif input_value == 'false':
                output_value = False
            elif input_value == 'true':
                output_value = True
            elif input_value.endswith('L'):  # Long
                try:
                    output_value = int(input_value.rstrip('L'))
                except ValueError:
                    pass
            else:
                try:
                    output_value = literal_eval(input_value)
                except ValueError:
                    pass
                except SyntaxError:
                    pass
            return output_value

        for line in gen:
            match = key_regex.search(line)
            vmodl_match = vmodl_regex.search(line)

            if line.startswith('==') and line.endswith('=='):
                title_match = title_regex.search(line)

                if len(stack) == 2:
                    stack.pop()  # Finish with last entry.
                elif len(stack) > 2:  # Problems!
                    raise Exception('unexpected title')

                if title_match:
                    title = title_match.groupdict().get('title')
                    if type(stack[-1]) is dict:
                        # Get next line
                        item = gen.__next__()
                        vmodl_match = vmodl_regex.search(item)
                        if vmodl_match:
                            if vmodl_match.groupdict().get('listchar'):
                                stack[-1][title] = []
                            elif vmodl_match.groupdict().get('dictchar'):
                                stack[-1][title] = {}
                            else:
                                raise Exception('Bwa?')
                        else:
                            raise Exception('I am a confuse')
                        stack.append(stack[-1][title])
                pass  # Skip titles
            elif match:
                key = match.groupdict().get('key')
                if vmodl_match:
                    breadcrumbs.append(vmodl_match.groupdict().get('vmodltype'))
                    if vmodl_match.groupdict().get('listchar'):  # list
                        if not line.rstrip(',').endswith(']'):
                            stack[-1][key] = []
                            stack.append(stack[-1][key])

                    elif vmodl_match.groupdict().get('dictchar'):  # Dict
                        if not line.rstrip(',').endswith('}'):
                            stack[-1][key] = {}
                            stack.append(stack[-1][key])

                else:
                    value_match = value_regex.search(line)
                    if value_match:
                        value = value_match.groupdict().get('value', None)
                        value = normalize_value(value.rstrip(','))
                        stack[-1][key] = value

            elif (line.rstrip(',').endswith('}') or line.rstrip(',').endswith(']')) and (len(stack) > 1):
                breadcrumbs.pop()
                stack.pop()
            elif vmodl_match:  # vmodl type /wout key
                breadcrumbs.append(vmodl_match.groupdict().get('vmodltype'))
                if vmodl_match.groupdict().get('listchar'):  # list
                    if not line.endswith('],'):
                        try:
                            if type(stack[-1]) == list:  # Should be list.
                                stack[-1].append([])
                                stack.append(stack[-1][-1])
                        except IndexError:
                            output = []
                            stack.append(output)
                elif vmodl_match.groupdict().get('dictchar'):  # Dict
                    if not line.endswith('},'):
                        try:
                            if type(stack[-1]) == list:
                                stack[-1].append({})
                                stack.append(stack[-1][-1])
                        except IndexError:
                            output = {}
                            stack.append(output)
            else:  # Exception!
                if len(stack) > 0:
                    if type(stack[-1]) is list:
                        value = line.lstrip().rstrip(',')
                        value = normalize_value(value)
                        stack[-1].append(value)
                    elif type(stack[-1]) is dict:
                        pass
                    else:
                        print(stack)
                        raise Exception('Problem processing line {0}'.format(line))
                else:
                    pass  # Skip lines that don't conform.

        return output

    def _parse_nicinfo(self):
        """
        Parses the content of commands/nicinfo.sh.txt
        :return:
        """
        if self._nicinfo is None:
            try:
                nic_regex = re.compile(
                    '(?P<devname>[^\s]+)\s+(?P<pciid>[^\s]+)\s+(?P<driver>[^\s]+)\s+(?P<adminstatus>[^\s]+)?\s+' +
                    '(?P<linkstatus>[^\s]+)\s+(?P<speed>[\d]+)\s+(?P<duplex>[^\s]+)\s+(?P<mac>[0-9a-f:]+)\s+' +
                    '(?P<mtu>[\d]+)\s+(?P<desc>.*)'
                )
                """
                Example dict output from regex:
                {'adminstatus': 'Up',   <- optional
                 'desc': 'Cisco Systems Inc Cisco VIC Ethernet NIC',
                 'devname': 'vmnic0',
                 'driver': 'enic',
                 'duplex': 'Full',
                 'linkstatus': 'Up',
                 'mac': '00:25:b5:3e:a0:0d',
                 'mtu': '9000',
                 'pciid': '0000:06:00.0',
                 'speed': '20000'}
                """
                with self.get_file('commands/nicinfo.sh.txt') as f:
                    content = f.readlines()
                content = [x.rstrip() for x in content]
                if content[0] != 'Network Interface Cards Information.':
                    raise NephelaiParseException('Unexpected content in nicinfo')
                nics = {}
                stats_start = 4
                for i, line in enumerate(content[4:]):
                    if line == '':
                        break
                    match = nic_regex.search(line)
                    if match:
                        nics[match.groupdict().get('devname', 'unknown')] = match.groupdict()
                        stats_start += 1

                # Now process the ethtool output
                breadcrumbs = []  # Keep track of breadcrumbs
                for entry in [y.split('   ') for y in content[stats_start:]]:
                    if entry != ['']:  # Blank line.
                        if len(entry) == 1:
                            if entry[0][:4] == 'NIC:':  # New NIC approaches
                                k, v = entry[0].split(':', 1)
                                nic_name = v.strip()
                                breadcrumbs = [nic_name]  # Reset the breadcrumbs
                                if nics.get(nic_name, None) is None:  # Does it exist.
                                    raise NephelaiParseException("Nic not present to insert stats {0}".format(nic_name))
                            elif entry[0][-1] == ':':  # Not error message hopefully.
                                new_key = entry[0][:-1]
                                if new_key.endswith('for ' + breadcrumbs[0]):
                                    new_key = new_key.split('for')[0].strip()
                                breadcrumbs = breadcrumbs[:1]
                                breadcrumbs.append(new_key)
                                nics.get(breadcrumbs[0], {})[new_key] = {}
                        elif len(entry) > 1:
                            depth = len(entry)
                            if depth == len(breadcrumbs):  # Correct depth
                                item = entry[-1]
                                k, v = item.split(':', 1)
                                v = v.strip()
                                k = k.strip()
                                if v != '':
                                    try:
                                        tmpdict = reduce(dict.__getitem__, breadcrumbs, nics)
                                        if isinstance(tmpdict, dict):
                                            tmpdict.update({k: self._normalize_localcli(v)})
                                        else:
                                            raise NephelaiParseException('Found unexpected type in nics dict. {0}, {1}'
                                                                         .format(type(tmpdict), breadcrumbs))
                                    except KeyError:
                                        print(nics)
                                        raise
                                else:
                                    tmpdict = reduce(dict.__getitem__, breadcrumbs, nics)
                                    tmpdict.update({k: {}})
                                    breadcrumbs.append(k)

                            elif depth > len(breadcrumbs):  # Shouldn't happen I think?
                                pass  # Skip it?
                                """
                                raise NephelaiParseException('depth {0} > breadcrumbs {1} ({2})'.format(
                                    depth,
                                    len(breadcrumbs),
                                    breadcrumbs
                                ))
                                """
                            else:  # Back up N steps
                                breadcrumbs = breadcrumbs[:depth]

                self._nicinfo = nics
                return self._nicinfo
            except:
                self._nicinfo = {}
                raise
        else:
            return self._nicinfo

    def _normalize_localcli(self, value):
        """
        Given value from localcli
         if int, return int
         if float return float
         if bool return bool
         etc...
        :param value:
        :return: value, or decoded value
        """
        try:
            if value == 'true':
                return True
            elif value == 'false':
                return False
            elif value == '':
                return None
            elif value.isdigit():
                try:
                    return int(value)
                except ValueError:
                    raise
            else:
                try:
                    return float(value)
                except ValueError:
                    raise
        except:
            return value

    def _parse_localcli_vsan_network_list(self):
        """
        Function to parse the content of 'localcli_vsan-network-list.txt'
        :return: list of dicts.
        """
        with self.get_file('commands/localcli_vsan-network-list.txt') as f:
            content = f.readlines()
        """
        Example content:
        Interface:
           VmkNic Name: vmk2
           IP Protocol: IPv4
           Interface UUID: f2bae454-c847-9435-5fcd-b083fed28255
           Agent Group Multicast Address: 224.2.3.4
           Agent Group Multicast Port: 23451
           Master Group Multicast Address: 224.1.2.3
           Master Group Multicast Port: 12345
           Multicast TTL: 5

        Interface:
           VmkNic Name: vmk3
           IP Protocol: IPv4
           Interface UUID: febae454-484e-6215-5d33-b083fed28255
           Agent Group Multicast Address: 224.2.3.4
           Agent Group Multicast Port: 23451
           Master Group Multicast Address: 224.1.2.3
           Master Group Multicast Port: 12345
           Multicast TTL: 5

        Summary:
        String 'Interface:' then entry
        Entry is K:V pairs split on ':'
        """
        output = {}
        if_name = 'Unknown'
        for line in content:
            cleaned = line.rstrip()
            if (cleaned != '') and not (cleaned == 'Interface:'):  # Non blank, not interface
                key, value = cleaned.lstrip().split(':', 1)
                if key == 'VmkNic Name':
                    if_name = value.lstrip()
                    output[if_name] = {}
                output[if_name][key] = self._normalize_localcli(value.lstrip())
        return output

    def _parse_localcli_vsan_storage_list(self):
        """
        Function to parse the content of 'localcli_vsan-storage-list.txt'
        :return:
        """
        with self.get_file('commands/localcli_vsan-storage-list.txt') as f:
            content = f.readlines()  # Read the whole thing at once.
        """
        Entries look like so:
        naa.5000cca07233a7f8:
           Device: naa.5000cca07233a7f8
           Display Name: naa.5000cca07233a7f8
           Is SSD: false
           VSAN UUID: 52139014-7f0a-c24a-847b-624aa52123a9
           VSAN Disk Group UUID: 5250b3d9-88a2-6671-f61e-cefd4491f69f
           VSAN Disk Group Name: naa.5002538454c6da70
           Used by this host: true
           In CMMDS: true
           Checksum: 6264992847805990079
           Checksum OK: true
           Emulated DIX/DIF Enabled: false

        To summarize:
        No whitespace terminated /w ':$' == Dev name
        Rest is K/V pair split on ':'
        """
        output = {}
        dev_name = 'Unknown'
        for line in content:
            cleaned = line.rstrip()
            if cleaned != '' and not cleaned.startswith('VsanUtil'):  # Not blank line not error.
                if not cleaned[0:3].isspace() and cleaned[-1] == ':':
                    dev_name = cleaned.rstrip(':')  # Remove trailing :
                    output[dev_name] = {}  # Make empty dict for our content in later lines.
                else:  # Not blank, leading 3 are spaces - this is a k/v pair
                    key, value = cleaned.split(':', 1)
                    output.get(dev_name)[key.lstrip()] = self._normalize_localcli(value.lstrip())
        return output

    def validate(self):
        """
        Tests bundle to see if it is an ESXi log bundle

        Looks for valid content in *commands/vmware_-vl.txt*

        :return: True / False
        """
        """
        How to detect vm-support?
        1) Dir structure?
        2) README File contents @ root of vm-support?
        3) commands/vmware_-vl.txt ?
        """
        try:
            with self.get_file('commands/vmware_-vl.txt') as f:
                content = f.readlines()
                if len(content) > 0:
                    if content[0].startswith('VMware ESXi'):
                        return True
        except:  # Swallow errors
            return False

    def _read_json(self, rel_filename):
        """
        Open json file in json/ of vm-support and return python object.
        :param rel_filename: relative path to json file.
        :return: python object / list / dict
        """
        with self.get_file(rel_filename) as f:
            try:
                return json.load(f)
            except ValueError:  # Should be json.JSONDecodeError - but that is 3.5 only and want to target 3.4 also.
                f.seek(0)  # Reset.
                max_tries = 100
                current_try = 0
                while True:
                    f.readline()  # Skip a line.
                    try:
                        return json.load(f)
                    except ValueError:
                        if current_try <= max_tries:
                            current_try += 1
                            pass # Next line
                        else:
                            raise NephelaiUnavailException("{} unavailable {}".format(rel_filename, 'Malformed JSON'))
            except Exception as e:
                raise NephelaiUnavailException("{} unavailable {}".format(rel_filename, str(e)))

    def find_vmxs(self):
        """
        Scan log bundle for .vmx files - return list of VMBundle instances

        :todo: Currently this is expensive.
        :return: list of VMBundle instances
        """
        vmxs = []
        if os.path.exists(os.path.join(self.path, 'vmfs', 'volumes')):
            for root, dirs, files in os.walk(os.path.join(self.path, 'vmfs', 'volumes')):
                for vmx in [x for x in files if x.endswith(('.vmx', '.vmx.gz', '.vmx.bz2'))]:  # Do we find a .vmx file?
                    logging.debug('Found VM config dir {0}, vmx {1}'.format(root, vmx))
                    vmxs.append(VMBundle(path=root, rootBundle=self, vmx_name=vmx))
        return vmxs

    def _parse_localcli_vsan_cluster_list(self):
        """
        return cleaned up dict of 'localcli_vsan-cluster-get info.
        :return: dict or None
        """
        outdict = {}
        blacklist = ['Cluster Information']
        try:
            lines = list(self.get_file_lines_iter('commands/localcli_vsan-cluster-get.txt'))
            if not lines[1].rstrip() in ['VSAN Clustering is not enabled on this host',
                                         'Virtual SAN Clustering is not enabled on this host']:
                for line in lines:
                    tmp = line.lstrip().split(':')
                    if tmp[0] not in blacklist:
                        if tmp[0] == 'Current Local Time':
                            outdict[tmp[0]] = ':'.join(tmp[-3:]).strip()
                        elif tmp[0] == 'Sub-Cluster Member UUIDs':
                            outdict[tmp[0]] = [x.lstrip() for x in tmp[1].rstrip().split(',')]  # List of UUID's
                        else:
                            outdict[tmp[0]] = tmp[1].strip()
                return outdict
            else:
                return None  # VSAN is disabled
        except OSError:
            return None  # VSAN is disabled

    def is_vsan_enabled(self):
        """
        Checks for VSAN - parses *commands/localcli_vsan-cluster-get.txt*
        :return: Bool True / False
        """
        if not self._vsan_cluster_info:  # No cached data
            tmp = self._parse_localcli_vsan_cluster_list()
            if tmp:
                # Cache data and return True
                self._vsan_cluster_info = tmp
                return True
        else:
            return True  # Cached data so return True
        return False


class VCenterBundleBase(Logbundle):
    """
    VC Log bundle.
    This is going to be based on the appliance bundle first - with windows VC being a subclass.
    Starting /w 6.0 for consistency.

    :param path: Path is required - this is a directory which contains one or more files which constitute the log\
     bundle.
    """

    def __init__(self, path=None, **kwargs):
        self._bundleInfo = None  # this is a pre-req for validation
        super().__init__(path, **kwargs)
        self.bundleType = "vCenter"
        self._platform = "unknown"  # Windows vs Linux
        self._hostname = None
        self._logs = None
        self._moref_map = None
        self.LOG_SIGNATURES = [  # This is for the moref processor - stored here to make overriding easier.
            ('[VpxdHostSync] Synchronizing host: host-', re.compile(
                r'.*\[VpxdHostSync\] Synchronizing host: (?P<hostid>host-\d+) \((?P<hostname>[^,]+), (?P<hostip>[^\)]+)\)')),
            ('[VpxdHostSync] Synchronizing host:', re.compile(
                r'.*opID=HB-(?P<hostid>host-\d+).*\[VpxdHostSync\] Synchronizing host: (?P<hostname>[^ ]+) \((?P<hostip>[^\) ,]+)\)')),
            ('Reloading vm [vim.VirtualMachine:',
             re.compile(r'.*Reloading vm \[vim\.VirtualMachine:(?P<vmid>vm-\d+),(?P<vmname>[^\]]+)\].*')),
            ('[VpxdInvtVm] Saving fields for',
             re.compile(r'.*\[VpxdInvtVm\] Saving fields for (?P<vmname>[^ ]+) \(/vpx/(?P<vmid>vm/#\d+)/\).*')),
            ('[VpxdVAppUtil] Triggering async state refresh on', re.compile(
                r'.*\[VpxdVAppUtil\] Triggering async state refresh on (?P<vmid>vm-\d+) \((?P<vmname>[^\)]+)\).*')),
            ('Initializing min EVC key for VM', re.compile(
                r'.*Initializing min EVC key for VM (?P<vmname>[^ ]+) \[vim\.VirtualMachine:(?P<vmid>vm-\d+)\]')),
            ('Checking admissibility of VM', re.compile(
                r'.*Checking admissibility of VM \[vim\.VirtualMachine:(?P<vmid>vm-\d+),(?P<vmname>[^\]]+)\].*')),
            (', vmId [', re.compile(
                r'.*\[EventManagerMo\] Event.* vmId \[(?P<vmid>\d+)=(?P<vmname>[^\]]+)\],.* hostId \[(?P<hostid>\d+)=(?P<hostname>[^\]]+)\].*')),
            (', hostId [',
             re.compile(r'.*\[EventManagerMo\] Event.* hostId \[(?P<hostid>\d+)=(?P<hostname>[^\]]+)\].*')),
        ]

    def validate(self):
        try:
            return 'vc-support' in self.bundleInfo.get('Command line', '')
        except Exception as e:
            logging.warning('{0} failed validation {1}'.format(self.path, e), exc_info=True)
            return False

    @property
    def bundleInfo(self):
        """
        Content of the README file in a vc-support - which manifests etc were ran during bundle creation etc.

        :return: dict representation of the content of *README* file in vm-support.
        """
        if self._bundleInfo is None:
            try:
                output = {}
                with self.get_file('README') as f:
                    content = f.readlines()
                for line in content[:5]:
                    try:
                        key, value = line.rstrip().split(':', 1)
                        value = value.lstrip()
                        if key == 'Options':
                            value = literal_eval(value)
                            if 'manifests' in value:
                                value['manifests'] = value.get('manifests', '').split(' ')
                        elif key == 'Captured on':
                            try:
                                value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
                            except:
                                pass
                        output[key] = value
                    except ValueError:
                        pass
                self._bundleInfo = output
                return self._bundleInfo
            except:
                self._bundleInfo = {}
                logging.debug('Problem building bundleInfo.', exc_info=True)
        else:
            return self._bundleInfo

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
    def moref_map(self):
        """
        Dict
        *K:V pairs of K = moref V = String describing the moref (VM name / Host Name etc)
        :return:  dict
        """
        if self._moref_map is None:
            self._moref_map = self._moref_scan()

        return self._moref_map

    def _moref_scan(self):
        """
        Internal function which scans vpxd logs.
        :return: dict of mappings
        """
        output = {}
        for vpxd_file in self.logs.get('vpxd'):
            with self.get_file(vpxd_file) as f:
                for line in f.readlines():
                    results = self._moref_process_line(line)
                    if results:
                        if results.get('moref') not in output:
                            output[results.get('moref')] = results.get('description')

        for profile_file in self.logs.get('vpxd-profiler'):
            with self.get_file(profile_file) as f:
                for line in f.readlines():
                    if ('/HostStatus/HostId' in line) and ('Name' in line):
                        parts = line.split('/')
                        if parts[3].startswith('host-'):
                            output[parts[3]] = parts[-1].split(' ')[-1].rstrip()

        return output

    def _moref_append_ref(self, results):
        pass

    def _moref_process_line(self, line):
        """
        line processor for the moref scanner.
        :param line:  string
        :return:  dict if detected relationship or none
        """
        output = None
        for substr, regex in self.LOG_SIGNATURES:
            if substr in line:
                match = regex.match(line)
                if match:
                    gdict = match.groupdict()

                    if 'vmid' in gdict:
                        moid = gdict.get('vmid')
                        moid = moid.replace('vm/#', 'vm-')
                        if not moid.startswith('vm-'):
                            moid = 'vm-' + moid
                        if 'vmname' in gdict:
                            output = {'moref': moid, 'description': gdict.get('vmname')}

                    elif 'hostid' in gdict:
                        moid = gdict.get('hostid')
                        if not moid.startswith('host-'):
                            moid = 'host-' + moid
                        if 'hostname' in gdict:
                            output = {'moref': moid, 'description': gdict.get('hostname')}
        return output

    def _get_log_sources(self):
        """
        return list of paths to find logs in.
        :return:
        """
        if self.platform == 'Windows':
            return ['ProgramData/VMware/vCenterServer/logs/vmware-vpx']
        elif self.platform == 'Linux':
            return ['var/log/vmware/vpxd']

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

            SOURCES = self._get_log_sources()

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

            def sorting_key(filename):
                try:
                    match = log_filename_regex.match(filename)
                    if match:
                        if match.groupdict().get('suffix'):
                            return int(match.groupdict().get('suffix').strip('-'))
                        else:
                            return -1
                    return filename
                except:
                    return filename

            for log in self._logs:
                self._logs[log].sort(key=sorting_key)

        return self._logs


class VCenter55Bundle(VCenterBundleBase):
    """
    Support for older vCenter 5.5 bundles.
    Doing the inheritance this way to make future  (vsphere-2016 / 2017 etc) changes easier as 5.5 Drops to EOL
    """

    @property
    def bundleInfo(self):
        return None

    def _get_log_sources(self):
        """
        return list of paths to find logs in.
        :return:
        """
        if self.platform == 'Windows':
            return ['Logs/vpxd/']
        elif self.platform == 'Linux':
            return ['var/log/vmware/vpxd']

    @property
    def platform(self):
        if self._platform == 'unknown':
            try:
                with self.get_file('Config/systeminfo.txt') as f:
                    self._platform = 'Windows'  # Just checking I can open the file.
            except FileNotFoundError:
                self._platform = 'Linux'
        return self._platform

    def validate(self):
        """

        :return:
        """
        with self.get_file('vc-support-ver.txt') as f:
            line = f.readline()
            if line.startswith('5'):
                return True

        return False


def ESXBundle(*args, **kwargs):
    """
    Constructor for figuring out the version of ESXi and returning the correct Object.
    :param args:
    :param kwargs:
    :return: instance of ESXBundleBase or a child therof
    """
    return ESXBundleBase(*args, **kwargs)


def VCBundle(*args, **kwargs):
    """
    Constructor for figuring out Windows vs Linux vs Container and version of vCenter log bundle.
    :param args:
    :param kwargs:
    :return: instance of VCBundleBase or a child therof
    """
    return VCenterBundleBase(*args, **kwargs)


def is_path_esx_bundle(path, **kwargs):
    """
    checks if a path is a valid bundle
    :param kwargs:
    :param path:
    :return: ESXBundle object or None
    """
    vmsup_path_regex = re.compile('^(?P<start>.*)/(?P<vmsup>esx-(?P<hostname>[0-9a-zA-Z\-_.]+?)-20[0-9]{2}[^/]+)/?$')
    vmsup_path_inside_regex = re.compile(
        '^(?P<start>.*)/(?P<vmsup>esx-(?P<hostname>[0-9a-zA-Z\-_.]+?)-20[0-9]{2}[^/]+)(/.+)?$')
    abspath = os.path.abspath(path)
    if os.path.isdir(abspath):
        match = vmsup_path_inside_regex.match(abspath)
        if match:
            vmsup_path = os.path.sep.join(match.groups()[:2])
            try:
                return ESXBundle(path=vmsup_path, **kwargs)
            except NephelaiValidateException:
                return None

    return None
