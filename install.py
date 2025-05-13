import getpass
import base64
import argparse
import sys
from install import Environment
from install.WhitelistManager import WhitelistManager


def get_whitelist_manager():
    w = WhitelistManager()
    w.load_instance('cloud', './cloud/config.json', './cloud/whitelist.yml')
    return w


def install_target_servers(env_name, instance, connection):
    from install.resources.TargetServer import TargetServer
    target_servers = get_whitelist_manager().get_whitelisted_target_servers(instance, env_name)
    print(f"whitelisted target_server {target_servers}")
    for targetServer in target_servers:
        print(f"\n--- Installing {targetServer} in environment: {env_name} ---")
        targetServer = TargetServer(targetServer['name'], targetServer, connection)
        targetServer.apply()


def main():
    parser = argparse.ArgumentParser(description="Script that takes an instance argument.")
    parser.add_argument(
        "--instance",
        required=True,
        choices=["on-prem", "cloud"],
        help="Specify the instance type: 'on-prem' or 'cloud'."
    )
    parser.add_argument('--username', required=True, help='username to finish installaiton')
    parser.add_argument('--host', required=True, help='apigee host finish installaiton')
    parser.add_argument('--org', required=True, help='apigee host finish installaiton')
    args = parser.parse_args()
    if args.instance not in ("on-prem", "cloud"):
        print("Error: --instance must be either 'on-prem' or 'cloud'.", file=sys.stderr)
        sys.exit(1)
    if not (args.username or args.host or args.org):
        print("Error: --username, --org, --host are required'.", file=sys.stderr)
        sys.exit(1)
    password = getpass.getpass(prompt='Password: ')
    if not password:
        print("Error: Password is required.", file=sys.stderr)
        sys.exit(1)

    print(f"Username: {args.username}")
    print(f"Password entered: {'*' * len(password)}")
    print(f"Instance selected: {args.instance}")
    credentials = f'{args.username}:{password}'
    encoded_credentials = f"Basic {base64.b64encode(credentials.encode()).decode('utf-8')}"

    for env in Environment.Environment:
        from install.setup.Connection import Connection
        connection = Connection(args.org, args.host, env.value, encoded_credentials)
        install_target_servers(env.value, args.instance, connection)

    # process pilot environment

    # process live environment

    # process kvms, targetservers, caches

    # process proxies

    # process products

    # process developer apps


if __name__ == "__main__":
    main()
