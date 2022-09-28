from create_installer import generate_installer

def main():
    applications = [
        {
            "winget_id": "Git.Git",
            "file_path": r"Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Git_is1",
        },
        {
            "winget_id": "WinSCP.WinSCP",
            "registry_key": r"Computer\HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\winscp3_is1",
            "version": "5.21.2"
        },
        {
            "winget_id": "PuTTY.PuTTY",
            "file_path": r"C:\Program Files\PuTTY",
        },
    ]
    for application in applications:
        if "winget_id" not in application:
            raise ValueError("All applications must supply a valid 'winget_id' key")
        if not application["winget_id"]:
            raise ValueError(f"All applications must supply a valid 'winget_id' value. Received: {application['winget']}")
        if not ("file_path" in application or "registry_key" in application):
            raise ValueError(f"All applications must contain either a 'file_path' or a 'registry_key' key")
        if ("file_path" in application and "registry_key" in application):
            raise ValueError(f"All applications must contain either a 'file_path' or a 'registry_key' key, not both")
    
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
        
        generate_installer(winget_id=winget_id, registry_key=registry_key, file_path=file_path, version=version)


if __name__ == '__main__':
    main()