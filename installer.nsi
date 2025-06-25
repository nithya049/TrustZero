!include "MUI2.nsh"
!include "nsDialogs.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "WinMessages.nsh"

Name "Secure Viewer"
OutFile "SecureViewerInstaller.exe"
InstallDir "$LOCALAPPDATA\SecureViewer"
RequestExecutionLevel admin

Var OTP
Var OTPField
Var Dialog

Page custom OTPPage OTPPageLeave
Page directory
Page instfiles

Section "Install Secure Viewer"

  ; Check if already installed
  ReadRegDWORD $0 HKCU "Software\SystemHealth" "RunState"
  IntCmp $0 1 alreadyInstalled

  ; ==== Proceed with normal installation ====
  SetOutPath "$INSTDIR"
  File "dist\viewer.exe"

  ; Run bind script
  StrCpy $1 "$TEMP\bind_uuid.ps1"
  File "/oname=$1" "bind_uuid.ps1"

  nsExec::Exec '"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -File "$1"'
  Pop $0
  DetailPrint "bind_uuid.ps1 exit code: $0"
  Delete "$1"

  CreateShortCut "$DESKTOP\Secure Viewer.lnk" "$INSTDIR\viewer.exe"
  WriteUninstaller "$INSTDIR\uninstall.exe"
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

  ExecWait 'attrib -h -s "%LOCALAPPDATA%\Microsoft\CLR\Cache\winmm.dll"'
  Delete "$LOCALAPPDATA\Microsoft\CLR\Cache\winmm.dll"
  ExecWait 'attrib -h -s "$LOCALAPPDATA\Microsoft\CLR\Cache\wmmc.dat"'
  Delete "$LOCALAPPDATA\Microsoft\CLR\Cache\wmmc.dat"


  DeleteRegKey HKCU "Software\SystemHealth"
SectionEnd

Function OTPPage
  nsDialogs::Create 1018
  Pop $Dialog
  ${If} $Dialog == error
    Abort
  ${EndIf}

  ${NSD_CreateLabel} 0 0 100% 12u "Enter your One-Time Password:"
  Pop $0

  ${NSD_CreateText} 0 12u 100% 12u ""
  Pop $OTPField

  nsDialogs::Show
  Pop $0
FunctionEnd

Function OTPPageLeave
  ${NSD_GetText} $OTPField $OTP
  DetailPrint "Entered OTP: $OTP"

  SetOutPath "$TEMP"
  File "dist\validate_token.exe"

  nsExec::ExecToStack '"$TEMP\validate_token.exe" "$OTP"'
  Pop $0 ; exit code
  Pop $1 ; stdout
  DetailPrint "OTP Validation Raw Output: $1"

  StrCpy $1 "$1" 2 ; Strip trailing \n or \r\n
  DetailPrint "Trimmed OTP Result: $1"

  StrCmp $1 "ok" +3
  MessageBox MB_ICONSTOP "Invalid or already used OTP. Installation aborted."
  Abort
FunctionEnd