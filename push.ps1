# push.ps1 - first push of the project to GitHub
# Run:  powershell -ExecutionPolicy Bypass -File .\push.ps1
# Uses your already configured GitHub credentials (Git Credential Manager).

$ErrorActionPreference = 'Stop'
$repo = 'https://github.com/Yuri-Sverdlov/COMFYUI-STORY-ILLUSTRATOR.git'
Set-Location -Path $PSScriptRoot

Write-Host '== 1. Remove stale index.lock (if any) ==' -ForegroundColor Cyan
$lock = Join-Path $PSScriptRoot '.git\index.lock'
if (Test-Path $lock) { Remove-Item $lock -Force; Write-Host '   removed' } else { Write-Host '   none' }

Write-Host '== 2. Check git identity ==' -ForegroundColor Cyan
if (-not (git config user.name))  { git config user.name  'Yuri-Sverdlov' }
if (-not (git config user.email)) { git config user.email 'yurispp@gmail.com' }
Write-Host ('   {0} / {1}' -f (git config user.name), (git config user.email))

Write-Host '== 3. Branch main ==' -ForegroundColor Cyan
git branch -M main

Write-Host '== 4. Stage and commit ==' -ForegroundColor Cyan
git add -A
if (git status --porcelain) {
    git commit -m 'Initial commit: COMFYUI-STORY-ILLUSTRATOR project'
} else {
    Write-Host '   nothing to commit'
}

Write-Host '== 5. Remote origin ==' -ForegroundColor Cyan
if (git remote | Select-String -Quiet '^origin$') {
    git remote set-url origin $repo
} else {
    git remote add origin $repo
}
git remote -v

Write-Host '== 6. Push ==' -ForegroundColor Cyan
git push -u origin main

Write-Host ''
Write-Host 'Done. Open: https://github.com/Yuri-Sverdlov/COMFYUI-STORY-ILLUSTRATOR' -ForegroundColor Green
