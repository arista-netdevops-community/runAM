# runAM (run-a-module) EVPN

<!-- TOC -->

- [runAM (run-a-module) EVPN](#runam-run-a-module-evpn)
  - [Change Log](#change-log)
  - [Disclaimer](#disclaimer)
  - [Overview](#overview)
  - [Installation](#installation)
  - [Data Store](#data-store)
  - [CLI](#cli)
  - [Important Dependancies](#important-dependancies)
  - [Workflow](#workflow)
    - [Profiles](#profiles)
    - [Port (Server) Provisioning](#port-server-provisioning)

<!-- /TOC -->

## Change Log

- 0.1.1 (Current Release)
  - First version with a small subset of runAM features required for port provisioning

## Disclaimer

While runAM-evpn provides a full set of modules required to build EVPN network, it is not covering any possible design.
Data model used is highly subjective and not necessarily optimal for every use case.
Use it only as a reference and build your own set of modules if required.
There is no official support for this module as well, but issues created will be reviewed and fixed or closed.

If you are interested in automating Arista EVPN network, please take a look at [Arista-AVD](https://github.com/aristanetworks/ansible-avd) Ansible collection as well.
Ansible-AVD has superior community support and is definitely recommended as the first stop.
runAM-evpn is not a replacement for Ansible-AVD, but provides alternative approach to archive the same target using native Python.

## Overview

runAM stands for "run A Module".
runam-evpn package contains number of Python modules required to provision Arista EVPN network.
Every module is focused on a specific task. Modules can be changes, unplugged or re-arranged as required, but some modules depend on the data produced by other modules. Please check [Workflow](#workflow) section before making any changes.

runAM can be used in 3 different ways:

- Imported from any Python script with `import runAM`
- Execute runAM module with `python3 -m runAM <cli-arguments>`
- Use build in runAM CLI. Execute `runAM --help` for details.

runAM motto is KISS. Always focus on simplicity, readability and ease of maintanance. Features and code optimisation are secondary if not improving simplicity.

## Installation

1. Create `database` directory.
2. Install runAM: `pip install runAM-evpn`
3. Enable CLI autocompletition: `eval "$(register-python-argcomplete runAM)"`

For details about CLI autocompletetion please refer to [argcomplete documentation](https://kislyuk.github.io/argcomplete/).

## Data Store

Different runAM modules can exchange the data using common data store.
An instance of JSONStore class is initialized when a module starts and provides number of methods for simplified access to a json file holding the data (`db.json` by default).
Reling on a simple JSON file allows to reduce complexity, eliminate unnecessary dependancies and use Git version control.
The data store class can be extended to support any database that is capable to store JSON data.

Following classes can be used to interact with the data store:

- `JSONStore` - basic methods to interact with the data store
- `PortConfigGenerator(JSONStore)` - additional methods required to build low level port configuration
- `ProfileTicketStore(JSONStore)` - additional methods to work with profile tickets in the data store
- `ServerTicketStore(PortConfigGenerator)` - additional methods to work with server tickets in the data store

## CLI

runAM provides basic CLI to control typical network provisioning operations.  
Using CLI is not mandatory. Every module can be called from any 3rd party tool or script. However runAM CLI helps to eliminate dependancies and is the fastest way to start using runAM modules.
runAM CLI is available once the module is installed. Use `runAM --help` to get details.  
To enable autocompletition, use `eval "$(register-python-argcomplete runAM)"`.  
For details about CLI autocompletetion please refer to [argcomplete documentation](https://kislyuk.github.io/argcomplete/).

CLI can be easily adjusted by changing runAM.cli_spec. This dictionary has following data structure:

```python
{
    <cli-command>: {
        'python_module': <python module to be triggered by this command>,
        'help': <cli command description>,
        'add_argument': [  # add arguments required for Python module to operate as a list
            {
                'arg_name': <full name of CLI argument>,
                'arg_short_name': <short name of CLI argument>,
                'help': <CLI argument help>,
            }
        ]
    }
}
```

On top of runAM CLI, you can use [`jq` tool](https://stedolan.github.io/jq/) to query any data in the database json file.

## Important Dependancies

When possible runAM avoids dependancies to external packages to keep code clean and improve performance.
Neverhterless, some external packages are required for runAM to work:

1. `argcomplete` - CLI auto completition for Python scripts. [https://pypi.org/project/argcomplete/](https://pypi.org/project/argcomplete/)
2. `PyYAML` - read/write YAML data. [https://pypi.org/project/PyYAML/](https://pypi.org/project/PyYAML/)
3. `glom` - for easy access to nested data structures. It helps to keep code compact and readable. [https://pypi.org/project/glom/](https://pypi.org/project/glom/)
4. `jq` - jq for Python. Used to make recursive queries with a reasonable performance. [https://pypi.org/project/jq/](https://pypi.org/project/jq/)

## Workflow

The workflow examples are based on runAM CLI and explain the logic in simplified way. For details please refer to the code.

### Profiles

Profiles contain common data that is re-used frequently. Every profile is identified by a **unique** tag set and if referenced somewhere else, data will be merged.
To merge specific profile into any data structure, use:

```yaml
  any_dictionary_key:
    profiles:
    - ['tag1', 'tag2', 'tag3']  # merge some profile into this dict key
    - ['tag1', 'tag4']  # merge another profile
    - ...
```

Profile tickets can be defined as single- or multi-doc YAMLs. Example:

```yaml
---
tags: ['fallback', 'port_channel']  # tags must be unique
# any data to be merged can be defined below
fallback:
  mode: individual
  timeout: 50
```

Merge means that existing data will be retained.

Commands:

- `runAM profile.add --input_file <profile-ticket-name>.yml`  
  This command adds profile ticket to profile_tickets table in the data store.
  Actions:
  - Find out if ticket is a dictionary (single-doc) or a list (multi-doc YAML).
  - Verify if tags are unique for every ticket. Raise an error and exit if not.
  - Add every ticket into profile_tickets table.
  - Write the change into the data store on disk.
- `runAM profile.query --tags tag1,tag2,...`
  Find all profiles matching specified tag list.
- `runAM profile.delete --tags tag1,tag2,...`
  Delete all profile tickets matching specified tag list. Save that to the disk.

**IMPORTANT**: profiles must be defined before defining any data structures reling on these profiles.

### Port (Server) Provisioning

Port provisioning builds low level data required to parse configuration templates for switch ports towards end hosts (server, compute, external route/switch, etc.).  
The keyword `server` used for corresponding CLI command may be a bit confusing, as the workflow is not limited to servers only. But any other keyword can be equally confusing. Change `runAM.cli_spec` if required.

Port provisioning ticket examples are provided in `tests > data > server_tickets`

Commands:

- `runAM server.add --input_file <server-ticket-name>.yml`
  Add a server ticket into the database and build low level data required to parse configuration templates.
  Actions:
  - Find out if ticket is a dictionary (single-doc) or a list (multi-doc YAML).
  - Verify if server_id is already present in the database. server_id must be unique. If already present raise an error and exit.
  - Verify if switch_name/switch_port combinations defined in the ticket are already in use. If in use, raise an error and exit.
  - Add tickets into the database.
  - Build low level data required to parse configuration templates.
  - Write the change into the data store on disk.
- `runAM server.query --server_id <server ID>`
  Find a server ticket matching specified server ID.
- `runAM server.delete --server_id <server ID>`
  Delete a server ticket matching specified server ID.
  Actions:
  - Find a server ticket matching the specified server ID.
  - Delete the ticket.
  - Re-build low level data required to parse configuration templates.
  - Write the change into the data store on disk.
