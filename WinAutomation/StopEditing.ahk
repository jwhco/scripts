; Close Obsidian
if WinExist("Obsidian")
	WinClose
else
	WinClose "Obsidian"
	
; Close VsCode
if WinExist("Visual Studio")
	WinClose 
else 
	WinClose "Visual Studio"
	