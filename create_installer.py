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
from intunify import copy_nary_file, slugify, create_intunewin_file, get_winget_show_output


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
    detections = parser.add_mutually_exclusive_group()
    detections.add_argument(
        "-k",
        "--key",
        type=str,
        help=r'Registry key path whose existence will be used as evidence of successful installation. e.g. "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{806133d5-0a8a-48d2-a337-3a97013d4f27}"',
    )
    detections.add_argument(
        "-f",
        "--file",
        type=str,
        help=r'/path/to/file whose existence will be used as evidence of successful installation. e.g. "%PROGRAMFILES%\Mozilla Firefox\uninstall.exe"',
    )
    detections.add_argument(
        "-d",
        "--display_name",
        type=str,
        help=r'DisplayName property an exact match to a registry key will be used as evidence of successful installation. e.g. "Docker Desktop"',
    )
    parser.add_argument(
        "-s",
        '--show', 
        action="store_true", 
        default=False,
        help=r'Save winget show output to "package_details.yaml" file.',
    )
    args = parser.parse_args()
    if not (args.key or args.file or args.display_name):
        parser.error("Must supply either --key, --file, or --display_name arguments.")
    return args


def main() -> None:
    """
    Generate an installer package from the command line. Run create_installer.py -h for usage.
    """
    args = get_args()
    winget_id = args.winget_id
    version = args.version
    registry_key = args.key
    file_path = args.file
    display_name = args.display_name

    generate_installer(winget_id=winget_id, registry_key=registry_key, file_path=file_path, display_name=display_name, version=version, include_show_output=args.show)


def generate_installer(winget_id, registry_key=None, file_path=None, display_name=None, version=None, output_parent_directory = Path.cwd(), include_show_output=False):
    """Given a winget_id value, a registry key or a file path as evidence of successful installation,
    and optionally a version string, generates a folder containing an install script,
    a detection script, an uninstall script and a README.md file.

    If IntuneWinAppUtil.exe exists on the PATH, it will also generate an intunewin file.
    """
    required_mutually_exclusive_args = [registry_key, file_path, display_name]
    supplied_mutually_exclusive_args = [a for a in required_mutually_exclusive_args if a is not None]
    if len(supplied_mutually_exclusive_args) != 1:
        raise ValueError("Must supply exactly one of a registry_key, a registry key's DisplayName value or a file_path as evidence of successful installation.")

    
    WINGET_ID_TO_REPLACE = "a369b91c-188f-4adc-899b-3a47d38c3ce7"
    PATH_TO_REPLACE = "5e56c978-80c2-4369-aafb-037cab7dda93"
    VERSION_TO_REPLACE = "de6a4f36-0b0c-46de-b491-36960cbcee2d"
    REGISTRY_DISPLAY_NAME_TO_REPLACE = "188e7e89-6fe4-44f0-8302-08972f8a6a34"

    slug = slugify(winget_id)
    version_string = f"--version '{version}'" if version else ""

    script_dir = Path(__file__).parent
    templates_dir = script_dir / "_installer_template"

    # Template file paths
    readme_template = templates_dir / "README.template"
    installation_template = templates_dir / "install.template"

    detection_template = templates_dir / "detect.template"
    known_display_name_detection_template = templates_dir / "known_display_name_detect.template"
    known_key_detection_template = templates_dir / "known_key_detect.template"

    uninstallation_template = templates_dir / "uninstall.template"
    known_display_name_uninstallation_template = templates_dir / "known_display_name_uninstall.template"
    known_key_uninstallation_template = templates_dir / "known_key_uninstall.template"

    # Output file paths
    Path.mkdir(output_parent_directory, exist_ok=True)
    output_directory = output_parent_directory / slug
    Path.mkdir(output_directory, exist_ok=True)

    readme_output_file_path = output_directory / "README.md"
    install_output_file_path = output_directory / "install.ps1"
    uninstall_output_file_path = output_directory / "uninstall.ps1"
    detect_output_file_path = output_directory / "detect.ps1"

    # Run winget show, massage output and save as package_details.yaml if run with --show.
    if include_show_output:
        try:
            winget_show_output_file_path = output_directory / "package_details.yaml"

            # Need to convert to LF for correct handling by Python
            winget_show_output = get_winget_show_output(winget_id).replace('\r\n', '\n')

            winget_show_output = winget_show_output[winget_show_output.find('Found'):].replace('Found ', 'Found: ')
            with winget_show_output_file_path.open('w', encoding='utf-8') as f:
                f.write(winget_show_output)
        except UnicodeEncodeError as e:
            print(f"Encounted a decoding error when parsing winget show output for {winget_id}. Skipping...")
            print(e)

    # Always copy the README
    copy_nary_file(
        readme_template, readme_output_file_path, [(WINGET_ID_TO_REPLACE, winget_id)])

    # Always copy the installation file
    copy_nary_file(
        installation_template,
        install_output_file_path,
        [(VERSION_TO_REPLACE, version_string), (WINGET_ID_TO_REPLACE, winget_id)],
    )

    # We prefer args.key to args.displayname to args.file (and exit if other than one is supplied)

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
    elif display_name:
        copy_nary_file(
            known_display_name_detection_template,
            detect_output_file_path,
            [(REGISTRY_DISPLAY_NAME_TO_REPLACE, display_name)],
        )
        copy_nary_file(
            known_display_name_uninstallation_template,
            uninstall_output_file_path,
            [(REGISTRY_DISPLAY_NAME_TO_REPLACE, display_name)],
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
