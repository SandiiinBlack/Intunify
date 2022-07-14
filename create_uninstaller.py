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

import subprocess
from pathlib import Path
from argparse import ArgumentParser, Namespace

def slugify(string: str) -> str:
    """Return a string replacing spaces with underscores and stripping double periods.

    Args:
        string (str)

    Returns:
        str
    """
    return string.replace(" ", "_").replace("..","")


def get_display_name() -> str:
    """Return the value of the name parameter parsed in from the command line

    Returns:
        str: args.name
    """
    parser = ArgumentParser()
    parser.add_argument('name', type=str, help="The value of the 'Display Name' registry key for the application to uninstall")
    args = parser.parse_args()
    return args.name


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


def copy_file(inf: Path, outf: Path, string_to_be_replaced: str, name: str) -> None:
    """Copies the contents of 'inf' to 'outf' replacing 'replacement_string' with 'name'

    Args:
        inf (Path): in file path
        outf (Path): out file path
        replacement_string (str): GUID found in 'inf' to be replaced in 'outf' with 'name'
        name (str): user input string that should correspond to the DisplayName registry value
    """
    with open(inf, "r") as f, outf.open("w") as g:
        text = f.read().replace(string_to_be_replaced, name)
        g.write(text)
    

def copy_known_file(inf: Path, outf: Path, guid: str, guid_replacement: str, path_to_replace: str, replacement_path: str) -> None:
    r"""Copies the contents of 'inf' to 'outf' replacing 'replacement_string' with 'name'

    Args:
        inf (Path): in file path
        outf (Path): out file path
        replacement_string (str): GUID found in 'inf' to be replaced in 'outf' with 'name'
        name (str): user input string that should correspond to the DisplayName registry value
        path_to_replace (str): another GUID to replace
        replacement_path (str): path of the registry key, should take the format
        "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{F307E329-805A-4C79-BAEC-7FB35F3FE64B}"
    """
    with open(inf, "r") as f, outf.open("w") as g:
        if not replacement_path.startswith("HKEY_LOCAL_MACHINE"):
            raise ValueError(f"replacement_path must start with HKEY_LOCAL_MACHINE")
        replacement_path = replacement_path.replace("HKEY_LOCAL_MACHINE", "HKLM:")
        text = f.read().replace(guid, guid_replacement).replace(path_to_replace, replacement_path)
        g.write(text)

def create_intunewin_file(slug: str) -> None:
    """Generate an .intunewin file from the folder contents.

    Requires IntuneWinAppUtil.exe to be installed and on the path.

    Args:
        slug (str): slug of the folder name
    """
    try:
        subprocess.run(
            [
                f"IntuneWinAppUtil.exe", 
                f"-c", 
                f".\{slug}\\", 
                f"-s", 
                f".\{slug}\\uninstall.ps1",
                f"-o", 
                f".\{slug}\\"
            ], 
            timeout=15
        )
    except FileNotFoundError as exc:
        print(f"Unable to generate {slug}.intunewin file because the IntuneWinAppUtil executable could not be found.")
    except subprocess.CalledProcessError as exc:
        print(
            f"Process failed because did not return a successful return code. "
            f"Returned {exc.returncode}\n{exc}"
        )
    except subprocess.TimeoutExpired as exc:
        print(f"Process timed out.\n{exc}")


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


    create_intunewin_file(display_name)

if __name__ == "__main__":
    main()