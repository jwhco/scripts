#
# Use PowerShell to convert `.doc` to `.docx`
#

# Purpose: Convert all `.doc` in directory to `.docx` using Microsoft Word via PowerShell. Feed script a fully qualified path. Converted file should be in the same directory as the original.
# Platform: Windows
# Author: Justin Hitt
# Usage: Run from anywhere, feed fully qualified directory containing `.doc` files. Must open PowerShell first. Will recurse directories.
#
#   Doc2Docx.ps1 c:\fully\qualified\path\
#
#   powershell.exe -File "C:\path\to\script\Doc2Docx.ps1" "C:\fully\qualified\path\"
#

# Read Command Line Arguments
param (
    [string]$path
)

# Determine if Valid Path
Test-Path -Path $path -IsValid

$word_app = New-Object -ComObject Word.Application

$Format = [Microsoft.Office.Interop.Word.WdSaveFormat]::wdFormatXMLDocument

Get-ChildItem -Path $path -Filter *.doc -Recurse | ForEach-Object {
    $document = $word_app.Documents.Open($_.FullName)
    $docx_filename = "$($_.DirectoryName)\$($_.BaseName).docx"
    $document.SaveAs([ref] $docx_filename, [ref]$Format)
    $document.Close()
}
$word_app.Quit()
