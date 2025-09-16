{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python_packages = p: with p; [ requests beautifulsoup4 prometheus_client gunicorn ];
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [ (pkgs.python3.withPackages python_packages) ];
          shellHook = "";
        };
      });
}
