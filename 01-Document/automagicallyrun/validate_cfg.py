#!/usr/bin/env python3

import json
import os
import traceback
import sys
from automagicallyrun import CFG_FILENAME, VALID_BEHAVIOURS

def check_cfg(cfg):
    """
    Raises assertion if problem present.
    :param cfg: 
    :return: 
    """

    assert 'exceptions' in cfg.keys(), " 'exceptions' key missing"
    assert type(cfg.get('exceptions')) is dict, "'exceptions' should be an object / dict."
    assert 'application_name' in cfg.keys(), " 'application_name' key missing"
    assert type(cfg.get('application_name')) is str, "'application_name' should be a string."
    assert 'behaviour' in cfg.keys(), " 'behaviour' key missing"
    assert cfg.get('behaviour') in VALID_BEHAVIOURS, "'behaviour' should be one of {0}".format(VALID_BEHAVIOURS)
    if cfg.get('behaviour') == 'LD_LIBRARY_PATH':
        assert 'LD_LIBRARY_PATH' in cfg.keys(), "If behaviour is LD_LIBRARY_PATH you need to specify one."
    if cfg.get('behaviour') == 'LD_LIBRARY_LIST':
        assert 'LD_LIBRARY_LIST' in cfg.keys(), "If behaviour is LD_LIBRARY_LIST you need to specify one."
    if cfg.get('behaviour') == 'latest_match_criteria':
        assert 'criteria' in cfg.keys(), "If behaviour is latest_match_criteria you need to specify criteria."
    if 'LD_LIBRARY_PATH' in cfg.keys():
        assert type(cfg.get('LD_LIBRARY_PATH')) is list, "'LD_LIBRARY_PATH' should be a list."
    if 'LD_LIBRARY_LIST' in cfg.keys():
        assert type(cfg.get('LD_LIBRARY_LIST')) is list, "'LD_LIBRARY_LIST' should be a list."
    if 'criteria' in cfg.keys():
        assert type(cfg.get('criteria')) is dict, "'criteria' should be an object / dict."
    if 'min_build' in cfg.keys():
        assert type(cfg.get('min_build')) is int, "'min_build' must be an int."
    if 'max_build' in cfg.keys():
        assert type(cfg.get('max_build')) is int, "'max_build' must be an int."
    if cfg.get('behaviour') != 'MESSAGE':
        assert 'cmd_path' in cfg.keys(), " 'cmd_path' key missing."
        assert type(cfg.get('cmd_path')) is str, "'cmd_path' should be a string."
        assert 'cmd_prefix' in cfg.keys(), " 'cmd_prefix' key missing"
        assert type(cfg.get('cmd_prefix')) is str, "'cmd_prefix' should be a string."

if __name__ == '__main__':

    cfg_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), CFG_FILENAME)

    try:
        cfg_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), CFG_FILENAME)
        with open(cfg_file) as f:
            master_cfg = json.load(f)
    except Exception as e:
        print('Problem loading cfg file: "{0}"'.format(cfg_file))
        traceback.print_exc()
        sys.exit()

    problem = 0
    success = 0
    for app in master_cfg:
        try:
            check_cfg(app)
            for major, stuff in app.get('exceptions').items():
                for additional in stuff:
                    copy_app = app.copy()
                    copy_app.update(additional)
                    check_cfg(copy_app)
            success += 1
            print(app.get('application_name'))
        except AssertionError as e:
            print('\033[31mProblem with:\033[0m "\033[41m{0}\033[0m"'.format(app))
            print('\033[43m')
            traceback.print_exc()
            print('\033[0m')
            problem += 1

    names = [x.get('application_name') for x in master_cfg]
    name_set = set(names)

    for x in name_set:
        if names.count(x) > 1:
            print('\033[31mDuplciate for: "{0}" found.\033[0m'.format(x))
            problem += 1

    print('Checked {0} entries. {1} success, {2} problems'.format(problem + success, success, problem))