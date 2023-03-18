#!/usr/bin/env python3

import sys
import os
import glob
from pathlib import Path
import subprocess

NGINX_AVAILABLE = "/etc/nginx/sites-available"
NGINX_ENABLED = "/etc/nginx/sites-enabled"

class Colors:
    GREEN = "\033[32m" if sys.stdout.isatty() else ""
    RED = "\033[31m" if sys.stdout.isatty() else ""
    RESET = "\033[0m" if sys.stdout.isatty() else ""

def usage():
    print("Usage: nginx_manage_site.py [enable|disable|list] site_pattern")
    sys.exit(1)

def list_sites():
    print("Available sites:")
    for site in Path(NGINX_AVAILABLE).iterdir():
        site_name = site.name
        if Path(os.path.join(NGINX_ENABLED, site_name)).exists():
            color = Colors.GREEN
            status = "enabled"
        else:
            color = Colors.RED
            status = "disabled"
        print(f"{color}{site_name} ({status}){Colors.RESET}")

def get_matching_sites(site_pattern):
    matching_sites = glob.glob(f"{NGINX_AVAILABLE}/{site_pattern}*")

    if len(matching_sites) == 0:
        print("No matching sites found.")
        sys.exit(1)
    elif len(matching_sites) > 1 and "*" not in site_pattern:
        print("Multiple matching sites found:")
        for site in matching_sites:
            print(f"  {Path(site).name}")
        print("Please use a more specific pattern or provide a glob pattern.")
        sys.exit(1)

    return matching_sites

def enable_site(site_name):
    if not Path(os.path.join(NGINX_ENABLED, site_name)).exists():
        os.symlink(f"{NGINX_AVAILABLE}/{site_name}", f"{NGINX_ENABLED}/{site_name}")
        print(f"Site {site_name} enabled.")
    else:
        print(f"Site {site_name} is already enabled.")

def disable_site(site_name):
    if Path(os.path.join(NGINX_ENABLED, site_name)).exists():
        Path(os.path.join(NGINX_ENABLED, site_name)).unlink()
        print(f"Site {site_name} disabled.")
    else:
        print(f"Site {site_name} not found in {NGINX_ENABLED}.")

class ArgParser:
    def __init__(self, argv):
        self.argv = argv

    def parse(self):
        if len(self.argv) < 2:
            usage()

        action = self.argv[1]

        if action not in ["enable", "disable", "list"]:
            usage()

        if action in ["enable", "disable"]:
            if len(self.argv) < 3:
                print(f"Error: The '{action}' action requires a site pattern.")
                usage()
            site_pattern = self.argv[2]
        else:
            site_pattern = ""

        return {"action": action, "site_pattern": site_pattern}

def nginx_manage_site(action):
    try:
        action = args["action"]

        if action == "list":
            list_sites()
            return

        site_pattern = args["site_pattern"]
        matching_sites = get_matching_sites(site_pattern)

        for site in matching_sites:
            site_name = Path(site).name
            if action == "enable":
                enable_site(site_name)
            elif action == "disable":
                disable_site(site_name)
            else:
                print(f"Invalid action: {action}. Use 'enable', 'disable', or 'list'.")
                sys.exit(1)

        # Reload Nginx configuration
        subprocess.run(["sudo", "systemctl", "reload", "nginx"])

    except PermissionError as e:
        print(f"Error: {e}. Please run the script with the necessary privileges.")

if __name__ == "__main__":
    arg_parser = ArgParser(sys.argv)
    args = arg_parser.parse()
    nginx_manage_site(args)
