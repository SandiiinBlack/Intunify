from argparse import ArgumentParser
import json
from pathlib import Path
from create_installer import generate_installer

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-i', '--infile', type=str, required=True, help="path to JSON input file")
    parser.add_argument('-o', '--outfolder', type=str, required=True, help="path to place intunewin apps")
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
        if not ("file_path" in application or "registry_key" in application):
            raise ValueError(f"All applications must contain either a 'file_path' or a 'registry_key' key")
        if ("file_path" in application and "registry_key" in application):
            raise ValueError(f"All applications must contain either a 'file_path' or a 'registry_key' key, not both")
    
    # Build intunewin app
    for application in applications:
        winget_id = application["winget_id"]
        registry_key = None
        file_path = None
        version = None
        if "registry_key" in application:
            registry_key = application["registry_key"]
        elif "file_path" in application:
            file_path = application["file_path"]
        if "version" in application:
            version = application["version"]
        else:
            version = None
        
        generate_installer(winget_id=winget_id, registry_key=registry_key, file_path=file_path, version=version, output_parent_directory=Path(args.outfolder).absolute())


if __name__ == '__main__':
    main()