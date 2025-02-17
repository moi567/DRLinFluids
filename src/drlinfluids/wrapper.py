import json
import re


def actions2dict(entry_dict, reinforcement_learning_var, agent_actions):
    """Write parameters to velocity or pressure files in OpenFOAM.

    Parameters
    ----------
    entry_dict : list
        list for change item.
    reinforcement_learning_var : tuple
        reinforcement learning variables
    agent_actions : tuple
        The action value generated by the agent.

    Returns
    -------
    actions_dict
        Specify reinforcement learning variables.

    Examples
    --------
    from DRLinFluids.utils import actions2dict
    reinforcement_learning_var_example = (x, y, z)
    agent_actions_example = (1, 2, 3)

    note
    --------
    In particular, entry_dict should not contain regular expression related,
    minmax_value: Specify independent variables and expressions related to boundary conditions.
    Note that only the most basic calculation expressions are accepted, and operation functions
    in math or numpy cannot be used temporarily.
    entry_example = {
        'U': {
            'JET1': '({x} 0 0)',
            'JET2': '(0 {y} 0)',
            'JET3': '(0 0 {z})',
            'JET4': '{x+y+z}',
            'JET(4|5)': '{x+y+z}'  # X cannot contain regular expressions and must be separated manually
        },
        'k': {
            'JET1': '({0.5*x} 0 0)',
            'JET2': '(0 {0.5*y*y} 0)',
            'JET3': '(0 0 {2*z**0.5})',
            'JET4': '{x+2*y+3*z}'
        }
    }
    """
    mapping_dict = dict(zip(reinforcement_learning_var, agent_actions))

    entry_str_org = json.dumps(entry_dict, indent=4)
    entry_str_temp = re.sub(r"{\n", r"{{\n", entry_str_org)
    entry_str_temp = re.sub(r"}\n", r"}}\n", entry_str_temp)
    entry_str_temp = re.sub(r"}$", r"}}", entry_str_temp)
    entry_str_temp = re.sub(r"},", r"}},", entry_str_temp)
    entry_str_final = eval(f'f"""{entry_str_temp}"""', mapping_dict)
    actions_dict = json.loads(entry_str_final)

    return actions_dict


def dict2foam(flow_var_directory, actions_dict):
    """Write parameters to velocity or pressure files in OpenFOAM.

    Parameters
    ----------
    flow_var_directory : str
        Path to simulation file.
    actions_dict : tuple
        Specify reinforcement learning variables

    Examples
    --------
    from DRLinFluids.utils import dict2foam
    """
    for flow_var, flow_dict in actions_dict.items():
        print("/".join([flow_var_directory, flow_var]))
        with open("/".join([flow_var_directory, flow_var]), "r+") as f:
            content = f.read()
            for entry, value_dict in flow_dict.items():
                for keyword, value in value_dict.items():
                    content = re.sub(
                        f"({entry}(?:\n.*?)*{keyword}\s+).*;", f"\g<1>{value};", content
                    )
                # content = re.sub(f'({entry}(?:\n.*?)*value\s+uniform\s+).*;', f'\g<1>{value};', content)
            f.seek(0)
            f.truncate()
            f.write(content)
