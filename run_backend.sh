#!/bin/sh
nix-shell -p python311 python311Packages.flask python311Packages.flask-cors python311Packages.requests python311Packages.python-dotenv --run 'python3 main.py'
