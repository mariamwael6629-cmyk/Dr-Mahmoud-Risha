On Error Resume Next
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
baseDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = baseDir

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

url = "http://127.0.0.1:5000"

objShell.Run "pythonw app.py", 0, False

If Not ServerUp(objShell, url, 8) Then
    objShell.Run """" & baseDir & "\install_clinic.bat""", 1, True
    objShell.Run "pythonw app.py", 0, False
    ServerUp objShell, url, 45
End If

OpenChrome objShell, objFSO, url

Function ServerUp(sh, u, seconds)
    Dim k, http
    ServerUp = False
    For k = 1 To seconds
        Set http = CreateObject("MSXML2.XMLHTTP")
        http.open "GET", u, False
        http.send
        If Err.Number = 0 And http.Status >= 200 Then
            ServerUp = True
            Exit Function
        End If
        Err.Clear
        WScript.Sleep 1000
    Next
End Function

Sub OpenChrome(sh, fso, u)
    Dim chrome, paths, p
    chrome = ""
    paths = Array( _
      sh.ExpandEnvironmentStrings("%ProgramFiles%\Google\Chrome\Application\chrome.exe"), _
      sh.ExpandEnvironmentStrings("%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"), _
      sh.ExpandEnvironmentStrings("%LocalAppData%\Google\Chrome\Application\chrome.exe"))
    For Each p In paths
        If chrome = "" Then
            If fso.FileExists(p) Then chrome = p
        End If
    Next
    If chrome <> "" Then
        sh.Run """" & chrome & """ " & u, 1, False
    Else
        sh.Run u, 1, False
    End If
End Sub
