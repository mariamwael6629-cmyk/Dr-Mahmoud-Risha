On Error Resume Next
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
baseDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = baseDir

If Not objFSO.FileExists(baseDir & "\venv\Scripts\pythonw.exe") Then
    objShell.Run """" & baseDir & "\install_clinic.bat""", 1, True
End If

startupLnk = objShell.SpecialFolders("Startup") & "\Clinic Server.lnk"
If Not objFSO.FileExists(startupLnk) Then
    Set sc = objShell.CreateShortcut(startupLnk)
    sc.TargetPath = baseDir & "\run_silent.vbs"
    sc.WorkingDirectory = baseDir
    sc.Save
End If

desktopLnk = objShell.SpecialFolders("Desktop") & "\Dr Mahmoud Risha Clinic.lnk"
If Not objFSO.FileExists(desktopLnk) Then
    Set ds = objShell.CreateShortcut(desktopLnk)
    ds.TargetPath = WScript.ScriptFullName
    ds.WorkingDirectory = baseDir
    ds.Save
End If

objShell.Run "venv\Scripts\pythonw.exe app.py", 0, False

url = "http://127.0.0.1:5000"
For i = 1 To 45
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.open "GET", url, False
    http.send
    If Err.Number = 0 And http.Status >= 200 Then Exit For
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
