r"""create_uninstaller.py

This script takes as input:
Positional argument(s):
    name        Either the exact DisplayName value of the registry key from which 
                to find an UninstallString. If --key is suppied, this value is
                only used in naming the folder and in the README.md

Optional argument(s):
    -k, --key   If supplied, the generated powershell scripts will target this
                registry key directly, rather than looping through all until
                a match on the DisplayName property is found

And creates a folder containin the following files:
    \path\to\current\directory\{name}
        \README.md
        \detect.ps1
        \uninstall.ps1

If IntuneWinAppUtil.exe is installed and on the PATH it will create an INTUNEWIN
package in the same directory e.g.
    \path\to\current\directory\{name}
        \uninstall.intunewin
"""


from pathlib import Path
from argparse import ArgumentParser, Namespace
from intunify import slugify, copy_file, copy_known_file, create_intunewin_file






def get_args() -> Namespace:
    """Return the arguments parsed in from the command line

    Returns:
        Namespace: args
    """
    parser = ArgumentParser()
    parser.add_argument('name', type=str, help="The value of the 'Display Name' registry key for the application to uninstall. Also used to name folder.")
    parser.add_argument('-k', '--key', type=str, help=r'Registry key path of application to uninstall (if known). e.g. "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{806133d5-0a8a-48d2-a337-3a97013d4f27}"')
    args = parser.parse_args()
    return args







def main() -> None:
    """Given a Display Name registry key value, generates a folder containing an uninstall script,
    a detection script and a README.md file. If IntuneWinAppUtil.exe exists on the PATH, it will
    also generate an intunewin file.
    """
    DISPLAY_NAME_TO_REPLACE = "a369b91c-188f-4adc-899b-3a47d38c3ce7"
    PATH_TO_REPLACE = "5e56c978-80c2-4369-aafb-037cab7dda93"
    
    args = get_args()
    display_name = args.name
    slug = slugify(display_name)

    script_dir = Path(__file__).parent
    templates_dir = script_dir / "_uninstaller_template"
    detection_template = templates_dir / "detect.template"
    known_key_detection_template = templates_dir / "known_key_detect.template"
    uninstallation_template = templates_dir / "uninstall.template"
    known_key_uninstallation_template = templates_dir / "known_key_uninstall.template"
    readme_template = templates_dir / "README.template"

    output_directory = Path.cwd() / slug
    Path.mkdir(output_directory, exist_ok=True)

    readme = output_directory / "README.md"
    uninstall = output_directory / "uninstall.ps1"
    detect = output_directory / "detect.ps1"

    copy_file(readme_template, readme, DISPLAY_NAME_TO_REPLACE, display_name)
    if args.key:
        copy_known_file(known_key_detection_template, detect, DISPLAY_NAME_TO_REPLACE, display_name, PATH_TO_REPLACE, args.key)
        copy_known_file(known_key_uninstallation_template, uninstall, DISPLAY_NAME_TO_REPLACE, display_name, PATH_TO_REPLACE, args.key)
    else:
        copy_file(detection_template, detect, DISPLAY_NAME_TO_REPLACE, display_name)
        copy_file(uninstallation_template, uninstall, DISPLAY_NAME_TO_REPLACE, display_name)


    create_intunewin_file(display_name, "uninstall.ps1")

if __name__ == "__main__":
    main()