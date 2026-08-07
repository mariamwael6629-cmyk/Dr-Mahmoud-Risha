Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
objShell.CurrentDirectory = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.Run "venv\Scripts\pythonw.exe app.py", 0, False
WScript.Sleep 2500
objShell.Run "http://127.0.0.1:5000", 1, False
