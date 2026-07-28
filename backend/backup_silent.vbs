' Runs the USB backup script with no visible console window. Used by the
' Task Scheduler "repeat every 1 hour" trigger so it doesn't flash a black
' window on the secretary/doctor's screen every time it fires.
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = strScriptPath
objShell.Run "backup_to_usb.bat", 0, True
