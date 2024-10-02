#!/usr/bin/env python3
"""
Prototype for re-written automagicallyrun utility.
Original utility: eturra@vmware.com git.eng.vmware.com/gss-eturra-automagically-run.git
This version: rmurray@vmware.com & eturra@vmware.com

This utility is designed to allow quick access to a set of utilities which are built alongside
various versions of VMware software.
It is intended for use in the GSS CSP environment and makes several enviromental assumptions.
But in general - it likely works on any standard linux system inside the VMware network which has
the requisite /build mounts.

There is a configuration file in JSON format which defines which applications are supported.
And provides instructions on how to open each application for a variety of builds.

Users can either:
1) run this script from inside an ESXi support bundle for it to auto-detect the correct
build number.
2) Run this script from anywhere for the set of utliities which grab the 'latest' build of a given set
of criteria
3) Run this script with the '-b' option which will let the user override and select a specific build number.

Other files in the repo:
validate_cfg.py   - runs and validates the JSON configuration file. Use this after editing the cfg file
to ensure there are no typos / syntax errors etc.
test_amr.py   - Python unit test suite. Use this after editing this file to ensure no unexpected issues
are introduced.
amr.json     - default config file.

Useful info on how the LD_LIBRARY_* environment variables work:
http://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html
"""

import os
import sys
import json
import requests
import argparse
import math
import subprocess
from functools import lru_cache  # Used in front of the calls to buildweb.
from traceback import format_exc, print_exc

# Using nephelai for the ESX Bundle detection and loading the list of VIBs etc.
from nephelai.bundle import is_path_esx_bundle, ESXBundle

CFG_FILENAME = 'amr.json'  # Default config filename.

# unused here - but used in the test suite to validate the configuration file. - Should be kept up to date.
VALID_BEHAVIOURS = ['match_esxi', 'match_vib', 'latest_match_criteria', 'MESSAGE']

__version__ = '0.2'


class BuildInfoFailure(Exception):
    """
    Cannot get data on a given build for some reason
    """
    pass


class ConfigError(Exception):
    """
    Problem with the app cfg
    """
    pass


class BuildGuessFailure(Exception):
    """
    Cannot guess the correct build for some reason.
    """
    pass


def usage(additional_tags, exception_info=False):
    """
    Phone home to usage.gsstools vRLI instance.
    :param additional_tags: dict of tags to add. (k/v pairs)
    :param exception_info: Include traceback?
    :return:
    """
    from socket import gethostname

    agent_id = '45678912-ABCD-EF12-3456-ABCDEF23456'
    target_url = 'http://usage.gsstools.vmware.com:9000/api/v1/messages/ingest/{0}'.format(agent_id)

    usage_data = {
        'hostname': gethostname(),
        'username': os.getenv('USER', 'Unknown'),
        'version': __version__,
        'pwd': os.path.abspath(os.path.curdir)
    }
    if type(additional_tags) is dict:
        additional_tags.update(usage_data)
    else:
        additional_tags = usage_data  # Override

    tags = [{'name': x, 'content': y} for x, y in additional_tags.items() if y is not None]
    if not exception_info:
        txt = 'usagehit automagicallyrun user={0} command={1} build={2} exit_status={3} pwd={4}'.format(
            usage_data.get('username', 'unknown'),
            additional_tags.get('command', 'unknown'),
            additional_tags.get('build', 'unknown'),
            additional_tags.get('cmd_exit_status', 'unknown'),
            additional_tags.get('pwd'))
    else:
        txt = 'usagehit automagicallyrun - Problem:\n' + format_exc()

    message_body = {'messages': [{'text': txt, 'fields': tags}]
    }
    try:
        r = requests.post(target_url, json=message_body, timeout=5)
    except Exception as e:
        raise e
        # pass  # No worries about failures just continue.


@lru_cache()
def get_builds(**kwargs):
    """
    See: http://buildapi.eng.vmware.com/ob/help/ for API details.
    get a list of builds which match the set of criteria in kwargs. (See buildweb API for details)
    :param kwargs:
    :return:
    """
    try:
        r = requests.get(url='http://buildapi.eng.vmware.com/ob/build/', params=kwargs)
        if r.ok:
            return r.json()
        else:
            raise BuildInfoFailure('Response not ok: {0}, {1}'.format(r.status_code, r.text))
    except BuildInfoFailure as e:
        raise e
    except Exception as e:
        raise BuildInfoFailure('Exception while trying to pull data for query {0} : {1}'.format(kwargs, e))


@lru_cache()
def get_build_info(build_number):
    """
    Pull down info on a given build from VMW build infrastructure.
    :param build_number:
    :return: dict of info.
    Example response:
    {'_branch_url': '/ob/branch/vsphere60ep4/',
     '_buildflags_url': '/ob/buildflag/?build=3247720',
     '_buildmachines_url': '/ob/buildmachine/?build=3247720',
     '_buildnotes_url': '/ob/buildnote/?build=3247720',
     '_buildprogressnotes_url': '/ob/buildprogressnote/?build=3247720',
     '_buildstate_url': '/ob/buildstate/succeeded/',
     '_buildstateprogress_url': '/ob/buildstateprogress/?build=3247720',
     '_buildtags_url': '/ob/buildtags/?build=3247720',
     '_buildtree_url': 'http://build-squid.eng.vmware.com/build/mts/release/bora-3247720/',
     '_buildtype_url': '/ob/buildtype/release/',
     '_component_builds_url': '/ob/buildcomponent/?build=3247720',
     '_currenttime': '2016-11-01 06:02:12.762906',
     '_deliverables_url': '/ob/deliverable/?build=3247720',
     '_elapsed_sec': 3942.961547,
     '_incremental': False,
     '_incremental_builds_url': None,
     '_incremental_next_builds_url': None,
     '_incremental_previous_builds_url': None,
     '_localtree_url': '/ob/localtree/?build=3247720',
     '_ob_parent_builds_url': '/ob/buildcomponent/?component_buildid=3247720',
     '_parent_builds_url': '/ob/buildcomponent/?component_buildid=3247720',
     '_product_url': '/ob/product/server/',
     '_qatestresults_url': '/ob/qatestresult/?build=3247720',
     '_releasetag_url': '/ob/releasetag/?build=3247720',
     '_releasetype_url': '/ob/releasetype/GA/',
     '_requestor_url': '/ob/requestor/?build=3247720',
     '_sb_parent_builds_url': '/sb/buildcomponent/?component_buildid=3247720',
     '_storage_queue_url': '/ob/storagequeue/?build=3247720',
     '_this_resource': 'build',
     '_this_url': '/ob/build/3247720/',
     'backedup': True,
     'branch': 'vsphere60ep4',
     'bugid': None,
     'buildstate': 'succeeded',
     'buildsystem': 'ob',
     'buildtree': '/build/storage61/release/bora-3247720',
     'buildtree_size_in_mb': 28541,
     'buildtype': 'release',
     'changeset': '3885424',
     'compilation': None,
     'endtime': '2015-11-17 17:38:53.645104',
     'exit_code': 0,
     'expired': False,
     'id': 3247720,
     'keep_until': '2016-11-18 18:50:49.089067',
     'locales': 'en',
     'ondisk': True,
     'prodbuildnum': 38542,
     'product': 'server',
     'progress': None,
     'releasetype': 'GA',
     'reusable_id': None,
     'reuse_trees': False,
     'reuse_trees_tag': None,
     'saved': True,
     'scmserver': 'perforce.eng.vmware.com:1666',
     'starttime': '2015-11-17 16:33:10.683557',
     'version': '6.0.0',
     'zerocopy': False}
    :raises BuildInfoFailure:
    """
    try:
        r = requests.get('http://buildapi.eng.vmware.com/ob/build/{}'.format(build_number), timeout=5)
        if r.ok:
            return r.json()
        else:
            raise BuildInfoFailure('Response not ok: {0}, {1}'.format(r.status_code, r.text))
    except BuildInfoFailure as e:
        raise e
    except Exception as e:
        raise BuildInfoFailure('Exception while trying to pull data on build {0} : {1}'.format(build_number,
                                                                                               e))


def get_path_to_config():
    """
    return path to my configuration data.
    :return:
    """
    path, script = os.path.split(os.path.realpath(__file__))
    return os.path.join(path, CFG_FILENAME)


def get_path_to_user_tmpfs():
    """
    Return path to current logged in users tmpfs filesystem (/run/user/<uid>)
    failign that return /tmp/<username>
    TODO: If windows support is desired in the future (Why?) this will need to be
    re-worked to use os. lib for working with tmpfiles.
    :return: path to user ramdisk
    :raises FileNotfoundError if it isn't found:
    """
    uid = os.getuid()
    path = os.path.join('/run/user/', str(uid))
    if os.path.exists(path):
        return path
    else:
        alt_path = os.path.join('/tmp/', os.getenv('USERNAME'))
        if os.path.exists(alt_path):
            return alt_path
        else:
            os.mkdir(alt_path)
            return alt_path


class Runner:
    """
    Class for executing utliities per loaded config.

    CFG looks like:
    {
        "Application_Name": "foo",
        "behaviour": "match_vib",   # match_vib / match_esxi / latest_match_criteria / MESSAGE
        "cmd_prefix": "LD_LIBRARY_PATH",  # LD_LIBRARY_PATH has special behaviour - if not is ran with pretetermined fmtstring
        "LD_LIBRARY_PATH": [  # List of relative paths.
            "foo",
            "bar"
            ],'
        "LD_LIBRARY_LIST": [ # list of ABS paths (same fmt string work as the rest of the paths)

        ]
        "criteria" : {}  # used with 'latest_match_criteria' behaviour - this is a dict of the criteria to match.
        "message" : ''  # String - message which is displayed in the terminal.
        "cmd_path": "path",  # fmtstring
        "vib_name": "vsan",  # Name of vib to match if match_vib is set
        "branch" : "vsphere2016",  # Needed for behaviour 'latest' to know which branch
        "release_type" : "debug",  # Needed for behaviour 'latest' to know which release type to target (release/ debug)
        "exceptions": {
            6: [{
                "min_build": 1234,
                "max_build": None,  # min_build / max_build required - set to None for open ended.
                ## Override any key here from parent.
            }],
            5: [{
                "min_build": 1,
                "max_build": 5,
                "LD_LIBRARY_PATH": [ "bar", "baz"]
            },
            {
                "min_build": 6,
                "max_build": 10,
                "cmd_prefix": "echo 'I am a teapot short and stout'"
            }
            ]
        }
    }
    """

    def __init__(self, cfg, args, build=None, bundle=None, use_cache=True, debug=False):
        """
        :param cfg: dict which defines how we run a given cmd
        :param args: Command arguments (string)
        :param build: build number (numeric) (optional)
        :param bundle: nephelai ESXBundle instance (optional)
        :param use_cache: bool
        :return:
        """
        self.debug = debug  # Needs to be first
        if use_cache:
            try:
                self.tmpfs = get_path_to_user_tmpfs()
                self.debug_print('Temp set to: {0}'.format(self.tmpfs))
            except FileNotFoundError:
                self.debug_print('Cannot find user specific tmpfs.')
                self.tmpfs = None
        else:
            self.tmpfs = None

        self.cfg = cfg
        self.bundle = bundle
        self.build = build
        self.cli = ''
        self.args = args

    def debug_print(self, message):
        """
        Prints message to screen if debug mode is enabled.
        No-op if no debug mode.
        :param message:
        :return:
        """
        if self.debug:
            print(message)

    def build_resultant_cfg(self, major_version, build):
        """
        Take self.cfg and build resultant cfg
        Here we apply exceptions to the normal cfg due to product versions which differ
        from the norm.
        :param major_version: str - Major Version. (Returned from buildweb)
        :param build: int - buildnumber
        :return:
        """
        cfg_cp = self.cfg.copy()
        self.debug_print('Initial cfg is {0}'.format(cfg_cp))
        children = cfg_cp.pop('exceptions')
        exception_list = children.get(str(major_version), [])
        try:
            for exc in exception_list:
                if exc.get('min_build', 0) <= build < exc.get('max_build', math.inf):
                    cfg_cp.update(exc)  # Overlay exception dict over cfg.
        except Exception as e:
            raise e
        self.resultant_cfg = cfg_cp
        self.debug_print('Resultant cfg is: {0}'.format(self.resultant_cfg))

    def build_ld_lib_cmd_prefix(self):
        """
        Build CMD prefix to set LD_LIBRARY_PATH
        :return:
        """
        path_list = self.resultant_cfg.get('LD_LIBRARY_PATH')
        paths = [self.fill_out_abspath(path) for path in path_list]
        self.debug_print('List of paths to use for LD_LIBRARY_PATH {0}'.format(paths))
        return 'LD_LIBRARY_PATH=' + ':'.join(paths)

    def fill_out_abspath(self, path):
        """
        Take path - build dict based on self.resultant_cfg - and fill out
        This is where the fmtstrings are applied to all abspaths in the config
        so:
        {buildtree} becomes /build/storage61/release/bora-2700073/ etc...
        The list of supported format strings is essentially the response from get_build_info
        plus 'self_path' (which references the path to this application)
        :param path:
        :return:
        """
        if self.build_info.get('buildtree') is None:
            raise BuildInfoFailure('Build has been backed up - no available data.')
        fmt_dict = {
            'self_path': os.path.split(os.path.realpath(__file__))[0],
        }
        fmt_dict.update(self.build_info)
        return path.format(**fmt_dict)

    def build_command(self):
        """
        Primary logic which fills out self.cli with the command line we can run later.
        - This is the primary entry point.
        :return:
        """
        # Several cases here - self.build is None (in a bundle) - self.build is numeric (supplied at cli)
        # Build is None with no bundle - but its ok (voma) - error path
        self.debug_print('Build: {0}, Bundle: {1}'.format(self.build, self.bundle))
        if self.build is None and self.bundle is not None and self.cfg.get('behaviour') != 'latest_on_branch':
            # In the bundle case we need to check the esxi version first.
            esxi_buildnum = self.bundle.version.get('buildnumber')
            esxi_major = get_build_info(esxi_buildnum).get('version')
            # esxi_major = self.bundle.version.get('major')  # removing for less product specifics.
            self.build_resultant_cfg(esxi_major, esxi_buildnum)  # Load any exceptions and build out self.resultant_cfg
            # Ok, now we have our real set of instructions lets update the build number.
            self.update_build_from_behaviour()
        elif self.build:
            # Build supplied at command line so do nothing
            version = get_build_info(self.build).get('version')
            self.build_resultant_cfg(version, self.build)
        elif self.build is None and self.cfg.get('behaviour') == 'latest_match_criteria':
            self.resultant_cfg = self.cfg.copy()
            self.update_build_from_behaviour()
        else:
            raise ValueError('Non numeric build number? {0}'.format(self.build))

        if self.resultant_cfg.get('behaviour') == 'MESSAGE':
            print(self.resultant_cfg.get('message'))
            sys.exit(0)
        # Here we have exploded - or we have the build number.
        self.build_info = get_build_info(self.build)

        # Run it!

        if self.resultant_cfg.get('cmd_prefix') == 'LD_LIBRARY_PATH':
            prefix = self.build_ld_lib_cmd_prefix()
        elif self.resultant_cfg.get('cmd_prefix') == 'LD_LIBRARY_LIST':
            # Build tmpdir -
            target_dir = os.path.join(
                get_path_to_user_tmpfs(),
                'amr',   # Prefix
                self.resultant_cfg.get('application_name'),  # App name (Apps have own subdir)
                str(self.build)  # Build number
            )
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)  # If not in user specific tmpfs should look at changing permissions here.

            # Copy list of files into tmpdir
            for item in self.resultant_cfg.get('LD_LIBRARY_LIST', []):
                actual_path = self.fill_out_abspath(item)
                if not os.path.exists(os.path.join(target_dir, os.path.basename(actual_path))):  # Check cache first.
                    self.debug_print('linking {0} to {1}'.format(
                        actual_path,
                        os.path.join(target_dir, os.path.basename(actual_path))
                    ))
                    try:
                        os.symlink(actual_path, os.path.join(target_dir, os.path.basename(actual_path)))
                    except FileExistsError:
                        pass  # Skip

            # SET LD_LIB_PATH to tmpdir
            prefix = 'LD_LIBRARY_PATH={0}'.format(target_dir)
        else:
            prefix = self.fill_out_abspath(self.resultant_cfg.get('cmd_prefix', ''))

        cmd_path = self.fill_out_abspath(self.resultant_cfg.get('cmd_path'))

        self.cli = (prefix + ' ' + cmd_path + ' ' + self.args).lstrip()

    def execute_command(self):
        """
        Execute the command.
        This runs the thing.
        If you are using Runner() in a separate project then you will likely want to
        run the application yourself so you can capture the output.
        :return:
        """
        self.debug_print('Running : "{0}"'.format(self.cli))
        exit_status = subprocess.call(self.cli, shell=True)
        self.debug_print('Program exited with {0}'.format(exit_status))
        return exit_status

    def update_build_from_behaviour(self):
        """
        Take the resultant_cfg - and current build num / bundle and behaviour
        Update the build num as needed.
        :return:
        :raises BuildGuessFailure:
        """
        if self.resultant_cfg.get('behaviour', 'match_esxi') == 'match_esxi':
            if self.bundle is None:
                raise BuildGuessFailure('I do not have an ESX Bundle to guess the correct build with.')
            self.build = self.bundle.version.get('buildnumber')
        elif self.resultant_cfg.get('behaviour', 'match_esxi') == 'match_vib':
            if self.bundle is None:
                raise BuildGuessFailure('I do not have an ESX Bundle to guess the correct build with.')
            # Is VIB installed?
            try:
                matches = [z for z in self.bundle.localcli.get('localcli_software-vib-list', [{}])
                           if z.get('Name') == self.resultant_cfg.get('vib_name')]
                match = matches[0]
                """
                Data should look like this:
                [{'Acceptance Level': 'VMwareCertified',
                'Creation Date': '2015-12-08',
                'ID': 'VMware_bootbank_vsan_6.0.0-2.34.3309627',
                'Install Date': '2015-12-08',
                'Name': 'vsan',
                'Status': '',
                'Vendor': 'VMware',
                'Version': '6.0.0-2.34.3309627'}]
                """
                buildnum = match.get('Version').split('.')[-1]  # This won't work on non VMW VIBs.
                self.build = buildnum
            except IndexError as e:
                raise e
        elif self.resultant_cfg.get('behaviour') == 'latest_match_criteria':
            criteria = self.resultant_cfg.get('criteria')
            if criteria is None:
                raise ConfigError('No criteria specified - exiting')
            criteria.update({'_order_by': '-id', '_limit':5})  # Make sure first item in list is 'newest'
            build_list = get_builds(**criteria)
            self.debug_print('Response to query: {0}'.format(build_list['_list'][0]))
            selected_build = build_list.get('_list', [])[0]
            self.debug_print('Selected {0}'.format(selected_build.get('id')))
            self.build = selected_build.get('id')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='automagicallyrun is built to assist VMware GSS staff in running '
                                                 'utilities from VMware engineering mount points.')
    parser.add_argument('-b', '--buildnum', action='store', nargs=1, default=[None], metavar='BUILDNUM', type=int,
                        help='To override the automatic build number detection - specify.')
    parser.add_argument('-D', '--debug', action='store_true', default=False,
                        help='Enable debug Mode.')
    parser.add_argument('-e', '--export', action='store_true', default=False,
                        help='Do not run the command - output to STDOUT the command which would be ran instead.')
    parser.add_argument('-L', '--list', action='store_true', default=False,
                        help='List supported commands and exit..')
    parser.add_argument('-O', '--cfgoverride', action='store', default=False,
                        help='provide alternative cfg file to override global cfg.')

    # Load cfg
    cfg_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), CFG_FILENAME)
    with open(cfg_file) as f:
        master_cfg = json.load(f)

    # Sort out splitting the sys.argv into stuff to pass into argparse and the command which we want to run.
    try:
        command_pos, command = [(e, v) for e, v in enumerate(sys.argv[1:])
                                if v in [x.get('application_name') for x in master_cfg]].pop(0)
    except IndexError:
        command = None  # Exits later with a nice message and usage unless -L is passed.
        command_pos = len(sys.argv)  # This means the full arg list is parsed later.

    args = parser.parse_args(sys.argv[1:command_pos + 1])  # Parse args not related to our command.
    if args.cfgoverride:
        try:
            if os.path.exists(args.cfgoverride):
                # Load from disk
                with open(args.cfgoverride) as f:
                    override_cfg = json.load(f)

                for override_name, cfg_entry in [(x.get('application_name'), x) for x in override_cfg]:
                    existing = [x for x in master_cfg if x.get('application_name') == override_name]
                    if len(existing) == 0:  # Net-new item.
                        master_cfg.append(cfg_entry)
                    else:
                        for num, item in enumerate([x.get('application_name') for x in master_cfg]):
                            if item == override_name:
                                master_cfg[num] = cfg_entry
                print('Using {0} in addition to the global cfg.'.format(args.cfgoverride))
        except Exception as e:
            print('Problem loading {0}: {1}'.format(args.cfgoverride, e))
    cmd_args = ' '.join(sys.argv[command_pos + 2:])  # Convert command related args to a string.
    if args.debug:  # Debug mode? Can't use debug_print here yet as Runner doesn't exist.
        print('Args: {0}'.format(args))
        print('Command: {0}, command_pos: {1}, command_args: {2}'.format(command,
                                                                         command_pos,
                                                                         cmd_args))

    if args.list:  # List out supported applications. Then exit.
        print('Applications defined in config file: {0}'.format(cfg_file))
        for app_name in [x.get('application_name') for x in master_cfg]:
            print('{0}'.format(app_name))
        sys.exit(0)

    if command is None:  # no work to do - bail.
        print('No command specified? See "-L" for a list of supported commands.')
        sys.exit(127)

    # ==============================
    # Spin up Runner and go to work.
    # ==============================

    # Pull out the application config.
    cmd_cfg = [cfg for cfg in master_cfg if cfg.get('application_name') == command]
    if len(cmd_cfg) == 1:
        possible_bundle = None  # Init
        if args.buildnum[0] is None:  # No manual build num - perform autodetection.
            possible_bundle = is_path_esx_bundle(os.path.abspath(os.path.curdir))
            if not possible_bundle:  # Exit - no build num - no autodetect?
                if cmd_cfg[0].get('behaviour') != 'latest_match_criteria':
                    print('No build number specified, and no ESX bundle detected -- Exiting.')
                    sys.exit(1)
        problem = False
        exit_status = 127  # Command not found deafult.
        runtime = None
        try:
            runtime = Runner(cmd_cfg[0], cmd_args, build=args.buildnum[0], debug=args.debug, bundle=possible_bundle)
            runtime.build_command()
            if not args.export:
                exit_status = runtime.execute_command()
            else:
                print(runtime.cli.rstrip())  # Added .rstrip() to cleanup output for -e
                exit_status = 0
        except KeyboardInterrupt:  # ctrl-c
            exit_status = 130
        except BrokenPipeError:  # Head / Tail
            exit_status = 130
        except Exception as e:
            print_exc()
            problem = True
            raise e
        finally:
            usage(
                {
                    'command': command,
                    'args': cmd_args,
                    'build': runtime.build if runtime is not None else args.buildnum[0],
                    'bundle': possible_bundle.__repr__(),
                    'cmd_exit_status': exit_status
                }, problem
            )
            sys.exit(exit_status)  # Echo this status out for use in upper layer bash automation
    else:
        print('Cannot find {0} see "-L" for a list of supported applications.'.format(command))
        sys.exit(126)
