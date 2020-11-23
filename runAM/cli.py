import argparse
import argcomplete
import runAM
import os
import sys
import inspect
import select
import json
from pprint import pprint

def add_arguments(a_parser, argument_list):
    """Add arguments to a parser

    Args:
        a_parser (argparse parser object): a parser to modify
        argument_list (list): list of agument specification dictionaries
    """

    for an_argument in argument_list:

        args = [
            an_argument['arg_name'],
            an_argument['arg_short_name'],
        ]

        kwargs = {'help': an_argument['help']}
        if 'action' in an_argument.keys():
            kwargs.update({'action': an_argument['action']})
        if 'default' in an_argument.keys():
            kwargs.update({'default': an_argument['default']})
        if 'choices' in an_argument.keys():
            kwargs.update({'choices': an_argument['choices']})
        if 'type' in an_argument.keys():
            kwargs.update({'type': eval(an_argument['type'])})  # eval to convert string to type
        if 'required' in an_argument.keys():
            kwargs.update({'required': an_argument['required']})

        a_parser.add_argument(*args, **kwargs)

def parse():
    # Build CLI for runAMcli from cli_spec.py
    # runAMcli is using argcomplete. To enable autocompletition, follow the docs here:
    # https://kislyuk.github.io/argcomplete/
    # TL;DR switch to bash and run: eval "$(register-python-argcomplete runAMcli)"
    parser = argparse.ArgumentParser(
        description=runAM.cli_spec['__main_parser']['help'], formatter_class=argparse.RawTextHelpFormatter)
    if 'add_argument' in runAM.cli_spec['__main_parser'].keys():
        add_arguments(parser, runAM.cli_spec['__main_parser']['add_argument'])
    subparsers = parser.add_subparsers(help="Select package", dest='subparser_name')

    for p_name, p_spec in sorted(runAM.cli_spec.items()):
        if p_name != '__main_parser':
            subparser = subparsers.add_parser(
                p_name, help=p_spec['help'],
                description=p_spec['help'],
                formatter_class=argparse.RawTextHelpFormatter
            )
            if 'add_argument' in p_spec.keys():
                add_arguments(subparser, p_spec['add_argument'])

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    return vars(args)  # return args dictionary

def get_input(input_file=''):
    """Get input data from a file or stdin

    Args:
        input_file (str, optional): Filename to load input data. Must be json or YAML. Defaults to ''.

    Returns:
        [type]: [description]
    """

    # TODO: add CSV support

    # get stream from a file or stdin
    if input_file:
        in_stream = open(input_file, mode='r')
    else:
        if select.select([sys.stdin, ], [], [], 0.0)[0]:
            in_stream = sys.stdin

    # if input stream is present try to load data and add to all_params_dict
    try:
        in_string = "".join(in_stream)
    except Exception as _:
        pass  # ignore exception if in_stream not present or can not be loaded
    else:
        in_data = False

        try:  # try to load as JSON
            in_data = json.loads(in_string)
        except Exception as _:
            pass  # ignore if data is not a valid JSON

        if not in_data:
            try:  # try to load as YAML
                in_data = runAM.read.yaml_string(in_string, load_all=True)  # TODO: review if load_all is required?
            except Exception as _:
                pass  # ignore if data is not a valid YAML
        
        return in_data

def run_module(module_name_string, args_dict):
    """Run a module specified via CLI.

    Args:
        module_name_string (str): Module name to execute.
        args_dict (dict): CLI arguments dictionary.

    Returns:
        [any type returned by module]: Data returned by module. If any.
    """

    args = list()
    kwargs = dict()

    module_signature = inspect.signature(eval(module_name_string))
    for module_param_name in module_signature.parameters.keys():
        if module_signature.parameters[module_param_name].default is inspect._empty:
            # if default value is not defined, the parameter is positional and mandatory
            if module_param_name in args_dict.keys():
                args.append(args_dict[module_param_name])
            else:
                sys.exit('ERROR: Mandatory positional parameter {} is missing.'.format(module_param_name))
        else:
            if module_param_name in args_dict.keys():
                kwargs.update({
                    module_param_name: args_dict[module_param_name]
                })

    if module_name_string.startswith('runAM'):  # simple way to keep eval() safe
        return eval(module_name_string)(*args, **kwargs)

def interpreter():
    # process user input and execute a module
    args = runAM.cli.parse()

    # TODO: make module specific
    if 'input_file' in args.keys():
        if args['input_file']:
            in_data = runAM.cli.get_input(args['input_file'])
        else:
            in_data = runAM.cli.get_input()
    else:
        in_data = runAM.cli.get_input()

    args.update({
        'in_data': in_data
    })

    python_module_name = runAM.cli_spec[args['subparser_name']]['python_module']

    out_data = runAM.cli.run_module(python_module_name, args)
    if 'echo' in args.keys():
        if args['echo']:
            print(out_data)  # TODO: consider logging
