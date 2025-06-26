!include "MUI2.nsh"
!include "nsDialogs.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "WinMessages.nsh"

Name "Secure Mission Viewer"
OutFile "SecureMissionInstaller.exe"
InstallDir "$LOCALAPPDATA\SecureMissionViewer"
RequestExecutionLevel admin

Var OTP
Var OTPField
Var Dialog

!define MUI_WELCOMEPAGE_TITLE "Welcome to Secure Mission Viewer Installer"
!define MUI_WELCOMEPAGE_TEXT "This secure application provides device-bound, time-restricted access to encrypted mission files.$\r$\nEnsure you have a valid Mission OTP before proceeding."

!define MUI_FINISHPAGE_TEXT "Installation complete. Launch Secure Viewer from your desktop to begin secure access.$\r$\nYour access is time-limited and device-locked."

!define MUI_ABORTWARNING

; === Pages === 
!define MUI_ICON "logo.ico"
!define MUI_UNICON "logo.ico"
!insertmacro MUI_PAGE_WELCOME
Page custom OTPPage OTPPageLeave
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "Install Secure Mission Viewer"

  ReadRegDWORD $0 HKCU "Software\DefenseViewer" "Installed"
  IntCmp $0 1 alreadyInstalled

  SetOutPath "$INSTDIR"
  File "dist\viewer.exe"
  File "logo.ico"

  ; UUID Binding
  StrCpy $1 "$TEMP\bind_uuid.ps1"
  File "/oname=$1" "bind_uuid.ps1"
  nsExec::Exec '"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -File "$1"'
  Pop $0
  DetailPrint "bind_uuid.ps1 exit code: $0"
  Delete "$1"

  CreateShortCut "$DESKTOP\Mission Viewer.lnk" "$INSTDIR\viewer.exe" "" "$INSTDIR\logo.ico"
  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegDWORD HKCU "Software\DefenseViewer" "Installed" 1

  Goto done

  alreadyInstalled:
    MessageBox MB_ICONSTOP "Secure Mission Viewer is already installed on this system. Reinstallation denied."
    Abort

  done:
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\viewer.exe"
  Delete "$DESKTOP\Mission Viewer.lnk"
  Delete "$INSTDIR\uninstall.exe"
  Delete "$INSTDIR\logo.ico"
  RMDir "$INSTDIR"

  ExecWait 'attrib -h -s "%LOCALAPPDATA%\Microsoft\CLR\Cache\winmm.dll"'
  Delete "$LOCALAPPDATA\Microsoft\CLR\Cache\winmm.dll"
  ExecWait 'attrib -h -s "$LOCALAPPDATA\Microsoft\CLR\Cache\wmmc.dat"'
  Delete "$LOCALAPPDATA\Microsoft\CLR\Cache\wmmc.dat"

  DeleteRegKey HKCU "Software\DefenseViewer"
SectionEnd

Function OTPPage
  nsDialogs::Create 1018
  Pop $Dialog
  ${If} $Dialog == error
    Abort
  ${EndIf}

  ; === Header Label ===
  ${NSD_CreateLabel} 0 0 100% 14u "Mission Authorization"
  Pop $0
  CreateFont $1 "Segoe UI Bold" 12 700
  SendMessage $0 ${WM_SETFONT} $1 1

  ; === Instructional Text ===
  ${NSD_CreateLabel} 0 18u 100% 30u "Visit the mission portal and enter your email ID to receive a one-time authorization code (OTP). Then enter the OTP below to proceed with installation."
  Pop $0

  ; === OTP Input Field Label ===
  ${NSD_CreateLabel} 0 56u 100% 12u "Enter Mission Authorization Code (OTP):"
  Pop $0

  ; === OTP Input Field ===
  ${NSD_CreateText} 0 70u 100% 12u ""
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

  StrCpy $1 "$1" 2
  DetailPrint "Trimmed OTP Result: $1"

  StrCmp $1 "ok" +3
    MessageBox MB_ICONSTOP "Authorization failed. Invalid or expired mission code."
    Abort
FunctionEnd
