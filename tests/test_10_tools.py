import pytest
import os
import sys
import runAM
import json

# insert project directory to $PATH for imports to work
test_file = os.path.realpath(__file__)
test_dir = os.path.dirname(test_file)
project_dir = os.path.dirname(test_dir)
sys.path.append(project_dir)

def test_000_can_assert_true():
    # before any test verify if PyTest is working and can assert True
    assert True

def test_010_time_stamp():
    # TODO: regexp to check string format
    return_value = runAM.tools.time_stamp()
    assert isinstance(return_value, str)

def test_020_change_nested_value():
    # Change a value indexed by a key list
    in_dict = {
        '1': {
            'interface': {
                'ethernet': {
                    'tags': ['tag1', 'tag2']
                }
            }
        }
    }
    out_dict = runAM.tools.change_nested_value(path=['1', 'interface', 'ethernet'], in_data=in_dict, new_value={
        'tags': ['tag1', 'tag2'],
        "switchport": {
                "mode": "trunk",
                "native_vlan": 10,
                "vlan": "10, 20-30"
            }
    })
    assert out_dict == {
        '1': {
            'interface': {
                'ethernet': {
                    'tags': ['tag1', 'tag2'],
                    "switchport": {
                        "mode": "trunk",
                        "native_vlan": 10,
                        "vlan": "10, 20-30"
                    }
                }
            }
        }
    }

def test_025_delete_value():
    # Delete a value indexed by a key list
    in_dict = {
        '1': {
            'interface': {
                'ethernet': {
                    'tags': ['tag1', 'tag2'],
                    "switchport": {
                        "mode": "trunk",
                        "native_vlan": 10,
                        "vlan": "10, 20-30"
                    }
                }
            }
        }
    }
    out_dict = runAM.tools.change_nested_value(path=['1', 'interface', 'ethernet', 'tags'], in_data=in_dict, delete=True)
    assert out_dict == {
        '1': {
            'interface': {
                'ethernet': {
                    "switchport": {
                        "mode": "trunk",
                        "native_vlan": 10,
                        "vlan": "10, 20-30"
                    }
                }
            }
        }
    }

def test_030_merge_dict():
    # merge 2 dictionaries
    d1 = {
        'outKey1': {
            'inKey1': 'anyValue'
        }
    }
    d2 = {
        'outKey1': {
            'inKey2': 'anyOtherValue'
        }
    }
    assert runAM.tools.merge_data_objects(d1, d2) == {
        'outKey1': {
            'inKey1': 'anyValue',
            'inKey2': 'anyOtherValue'
        }
    }
