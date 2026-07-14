[Setup]
AppName=Lock Manager
AppVersion=1.0
AppPublisher=Your Name
DefaultDirName={autopf}\Lock Manager
DefaultGroupName=Lock Manager
UninstallDisplayIcon={app}\ui.exe
OutputDir=installer_output
OutputBaseFilename=LockManagerSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\ui.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\lock_tool.dll"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Lock Manager"; Filename: "{app}\ui.exe"
Name: "{group}\Uninstall Lock Manager"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Lock Manager"; Filename: "{app}\ui.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\ui.exe"; Description: "Launch Lock Manager"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\LockManager"