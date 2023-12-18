; Set the name of the installer
Name "HSR-AGENT"

; Set the default installation directory
InstallDir "$PROGRAMFILES\HSRAgent"

; Request application privileges for Windows Vista or higher
RequestExecutionLevel admin

; Include Modern UI
!include "MUI2.nsh"

; Define the interface for the installer
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section
    SetOutPath $INSTDIR
    ; Copy files
    File "C:\Users\novak\hsr-agent\dist\agent.exe" ; Replace with your application files
    File "C:\Users\novak\hsr-agent\icon.jpg" ; Replace with your application files

    ; Create autorun registry entry
    WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Run" "HSR-AGENT" '"$INSTDIR\agent.exe"'
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

; Uninstaller section
;UninstPage uninstConfirm
;UninstallDelete $INSTDIR\*.* ; Delete installed files
;RMDir $INSTDIR ; Remove installation directory if empty

; Write uninstaller registry info

; Define uninstaller section
Section "Uninstall"
    ; Remove autorun registry entry
    DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Run" "HSR-AGENT"

    Delete $INSTDIR\*.* ; Delete installed files
    RMDir $INSTDIR ; Remove installation directory if empty
SectionEnd

Function .onInstSuccess
    Exec '"$INSTDIR\agent.exe"' ; Replace YourApp.exe with your application's executable
FunctionEnd