# Installs the global Claude Code kit into your user folder (C:\Users\<you>\.claude).
#
# Run it from the feature-lab folder:
#   powershell -ExecutionPolicy Bypass -File claude-global\install.ps1
#
# Safe to run again after you change the kit:
#   - everything it touches is backed up first to ~\.claude\backups\global-kit-<date>\
#   - CLAUDE.md: only the part between the "global-kit" marker lines is replaced; your own text stays
#   - settings.json: our rules are ADDED to yours; nothing of yours is removed
#   - skills: our skill folders are replaced with the latest version

$ErrorActionPreference = "Stop"

$kit    = $PSScriptRoot                    # this claude-global folder
$repo   = Split-Path $kit -Parent          # the feature-lab folder (it holds the video engine)
$dest   = Join-Path $HOME ".claude"
$stamp  = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = Join-Path $dest "backups\global-kit-$stamp"
New-Item -ItemType Directory -Force -Path $dest, $backup, (Join-Path $backup "skills") | Out-Null

# Write text as UTF-8 *without* a BOM (an invisible mark Windows PowerShell adds by default,
# which can stop settings.json from loading).
function Write-Utf8($path, $text) {
    [System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding $false))
}

# Add a property to a JSON object, or change it if it already exists.
function Set-Prop($obj, $name, $value) {
    if ($obj.PSObject.Properties[$name]) { $obj.$name = $value }
    else { $obj | Add-Member -NotePropertyName $name -NotePropertyValue $value }
}

# ---------------------------------------------------------------- 1. CLAUDE.md
$start  = "<!-- global-kit:start -->"
$end    = "<!-- global-kit:end -->"
$ours   = "$start`n" + (Get-Content (Join-Path $kit "CLAUDE.md") -Raw).Trim() + "`n$end"
$target = Join-Path $dest "CLAUDE.md"
if (Test-Path $target) {
    Copy-Item $target $backup
    $old = Get-Content $target -Raw
    if ($old -and $old.Contains($start)) {
        # Replace only our old block.
        $pattern = [regex]::Escape($start) + "[\s\S]*?" + [regex]::Escape($end)
        $new = [regex]::Replace($old, $pattern, [System.Text.RegularExpressions.MatchEvaluator] { param($m) $ours })
    } else {
        # Keep your text and add ours at the end.
        $new = ("$old".TrimEnd() + "`n`n" + $ours).TrimStart()
    }
} else {
    $new = $ours
}
Write-Utf8 $target ($new + "`n")
Write-Host "CLAUDE.md      -> $target"

# ---------------------------------------------------------------- 2. settings.json
$settingsPath = Join-Path $dest "settings.json"
$kitSettings  = Get-Content (Join-Path $kit "settings.json") -Raw | ConvertFrom-Json
$current = $null
if (Test-Path $settingsPath) {
    Copy-Item $settingsPath $backup
    $raw = Get-Content $settingsPath -Raw
    if ($raw -and $raw.Trim()) {
        try { $current = $raw | ConvertFrom-Json }
        catch { throw "Your $settingsPath is not valid JSON, so I didn't touch it. Fix it (or delete it) and run again." }
    }
}
if (-not $current) { $current = [pscustomobject]@{} }
if (-not $current.PSObject.Properties["permissions"]) { Set-Prop $current "permissions" ([pscustomobject]@{}) }

foreach ($list in "allow", "ask", "deny") {
    $yours = @()
    if ($current.permissions.PSObject.Properties[$list]) { $yours = @($current.permissions.$list) }
    $merged = @(@($yours) + @($kitSettings.permissions.$list) | Where-Object { $_ } | Select-Object -Unique)
    Set-Prop $current.permissions $list $merged
}
# Commit/PR attribution: only set it if you haven't chosen something yourself.
if (-not $current.PSObject.Properties["attribution"]) { Set-Prop $current "attribution" $kitSettings.attribution }

Write-Utf8 $settingsPath (($current | ConvertTo-Json -Depth 20) + "`n")
Write-Host "settings.json  -> $settingsPath"

# ---------------------------------------------------------------- 3. skills
$skillsDest = Join-Path $dest "skills"
New-Item -ItemType Directory -Force -Path $skillsDest | Out-Null
Get-ChildItem (Join-Path $kit "skills") -Directory | ForEach-Object {
    $to = Join-Path $skillsDest $_.Name
    if (Test-Path $to) {
        Copy-Item $to (Join-Path $backup "skills\$($_.Name)") -Recurse
        Remove-Item $to -Recurse -Force
    }
    Copy-Item $_.FullName $to -Recurse
    Write-Host "skill          -> $to"
}

# The stickman-video skill carries a copy of this repo's video engine, so other projects can use it.
$template = Join-Path $skillsDest "stickman-video\template"
$video    = Join-Path $repo "video"
New-Item -ItemType Directory -Force -Path (Join-Path $template "assets") | Out-Null
foreach ($f in "draw.js", "make_video.py", "stage.html", "requirements.txt") {
    Copy-Item (Join-Path $video $f) $template
}
Copy-Item (Join-Path $video "assets\*") (Join-Path $template "assets")
Copy-Item (Join-Path $video "scenes.js") (Join-Path $template "scenes.example.js")
Write-Host "video engine   -> $template"

Write-Host ""
Write-Host "Done. Backup of your previous files: $backup"
Write-Host "Restart Claude Code (or open a new session) to load the changes."
