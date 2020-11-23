import pytest
import os
import sys
import runAM.read

# insert project directory to $PATH for imports to work
test_file = os.path.realpath(__file__)
test_dir = os.path.dirname(test_file)
project_dir = os.path.dirname(test_dir)
sys.path.append(project_dir)

def test_00_can_assert_true():
    # before any test verify if PyTest is working and can assert True
    assert True

def test_01_load_single_doc_yaml():
    yaml_filename = os.path.join(test_dir, "data/simple-single-doc-yaml.yml")
    loaded_data = runAM.read.yaml_file(yaml_filename)
    expected_data = {
        "name": "Martin D'vloper",
        "job": "Developer",
        "skill": "Elite",
        "employed": True,
        "foods": [
            "Apple",
            "Orange",
            "Strawberry",
            "Mango"
        ],
        "languages": {
            "perl": "Elite",
            "python": "Elite",
            "pascal": "Lame"
        },
        "education": "4 GCSEs\n3 A-Levels\nBSc in the Internet of Things\n"
    }
    assert loaded_data == expected_data

def test_02_load_multi_doc_yaml():
    yaml_filename = os.path.join(test_dir, "data/simple-multi-doc-yaml.yml")
    loaded_data = runAM.read.yaml_file(yaml_filename, load_all=True)
    expected_data = [
        {
            "name": "Martin D'vloper",
            "job": "Developer",
            "skill": "Elite",
            "employed": True,
            "foods": [
                "Apple",
                "Orange",
                "Strawberry",
                "Mango"
            ],
            "languages": {
                "perl": "Elite",
                "python": "Elite",
                "pascal": "Lame"
            },
            "education": "4 GCSEs\n3 A-Levels\nBSc in the Internet of Things\n"
        },
        [
            {
                "item": "Super Hoop",
                "quantity": 1
            },
            {
                "item": "Basketball",
                "quantity": 4
            },
            {
                "item": "Big Shoes",
                "quantity": 1
            }
        ]
    ]
    assert loaded_data == expected_data

def test_03_load_non_existing_yaml():
    try:
        runAM.read.yaml_file('non-existing.yaml')
    except Exception as _:
        assert True  # Loading non-existing file is expected to fail
    else:
        assert False

def test_04_load_invalid_yaml():
    try:
        yaml_filename = os.path.join(test_dir, "data/invalid-yaml.yml")
        runAM.read.yaml_file(yaml_filename)
    except Exception as _:
        assert True  # Loading invalid YAML file is expected to fail
    else:
        assert False

def test_05_read_yaml_string():
    yamL_string = (
        "---\n"
        "# An employee record\n"
        "name: Martin D'vloper\n"
        "job: Developer\n"
        "skill: Elite\n"
        "employed: True\n"
        "foods:\n"
        "    - Apple\n"
        "    - Orange\n"
        "    - Strawberry\n"
        "    - Mango\n"
        "languages:\n"
        "    perl: Elite\n"
        "    python: Elite\n"
        "    pascal: Lame\n"
        "education: |\n"
        "    4 GCSEs\n"
        "    3 A-Levels\n"
        "    BSc in the Internet of Things\n"
    )

    expected_data = expected_data = {
        "name": "Martin D'vloper",
        "job": "Developer",
        "skill": "Elite",
        "employed": True,
        "foods": [
            "Apple",
            "Orange",
            "Strawberry",
            "Mango"
        ],
        "languages": {
            "perl": "Elite",
            "python": "Elite",
            "pascal": "Lame"
        },
        "education": "4 GCSEs\n3 A-Levels\nBSc in the Internet of Things\n"
    }

    assert runAM.read.yaml_string(yamL_string) == expected_data
