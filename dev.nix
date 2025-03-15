{ pkgs ? import <nixpkgs> {} }:

{
  devshell = {
    packages = with pkgs; [
      python311
      python311Packages.flask
      python311Packages.flask-cors
      python311Packages.requests
      python311Packages.python-dotenv
    ];
  };
}