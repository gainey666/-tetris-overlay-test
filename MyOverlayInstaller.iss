; ---------------------------------------------------------
; MyOverlayInstaller.iss – Inno Setup script
; ---------------------------------------------------------
[Setup]
AppName=My Overlay
AppVersion=1.0
AppPublisher=Your Company
AppPublisherURL=https://yourcompany.example.com
DefaultDirName={pf}\MyOverlay
DefaultGroupName=My Overlay
AllowNoIcons=yes
OutputBaseFilename=MyOverlay-Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "C:\TetrisOverlay\dist\MyOverlay.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\My Overlay"; Filename: "{app}\MyOverlay.exe"
Name: "{commondesktop}\My Overlay"; Filename: "{app}\MyOverlay.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\MyOverlay.exe"; Description: "Launch My Overlay now"; Flags: nowait postinstall skipifsilent
