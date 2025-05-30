;
; Start Editing Environment
;

; Close Fathom
; ----
try {
    ProcessName := "Fathom.exe"
    if ProcessExist(ProcessName) {
        ProcessClose(ProcessName)
        ; Wait up to 5 seconds for Fathom to close
        Loop 50 {
            if !ProcessExist(ProcessName)
                break
            Sleep 100
        }
    }
} catch {
    MsgBox "Fathom, Failed to Close"
}


; Open VsCode
; ----
try
    RunWait '"C:\Users\User\AppData\Local\Programs\Microsoft VS Code\Code.exe" "C:\Users\User\GitHub\obsidian"', , "Min"
catch
    MsgBox "VsCode, Failed to Start"

; Open Obsidian
; ----
try
    RunWait '"C:\Users\User\AppData\Local\Obsidian\Obsidian.exe" "C:\Users\User\GitHub\obsidian"', , "Min"
catch
    MsgBox "Obsidian, Failed to Start"

Exit

;;;
