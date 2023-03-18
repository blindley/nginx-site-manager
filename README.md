# Nginx Site Manager

Nginx Site Manager is a command-line utility to manage Nginx virtual host configurations on a server. It allows you to enable, disable, create, and list available sites with ease. The script is written in Python and is compatible with Python 3.

## Features

- Enable or disable sites by creating or removing symlinks in the `sites-enabled` directory
- List available sites and their statuses (enabled or disabled)
- Create new Nginx virtual host configurations with reasonable default values
- Reload Nginx configuration automatically after enabling or disabling a site

## Installation

1. Clone the repository or download the `nginx_site_manager.py` script.
2. Move the script to a directory in your system's PATH, such as `/usr/local/bin/`, and rename it to `nginx-site-manager`: `$ sudo mv nginx_site_manager.py /usr/local/bin/nginx-site-manager`
3. Make the script executable: `$ sudo chmod +x /usr/local/bin/nginx-site-manager`


## Usage

Run `nginx-site-manager` with the desired action and any necessary arguments:

- Enable a site: `sudo nginx-site-manager enable [site_pattern]`
- Disable a site: `sudo nginx-site-manager disable [site_pattern]`
- List available sites: `sudo nginx-site-manager list`
- Create a new site: `sudo nginx-site-manager create [server_name] [--listen LISTEN]`

`[site_pattern]` is a pattern that matches the site's configuration file name in the `sites-available` directory. The script will look for files that match the pattern and enable or disable them accordingly. If multiple matching files are found, you must provide a more specific pattern or use a glob pattern.

`[server_name]` is the server name (domain) for the new site.

`[--listen LISTEN]` is an optional argument for the `create` action to specify the listen address and port (default: 80).

## Examples

- Enable a site: `sudo nginx-site-manager enable example`
- Disable a site: `sudo nginx-site-manager disable example`
- List available sites: `sudo nginx-site-manager list`
- Create a new site: `sudo nginx-site-manager create example.com`
- Create a new site with a custom listen address and port: `sudo nginx-site-manager create example.com --listen 8080`

## Note

The script requires root privileges to modify Nginx configurations and reload the Nginx service. Use `sudo` when running the script.
