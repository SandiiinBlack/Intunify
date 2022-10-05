r"""create_uninstaller.py

This script takes as input:
Positional argument(s):
    winget_id   The exact '--id' value to install an applicaition using winget
                

Optional argument(s):
    -v, --version   If supplied, the generated powershell script will specify this version
                    to install
    -k, --key       If supplied, the generated detection script will use this
                    registry key as evidence of successful installation
    -f, --file      If supplied, the generated detection script will use the existence of this
                    file as evidence of successful installation

                    If neither --key or --file are supplied, an Exception is raised

And creates a folder containin the following files:
    \path\to\current\directory\{name}
        \README.md
        \detect.ps1
        \install.ps1
        \uninstall.ps1

If IntuneWinAppUtil.exe is installed and on the PATH it will create an INTUNEWIN
package in the same directory e.g.
    \path\to\current\directory\{name}
        \install.intunewin
"""


from pathlib import Path
from argparse import ArgumentParser, Namespace
from intunify import copy_nary_file, slugify, create_intunewin_file


def get_args() -> Namespace:
    """Return the arguments parsed in from the command line

    Returns:
        Namespace: args
    """
    parser = ArgumentParser()
    parser.add_argument(
        "winget_id",
        type=str,
        help="The value of the '--id' value expected by winget to install the appliation. Also used to name folder.",
    )
    parser.add_argument(
        "-v",
        "--version",
        type=str,
        help='version number to install. Defaults to None (latest) e.g. "2.37.3"',
    )
    parser.add_argument(
        "-k",
        "--key",
        type=str,
        help=r'Registry key path whose existence will be used as evidence of successful installation. e.g. "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{806133d5-0a8a-48d2-a337-3a97013d4f27}"',
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help=r'/path/to/file whose existence will be used as evidence of successful installation. e.g. "%PROGRAMFILES%\Mozilla Firefox\uninstall.exe"',
    )
    args = parser.parse_args()
    if not (args.key or args.file):
        parser.error("Must supply either --key or --file arguments.")
    if args.key and args.file:
        parser.error("Must supply either --key or --file arguments, not both.")
    return args


def main() -> None:
    """
    Generate an installer package from the commandline. Run create_installer.py -h for usage.
    """
    args = get_args()
    winget_id = args.name
    version = args.version
    registry_key = args.key
    file_path = args.file

    generate_installer(winget_id, registry_key, file_path, version)


def generate_installer(winget_id, registry_key=None, file_path=None, version=None, output_parent_directory = Path.cwd()):
    """Given a winget_id value, a registry key or a file path as evidence of successful installation,
    and optionally a version strig, generates a folder containing an install script,
    a detection script, an uninstall script and a README.md file.

    If IntuneWinAppUtil.exe exists on the PATH, it will also generate an intunewin file.
    """
    if not(registry_key or file_path):
        raise ValueError('Must supply either a registry_key or file_path as evidence of successful installation. Neither supplied.')
    elif (registry_key and file_path):
        raise ValueError('Must supply either a registry_key or file_path as evidence of successful installation. Both supplied.')
    
    WINGET_ID_TO_REPLACE = "a369b91c-188f-4adc-899b-3a47d38c3ce7"
    PATH_TO_REPLACE = "5e56c978-80c2-4369-aafb-037cab7dda93"
    VERSION_TO_REPLACE = "de6a4f36-0b0c-46de-b491-36960cbcee2d"

    slug = slugify(winget_id)
    version_string = f"--version '{version}'" if version else ""

    script_dir = Path(__file__).parent
    templates_dir = script_dir / "_installer_template"

    # Template file paths
    readme_template = templates_dir / "README.template"
    installation_template = templates_dir / "install.template"

    detection_template = templates_dir / "detect.template"
    known_key_detection_template = templates_dir / "known_key_detect.template"

    uninstallation_template = templates_dir / "uninstall.template"
    known_key_uninstallation_template = templates_dir / "known_key_uninstall.template"

    # Output file paths
    Path.mkdir(output_parent_directory, exist_ok=True)
    output_directory = output_parent_directory / slug
    Path.mkdir(output_directory, exist_ok=True)

    readme_output_file_path = output_directory / "README.md"
    install_output_file_path = output_directory / "install.ps1"
    uninstall_output_file_path = output_directory / "uninstall.ps1"
    detect_output_file_path = output_directory / "detect.ps1"

    # Always copy the README
    copy_nary_file(
        readme_template, readme_output_file_path, [(WINGET_ID_TO_REPLACE, winget_id)]
    )

    # Always copy the installation file
    copy_nary_file(
        installation_template,
        install_output_file_path,
        [(VERSION_TO_REPLACE, version_string)],
    )

    # We prefer args.key to args.file (and exit if both or neither are supplied)

    if registry_key:
        # Copy known_detection_template and known_uninstall template
        copy_nary_file(
            known_key_detection_template,
            detect_output_file_path,
            [(PATH_TO_REPLACE, registry_key)],
        )
        copy_nary_file(
            known_key_uninstallation_template,
            uninstall_output_file_path,
            [(PATH_TO_REPLACE, registry_key)],
        )
    else:
        # Detect based on file evidence
        copy_nary_file(
            detection_template,
            detect_output_file_path,
            [(WINGET_ID_TO_REPLACE, file_path)],
        )
        # File doesn't require any template replacements
        copy_nary_file(uninstallation_template, uninstall_output_file_path)

    create_intunewin_file(winget_id, "install.ps1", cwd=output_parent_directory)


if __name__ == "__main__":
    main()
