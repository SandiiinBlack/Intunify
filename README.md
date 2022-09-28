# intunify
Python scripts to generate very specific intunewin packages

## bulk_application_installer_generator.py
Makes use of `create_installer.py` to generate a number of Intune Win32 apps taking a list of config dictionaries as input e.g.
```python
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
```

## create_installer.py
Generates an Intune Win32 app to install an application using winget.

### Known issues
* Is not able to expand path variables (e.g. %PROGRAMFILES%)

## create_uninstaller.py
Generates an Intune Win32 app to uninstall an application using the UninstallString registry key (either provided directly or by scanning the registry for matches on a DisplayName property value).