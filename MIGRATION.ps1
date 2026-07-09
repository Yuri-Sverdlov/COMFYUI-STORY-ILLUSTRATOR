<#
  Finalize split: COMFYUI-API-CHAT -> COMFYUI-STORY-ILLUSTRATOR
  Run on computer 2 (Windows). ASCII-only (PowerShell 5.x reads .ps1 as cp1252).
  Sections 1-3 are safe. Section 4 (cleanup of old repo) is optional.
#>

$Base = "G:\AI\_MY_PROGRAMMING_2"
$Src  = Join-Path $Base "COMFYUI-API-CHAT"
$Dst  = Join-Path $Base "COMFYUI-STORY-ILLUSTRATOR"
Set-Location $Base

# -- 1. Remove stray old workflows copied by mistake (cyberpunk/nsfw) ----------
if (Test-Path "$Dst\workflows") {
  Remove-Item "$Dst\workflows" -Recurse -Force
  Write-Host "removed stray workflows/"
}

# -- 2. Move heavy illustration galleries (~250 MB) into the new project -------
$galleries = @(
  "ancient_greece","character_sheets","dreamshaper_xl_lightning",
  "sd_xl_base_1_0","realismIllustriousBy_v50FP16",
  "realism_test","realism_test_2","greece_test_01","ipadapter_test"
)
foreach ($g in $galleries) {
  $from = Join-Path "$Src\sessions" $g
  if (Test-Path $from) {
    Move-Item $from "$Dst\sessions\" -Force
    Write-Host "moved $g"
  }
}
# Note: old chat sessions (2026-03-30_152515, *_test, *_runpod) and 'current'
# stay in COMFYUI-API-CHAT - they belong to the web app.

# -- 3. Init git in the new project and make the first commit ------------------
Set-Location $Dst
git init
git add .
git commit -m "init: COMFYUI-STORY-ILLUSTRATOR (split from COMFYUI-API-CHAT)"
git status

# -- 4. (OPTIONAL) Remove from the OLD repo the files that moved to the new one -
#    Uncomment only if sure. Everything stays in the old repo's git history.
<#
Set-Location $Src
git rm -r --cached scripts KNOWLEDGE_BASE.md SCENE_PARAMS_01.md
git rm -r --cached sessions/ancient_greece sessions/character_sheets `
  sessions/dreamshaper_xl_lightning sessions/sd_xl_base_1_0 `
  sessions/realismIllustriousBy_v50FP16 sessions/realism_test `
  sessions/realism_test_2 sessions/greece_test_01 sessions/ipadapter_test
Remove-Item "$Src\scripts" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$Src\KNOWLEDGE_BASE.md","$Src\SCENE_PARAMS_01.md" -Force -ErrorAction SilentlyContinue
git commit -m "chore: move illustration pipeline into a separate project"
#>

Write-Host ""
Write-Host "Done. Check COMFYUI-STORY-ILLUSTRATOR." -ForegroundColor Green
