import subprocess
from pathlib import Path
from argparse import ArgumentParser

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
    REPLACEMENT = "a369b91c-188f-4adc-899b-3a47d38c3ce7"
    name = get_display_name()
    slug = slugify(name)

    script_dir = Path(__file__).parent
    templates_dir = script_dir / "_uninstaller_template"
    detection_template = templates_dir / "detect.template"
    uninstallation_template = templates_dir / "uninstall.template"
    readme_template = templates_dir / "README.template"

    output_directory = Path.cwd() / slug
    Path.mkdir(output_directory, exist_ok=True)
    readme = output_directory / "README.md"
    uninstall = output_directory / "uninstall.ps1"
    detect = output_directory / "detect.ps1"

    copy_file(readme_template, readme, REPLACEMENT, name)
    copy_file(detection_template, detect, REPLACEMENT, name)
    copy_file(uninstallation_template, uninstall, REPLACEMENT, name)

    create_intunewin_file(name)

if __name__ == "__main__":
    main()