#!/usr/bin/env python3

import sys
import os
import glob
from pathlib import Path
import subprocess
import argparse

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

def create_site(server_name, listen):
    config_template = f"""\
server {{
    listen {listen};
    server_name {server_name};

    location / {{
        root /var/www/{server_name};
        index index.html;
    }}

    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;

    location = /50x.html {{
        root /usr/share/nginx/html;
    }}
}}
"""
    config_path = os.path.join(NGINX_AVAILABLE, server_name)

    if Path(config_path).exists():
        print(f"Error: A configuration file already exists for '{server_name}'.")
        sys.exit(1)

    with open(config_path, "w") as config_file:
        config_file.write(config_template)

    print(f"Created Nginx configuration for {server_name}.")

def nginx_manage_site(args):
    try:
        if args.action == "list":
            list_sites()
        elif args.action == "create":
            create_site(args.server_name, args.listen)
        elif args.action in ["enable", "disable"]:
            site_pattern = args.site_pattern
            matching_sites = get_matching_sites(site_pattern)

            for site in matching_sites:
                site_name = Path(site).name
                if args.action == "enable":
                    enable_site(site_name)
                elif args.action == "disable":
                    disable_site(site_name)
        else:
            print(f"Invalid action: {action}. Use 'enable', 'disable', 'create', or 'list'.")
            sys.exit(1)


        # Reload Nginx configuration
        subprocess.run(["sudo", "systemctl", "reload", "nginx"])

    except PermissionError as e:
        print(f"Error: {e}. Please run the script with the necessary privileges.")

def main():
    parser = argparse.ArgumentParser(description="Nginx site manager")
    subparsers = parser.add_subparsers(dest="action")

    parser_enable = subparsers.add_parser("enable", help="Enable a site")
    parser_enable.add_argument("site_pattern", help="Site name pattern")

    parser_disable = subparsers.add_parser("disable", help="Disable a site")
    parser_disable.add_argument("site_pattern", help="Site name pattern")

    parser_list = subparsers.add_parser("list", help="List available sites")

    parser_create = subparsers.add_parser("create", help="Create a new site")
    parser_create.add_argument("server_name", help="Server name")
    parser_create.add_argument("--listen", default="80", help="Listen address and port (default: 80)")

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        sys.exit(1)

    nginx_manage_site(args)

if __name__ == "__main__":
    main()
