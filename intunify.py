import subprocess
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Tuple


def slugify(string: str) -> str:
    """Return a string replacing spaces with underscores and stripping double periods.

    Args:
        string (str)

    Returns:
        str
    """
    return string.replace(" ", "_").replace("..","")

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

def copy_nary_file(inf: Path, outf: Path, replacements: List[Tuple[str, str]] or None = None, affixment=None) -> None:
    r"""Copies the contents of 'inf' to 'outf' replacing 'replacement_string' with 'name'

    Args:
        inf (Path): in file path
        outf (Path): out file path
        replacements: List[Tuple[str, str]] or None (to_replace, replacer)
    """
    with open(inf, "r") as f, outf.open("w") as g:
        text = f.read()
        if replacements:
            for guid, replacement in replacements:
                replacement = replacement.replace(r"Computer\"HKEY_LOCAL_MACHINE", "HKEY_LOCAL_MACHINE").replace("HKEY_LOCAL_MACHINE", "HKLM:").replace("'", "''")
                text = text.replace(guid, replacement)
        if affixment:
            text += affixment
        g.write(text)




def create_intunewin_file(slug: str, source_file: str, cwd=Path.cwd()) -> None:
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
                f".\{slug}\\{source_file}",
                f"-o", 
                f".\{slug}\\",
                f"-q"
            ], 
            timeout=15,
            cwd=cwd
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


def get_winget_show_output(winget_id):
    """Generate a "package_details.yaml" file using the winget show command.

    Requires IntuneWinAppUtil.exe to be installed and on the path.

    Args:
        winget_id (str): --id of the application.
    """
    try:
        out = subprocess.check_output(
            [
                f"winget.exe",
                f"show",
                f"--exact", 
                f"--id", 
                f"{winget_id}"
            ], 
            timeout=15
        )
        return out.decode()
    except FileNotFoundError as exc:
        print(f"Unable to generate {winget_id}.package_details file because the winget executable could not be found.")
    except subprocess.CalledProcessError as exc:
        print(
            f"Process failed because did not return a successful return code. "
            f"Returned {exc.returncode}\n{exc}"
        )
    except subprocess.TimeoutExpired as exc:
        print(f"Process timed out.\n{exc}")


# TODO: Confirm if this is still used
def get_display_name() -> str:
    """Return the value of the name parameter parsed in from the command line

    Returns:
        str: args.name
    """
    parser = ArgumentParser()
    parser.add_argument('name', type=str, help="The value of the 'Display Name' registry key for the application to uninstall")
    args = parser.parse_args()
    return args.name
