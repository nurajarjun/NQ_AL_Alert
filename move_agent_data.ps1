$sourceBrain = "C:\Users\himanika\.gemini\antigravity\brain"
$destBrain = "D:\Google\.gemini\antigravity\brain"
# Exclude the current active session to prevent errors
$exclude = "f426c7b5-3e7f-4529-8127-8155cdf95a49"

$sourceRec = "C:\Users\himanika\.gemini\antigravity\browser_recordings"
$destRec = "D:\Google\.gemini\antigravity\browser_recordings"

Write-Host "Starting migration of Agent data from C: to D:..."

if (Test-Path $sourceBrain) {
    Write-Host "Moving Brain Artifacts (History)..."
    # /E = recursive, /MOVE = move files and dirs, /XD = exclude dirs, /NFL = no file list, /NDL = no directory list
    robocopy $sourceBrain $destBrain /E /MOVE /XD $exclude /NFL /NDL /NJH /NJS
} else {
    Write-Host "Source Brain directory not found or already moved."
}

if (Test-Path $sourceRec) {
    Write-Host "Moving Browser Recordings..."
    robocopy $sourceRec $destRec /E /MOVE /NFL /NDL /NJH /NJS
} else {
    Write-Host "Source Browser Recordings directory not found."
}

Write-Host "Migration operations completed."
Write-Host "Note: The current session folder ($exclude) was skipped to keep the agent active."
