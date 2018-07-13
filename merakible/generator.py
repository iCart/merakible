from meraki import meraki
import types
import black
import inspect

import os
import shutil



def generate_methods():
    meraki_file = meraki.__file__
    yield from (
        m for m in vars(meraki)
        if not m.startswith('_')                                    # only the public ones
        and isinstance(getattr(meraki, m), types.FunctionType)      # only the functions
        and getattr(meraki, m).__code__.co_filename == meraki_file  # only the ones defined, not imported
    )


MODULE_TEMPLATE = '''
ANSIBLE_METADATA = {{'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'core'}}

DOCUMENTATION = """
yoohoooo
"""

RETURN = """
yaahaaaa
"""

from ansible.module_utils.basic import AnsibleModule
from meraki import meraki


def main():
    args = {arguments}
    
    module = AnsibleModule(
        bypass_checks=False,
        argument_spec=args,
        supports_check_mode=True,
    )
    
    output = meraki.{method}(**module.params)
    
    
    module.exit_json(changed=False, output=output)


if __name__ == '__main__':
    main()

'''


def clean_dir(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            raise IOError(f'{path} is a file!')
        shutil.rmtree(path)
    os.mkdir(path)


def main(modules_dir):
    """super doc"""
    clean_dir(modules_dir)

    for method in generate_methods():
        method_impl = getattr(meraki, method)
        signature = inspect.signature(method_impl)
        args = {}
        for param in signature.parameters.values():
            required = param.default is inspect._empty
            args[param.name] = {
                'type': 'str', 
                'required': required,
                'default': param.default if not required else None
            }

        method_text = MODULE_TEMPLATE.format(arguments=args, method=method)
        method_text = black.format_str(src_contents=method_text, line_length=black.DEFAULT_LINE_LENGTH)
        with open(os.path.join(modules_dir, f'meraki_{method}.py'), 'w') as module_file:
            module_file.write(method_text)
            print(f"Wrote {len(method_text)} charaters to {module_file.name}.")


if __name__ == '__main__':
    ansible_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ansible'))  # $PWD/../ansible
    print(ansible_dir)
    path = os.path.join(ansible_dir, 'lib', 'ansible', 'modules', 'network', 'meraki_dynamic')
    main(path)
