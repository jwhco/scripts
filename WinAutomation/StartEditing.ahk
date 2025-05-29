; Close Fathom

; Open VsCode
try 
	RunWait "C:\Users\User\AppData\Local\Programs\Microsoft VS Code\Code.exe",, "Min"
catch
	MsgBox "VsCode, Failed to Start"



; Open Obsidian
try
	RunWait "C:\Users\User\AppData\Local\Obsidian\Obsidian.exe",, "Min"
catch
	MsgBox "Obsidian, Failed to Start"



