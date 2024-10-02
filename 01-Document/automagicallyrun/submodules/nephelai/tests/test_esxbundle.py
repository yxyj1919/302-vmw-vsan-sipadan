import unittest
import sys
import os
import io
import datetime
sys.path.insert(0,os.path.abspath('../'))
import xml.etree.cElementTree as ElementTree

from nephelai.bundle import ESXBundleBase, VMBundle
from nephelai.util import CachingDict
from nephelai.exceptions import NephelaiBaseException, NephelaiValidateException, NephelaiParseException
from nephelai.exceptions import NephelaiUnavailException, NephelaiVersionException, NephelaiDisabledException



class TestESXBundleMethods(unittest.TestCase):
    """
    I would like to cover:
    the properties
    hostname
    version
    esxcfg_info
    nics
    switches
    bundleInfo
    cmmds
    localcli
    logs
    vm_list
    vsan_cluster_info
    """

    def setUp(self):
        """
        I'm going to need an actual vm-support here....
        :return:
        """
        valid_bundle = '/media/rmurray/wd/vm-supports/vsan-metro/esx-HWHLESXIMGPR01-2015-06-23--14.32/'
        self.test_instance = ESXBundleBase(path=valid_bundle)  # Lets use the test directory as our log bundle.


    def test_hostname(self):
        self.assertTrue(type(self.test_instance.hostname) == str)
        self.assertTrue(len(self.test_instance.hostname) > 1)

    def test_version(self):
        # Check for keys:
        self.assertListEqual(sorted(['Friendly','buildnumber','maint','major','minor']), sorted(self.test_instance.version.keys()))
        # check for values:
        self.assertTrue((type(self.test_instance.version.get('Friendly')) == str ) and
                        (self.test_instance.version.get('Friendly').startswith('VMware ESXi')))
        for key in ['buildnumber','maint','major','minor']:
            self.assertTrue(type(self.test_instance.version.get(key)) is int)

    def test_esxcfg_info(self):
        # TODO - more here but hard to be 100% sure any vm-support meets things..
        self.assertTrue(type(self.test_instance.esxcfg_info) == ElementTree.ElementTree)

    def test_nics(self):
        """
        Assumes at least 1 vmk# and 1 vmnic# - should be safe-ish assumption if we somehow got a vm-support out?
        """
        self.assertTrue(type(self.test_instance.nics) == dict)
        self.assertTrue(len([nic for nic in list(self.test_instance.nics.keys()) if nic.startswith('vmk')]) >= 1)
        self.assertTrue(len([nic for nic in list(self.test_instance.nics.keys()) if nic.startswith('vmnic')]) >= 1)
        candidate_vmk = [nic for nic in list(self.test_instance.nics.keys()) if nic.startswith('vmk')][0]
        candidate_vmnic = [nic for nic in list(self.test_instance.nics.keys()) if nic.startswith('vmnic')][0]
        self.assertTrue(type(self.test_instance.nics.get(candidate_vmk)) == dict)
        self.assertTrue(type(self.test_instance.nics.get(candidate_vmnic)) == dict)

        for key in list(self.test_instance.nics.get(candidate_vmk).keys()):
            self.assertTrue(key in self.test_instance._VALID_IP_PROTO)  # Valid protocol?
            self.assertTrue(type(self.test_instance.nics.get(candidate_vmk).get(key)) == dict)
            self.assertListEqual(sorted(['ipversion', 'macaddr', 'vmk', 'enabled', 'ipaddr', 'portgroup',
                                         'broadcast', 'netmask', 'tsomss', 'netstack', 'mtu', 'type']),
                                 sorted(self.test_instance.nics.get(candidate_vmk).get(key)))

        self.assertTrue(type(self.test_instance.nics.get(candidate_vmnic)) == dict)
        self.assertTrue(self.test_instance.nics.get(candidate_vmnic).get('devname') == candidate_vmnic)

    def test_switches(self):
        """
        Assumes at least 1 switch
        :return:
        """
        self.assertTrue(type(self.test_instance.switches) == dict)
        self.assertTrue(len(list(self.test_instance.switches.keys())) > 1)
        test_switch = list(self.test_instance.switches.keys())[0]  # Just pick the first one
        self.assertTrue(self.test_instance.switches.get(test_switch).get('type') in ['DVS','vSwitch'])

    def test_bundleInfo(self):
        """
        Looks for a dict and a datetime in 'Captured On'
        :return:
        """
        self.assertTrue(type(self.test_instance.bundleInfo) == dict)
        self.assertTrue(type(self.test_instance.bundleInfo.get('Captured on')) == datetime.datetime)

    def test_localcli(self):
        """
        So, this should be a nephelai.util.CachingDict
        There should be a non-zero number of keys.
        Testing if the caching is working is... tricky without making VERY large assumptions about where the tests are
        being executed..

        :return:
        """
        self.assertTrue(type(self.test_instance.localcli) == CachingDict)
        self.assertTrue(len(list(self.test_instance.localcli.keys())) > 1)

    def test_cmmds(self):
        """
        should only run this if VSAN is enabled...

        :return:
        """
        if self.test_instance.is_vsan_enabled():
            self.assertTrue(type(self.test_instance.cmmds) == list)
            types = set([type(x) for x in self.test_instance.cmmds])
            obj_types = set([x.get('type') for x in self.test_instance.cmmds])
            self.assertTrue(len(types) == 1)
            for item in ['SUB_CLUSTER', 'DOM_OBJECT', 'DISK', 'NODE']:
                self.assertTrue(item in obj_types)
        else:  # VSAN disabled.
            self.assertRaises(NephelaiDisabledException, len(self.test_instance.cmmds))

    def test_logs(self):
        """
        Make sure all the files can be opened and are io.BufferedIOBase
        :return:
        """
        attr_list = ['fileno', 'readline', 'read', 'seek']
        for log in self.test_instance.logs:
            for rel_path in self.test_instance.logs.get(log):
                """
                This doesn't work in 2.x ... blah
                self.assertIsInstance(self.test_instance.get_file(rel_path), io.BufferedIOBase)
                """
                test_obj = self.test_instance.get_file(rel_path)
                for attr in attr_list:
                    self.assertTrue(test_obj, attr)

    def test_vm_list(self):
        """

        :return:
        """
        if len(self.test_instance.vm_list) > 0:
            self.assertTrue(all([isinstance(x,VMBundle) for x in self.test_instance.vm_list]))

    def test_vsan_cluster_info(self):
        if self.test_instance.is_vsan_enabled():
            self.assertTrue(type(self.test_instance.vsan_cluster_info) == dict)
        else:
            self.assertRaises(NephelaiDisabledException, list(self.test_instance.vsan_cluster_info.keys()))