!include "MUI2.nsh"

Name "Secure Viewer"
OutFile "SecureViewerInstaller.exe"
InstallDir "$LOCALAPPDATA\SecureViewer"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "Install Secure Viewer"

  SetOutPath "$INSTDIR"
  File "dist\viewer.exe"
  File "bind_uuid.ps1"

  ; ✅ Run PowerShell script to create viewer.auth
  nsExec::Exec '"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -File "$INSTDIR\bind_uuid.ps1"'
  Pop $0
  DetailPrint "🔧 bind_uuid.ps1 exit code: $0"

  CreateShortCut "$DESKTOP\Secure Viewer.lnk" "$INSTDIR\viewer.exe"
  WriteUninstaller "$INSTDIR\uninstall.exe"

SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\viewer.exe"
  Delete "$INSTDIR\bind_uuid.ps1"
  Delete "$LOCALAPPDATA\SecureViewer\viewer.auth"
  Delete "$DESKTOP\Secure Viewer.lnk"
  Delete "$INSTDIR\uninstall.exe"
  RMDir "$INSTDIR"
SectionEnd
