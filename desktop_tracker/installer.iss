; LifeOS Desktop Agent — Inno Setup Installer Script
; This creates a professional Windows installer (.exe setup file)
; Prerequisites: Install Inno Setup from https://jrsoftware.org/isinfo.php
; Then right-click this file -> Compile with Inno Setup

[Setup]
AppName=POLARIS Desktop Agent
AppVersion=1.0.0
AppPublisher=LifeOS
AppPublisherURL=http://localhost:5173
DefaultDirName={autopf}\POLARIS Desktop Agent
DefaultGroupName=POLARIS
OutputDir=installer_output
OutputBaseFilename=POLARIS_Setup_v1.0.0
SetupIconFile=
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
UninstallDisplayIcon={app}\LifeOS_Tracker.exe
LicenseFile=
DisableProgramGroupPage=yes
DisableDirPage=no

[Files]
Source: "dist\LifeOS_Tracker.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env.example"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\POLARIS Desktop Agent"; Filename: "{app}\LifeOS_Tracker.exe"
Name: "{autodesktop}\POLARIS Desktop Agent"; Filename: "{app}\LifeOS_Tracker.exe"
Name: "{userstartup}\POLARIS Desktop Agent"; Filename: "{app}\LifeOS_Tracker.exe"; Comment: "Start POLARIS on login"

[Run]
Filename: "{app}\LifeOS_Tracker.exe"; Description: "Launch POLARIS Desktop Agent"; Flags: nowait postinstall skipifsilent
