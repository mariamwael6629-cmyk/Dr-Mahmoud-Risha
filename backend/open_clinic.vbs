On Error Resume Next
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
baseDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = baseDir

pythonw = baseDir & "\venv\Scripts\pythonw.exe"
If Not objFSO.FileExists(pythonw) Then
    objShell.Run """" & baseDir & "\install_clinic.bat""", 1, True
End If

objShell.Run "venv\Scripts\pythonw.exe app.py", 0, False

url = "http://127.0.0.1:5000"
ready = False
For i = 1 To 45
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.open "GET", url, False
    http.send
    If Err.Number = 0 And http.Status >= 200 Then
        ready = True
        Exit For
    End If
    Err.Clear
    WScript.Sleep 1000
Next

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
