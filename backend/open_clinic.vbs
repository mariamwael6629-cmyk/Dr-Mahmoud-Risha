On Error Resume Next
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
objShell.CurrentDirectory = objFSO.GetParentFolderName(WScript.ScriptFullName)

objShell.Run "venv\Scripts\pythonw.exe app.py", 0, False
WScript.Sleep 3000

url = "http://127.0.0.1:5000"
chrome = ""
paths = Array( _
  objShell.ExpandEnvironmentStrings("%ProgramFiles%\Google\Chrome\Application\chrome.exe"), _
  objShell.ExpandEnvironmentStrings("%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"), _
  objShell.ExpandEnvironmentStrings("%LocalAppData%\Google\Chrome\Application\chrome.exe"))

For Each p In paths
  If chrome = "" Then
    If objFSO.FileExists(p) Then chrome = p
  End If
Next

If chrome <> "" Then
  objShell.Run """" & chrome & """ " & url, 1, False
Else
  objShell.Run url, 1, False
End If
