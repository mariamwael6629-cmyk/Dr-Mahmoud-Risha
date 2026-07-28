' Starts the clinic server with no visible console window, using the
' virtualenv's pythonw.exe. Used by the "run at startup" Task Scheduler
' entry so the secretary/doctor never has to open a terminal manually.
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = strScriptPath
objShell.Run "venv\Scripts\pythonw.exe app.py", 0, False
