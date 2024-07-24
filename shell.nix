let
  pkgs = import <nixpkgs> { };
  python_packages = p: with p; [
    requests
    beautifulsoup4
    prometheus_client
    gunicorn
  ];
in
pkgs.mkShell {
  buildInputs = [
    (pkgs.python3.withPackages python_packages)
  ];
  shellHook = '''';
}


