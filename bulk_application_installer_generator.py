from argparse import ArgumentParser
import json
from pathlib import Path
from create_installer import generate_installer

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-i', '--infile', type=str, required=True, help="path to JSON input file")
    parser.add_argument('-o', '--outfolder', type=str, required=True, help="path to place intunewin apps")
    parser.add_argument('-s', '--show', action="store_true", default=False)
    exclusion_group = parser.add_mutually_exclusive_group()
    exclusion_group.add_argument('-x', '--exclude', type=str, nargs="*", help="list of space-separated WingetId's to exclude. Case insensitive.")
    exclusion_group.add_argument('-X', '--excludefile', type=str, help="path to a json file containing an array of WingetIds to exclude. Exclusion is case insensitive.")
    return parser.parse_args()


def main():
    args = parse_args()
    infile_path = Path(args.infile)
    with infile_path.open("r") as f:
        applications = json.load(f)
    
    # Test for errors
    for application in applications:
        if "winget_id" not in application:
            raise ValueError("All applications must supply a valid 'winget_id' key")
        if not application["winget_id"]:
            raise ValueError(f"All applications must supply a valid 'winget_id' value. Received: {application['winget']}")
        matching_props = ["registry_key", "file_path", "display_name"]
        count_matches = len([application.get(a, None) for a in matching_props if application.get(a, None) is not None])
        if count_matches != 1:
            raise ValueError(f"All applications must contain exactly one of a 'file_path', 'display_name' or a 'registry_key' property")
    
    # Remove excluded ids
    # parsed as command line arguments
    if args.exclude:
        lower_cased_ids_to_exclude = [winget_id.lower() for winget_id in args.exclude]
        applications = [
            app
            for app
            in applications
            if app["winget_id"].lower() not in lower_cased_ids_to_exclude
        ]

    # ...or as a file path
    elif args.excludefile:
        p = Path(args.excludefile)
        with p.open('r') as f:
            exclusions = json.load(f)
            lower_cased_ids_to_exclude = [winget_id.lower() for winget_id in exclusions]
            applications = [
                app
                for app
                in applications
                if app["winget_id"].lower() not in lower_cased_ids_to_exclude
            ]

    # Build intunewin app
    for application in applications:
        winget_id = application["winget_id"]
        registry_key = None
        display_name = None
        file_path = None
        version = None
        if "registry_key" in application:
            registry_key = application["registry_key"]
        elif "display_name" in application:
            display_name = application["display_name"]
        elif "file_path" in application:
            file_path = application["file_path"]
        if "version" in application:
            version = application["version"]
        else:
            version = None
        
        generate_installer(winget_id=winget_id, registry_key=registry_key, file_path=file_path, display_name=display_name, version=version, output_parent_directory=Path(args.outfolder).absolute(), include_show_output=args.show)


if __name__ == '__main__':
    main()