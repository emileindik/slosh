import subprocess
import os
import sys
import argparse
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_ssh_config(ssh_config_path):
    try:
        with open(ssh_config_path, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        logging.error(f"SSH config file does not exist, creating new file at {ssh_config_path}")
        return []
    except IOError as e:
        logging.error(f"Error opening SSH config file for read: {e}")
        return None

def write_ssh_config(ssh_config_path, new_config_lines):
    try:
        with open(ssh_config_path, 'w') as file:
            file.writelines(new_config_lines)
    except IOError as e:
        logging.error(f"Error opening SSH config file for write: {e}")

def update_ssh_config(host_alias, args_dict):
    """
    Updates or appends a new host configuration in the user's SSH config file. This function searches for an existing
    host configuration matching the given host_alias. If found, it updates the configuration with the provided arguments.
    If not found, it appends a new host configuration at the end of the file.

    Args:
        host_alias (str): The alias of the host to update or append in the SSH config file.
        args_dict (dict): A dictionary containing the SSH configuration options and their values.

    The function first ensures the existence of the SSH config file directory, then reads the current configurations.
    It iterates over each line to find a matching host configuration. If a match is found, it updates the configuration.
    Otherwise, it appends a new configuration at the end. Finally, it writes the updated or new configuration back to the file.
    """
    ssh_config_path = os.path.join(os.path.expanduser('~'), '.ssh', 'config')
    updated_config_lines = []
    host_found = False
    updating_host = False

    os.makedirs(os.path.dirname(ssh_config_path), exist_ok=True)

    lines = read_ssh_config(ssh_config_path)
    if lines is None:
        return

    for line in lines:
        if line.strip().startswith('Host ') and ' ' in line:
            current_host = line.strip().split(' ')[1]
            if current_host == host_alias:
                host_found = True
                updating_host = True
                updated_config_lines.append(f"Host {host_alias}\n")
                for key, value in args_dict.items():
                    updated_config_lines.append(f"    {key} {value}\n")
                # Ensure there's a newline after the updated host config to separate from the next entry
                updated_config_lines.append("\n")
                continue  # Skip the rest of the loop to avoid adding the existing host config lines
            elif updating_host:
                # We've finished updating the host and have encountered the next host, stop updating
                updating_host = False
        if not updating_host:
            updated_config_lines.append(line)

    if not host_found:
        if updated_config_lines and not updated_config_lines[-1].strip() == "":
            updated_config_lines.append("\n")  # Ensure there's a newline before the new host config if it's not the first entry
        updated_config_lines.append(f"Host {host_alias}\n")
        for key, value in args_dict.items():
            updated_config_lines.append(f"    {key} {value}\n")

    write_ssh_config(ssh_config_path, updated_config_lines)

def parse_ssh_host(known_args):
    """
    Parses the SSH host string and updates the known_args object with parsed components.

    This function takes a known_args object, which contains an attribute 'HostName' that may include
    a protocol prefix ('ssh://'), a user name ('user@'), and/or a port number (':port'). It updates
    the 'HostName' attribute by removing the protocol prefix if present. If a user name is included,
    it splits the string and updates both the 'User' and 'HostName' attributes accordingly. Similarly,
    if a port number is included, it splits the string and updates both the 'HostName' and 'Port'
    attributes.

    Args:
        known_args: An object with 'HostName', and optionally 'User' and 'Port' attributes.

    Returns:
        None. The function directly modifies the known_args object.
    """
    if known_args.HostName.startswith('ssh://'):
        known_args.HostName = known_args.HostName[6:]
    if '@' in known_args.HostName:
        known_args.User, known_args.HostName = known_args.HostName.split('@')
    if ':' in known_args.HostName:
        known_args.HostName, known_args.Port = known_args.HostName.split(':')

def remove_save_as_option(full_cli_options, host_alias_option):
    if '=' in host_alias_option:
        full_cli_options.remove(host_alias_option)
    else:
        host_alias_index = full_cli_options.index('--save-as')
        full_cli_options.pop(host_alias_index)
        full_cli_options.pop(host_alias_index)

def transform_known_args_values(known_args):
    # Map LogLevel
    log_level_map = {1: 'VERBOSE', 2: 'DEBUG1', 3: 'DEBUG3'}
    if known_args.LogLevel == 0:
        known_args.LogLevel = None
    elif known_args.LogLevel in log_level_map:
        known_args.LogLevel = log_level_map[known_args.LogLevel]
    else:
        known_args.LogLevel = "DEBUG3"

    # Clean HostName and decompose into User, HostName, Port
    parse_ssh_host(known_args)

def main():
    full_cli_options = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Use "--save-dev <host alias name>" to save the host configuration in the SSH config file. Otherwise, this is a pass-through to "ssh" cli.', add_help=False)
    parser.add_argument('--save-as', dest='host_alias')
    parser.add_argument('HostName', nargs="?")
    parser.add_argument('-l', dest='User')
    parser.add_argument('-p', dest='Port')
    parser.add_argument('-i', dest='IdentityFile')
    parser.add_argument('-A', dest='ForwardAgent', action='store_const', const='yes')
    parser.add_argument('-C', dest='Compression', action='store_const', const='yes')
    parser.add_argument('-v', dest='LogLevel', action='count', default=0)
    known_args, _ = parser.parse_known_intermixed_args()

    host_alias_option = next((opt for opt in full_cli_options if opt.startswith('--save-as')), None)
    if host_alias_option:
        remove_save_as_option(full_cli_options, host_alias_option)

    if known_args.host_alias:
        if not known_args.HostName:
            parser.error('At least one positional arg "destination" must be provided')

        transform_known_args_values(known_args)

        host_alias = known_args.host_alias
        delattr(known_args, 'host_alias')

        non_none_args = {k: v for k, v in vars(known_args).items() if v is not None}
        update_ssh_config(host_alias, non_none_args)

    subprocess.run(['ssh'] + full_cli_options)

if __name__ == '__main__':
    main()
