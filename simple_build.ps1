# Project AURA - Simple Build Script
Write-Host "Building Project AURA Release Package..." -ForegroundColor Green

# Set paths
$projectRoot = "E:\PROJECT AURA"
$releaseDir = "$projectRoot\release"

# Clean previous release
if (Test-Path $releaseDir) { 
    Remove-Item $releaseDir -Recurse -Force 
}

# Create release directory
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

# Copy built application
Copy-Item -Path "$projectRoot\dist\ProjectAURA" -Destination "$releaseDir\ProjectAURA" -Recurse

# Copy essential docs
$docs = @("README.md", "LICENCE", "ENHANCED_USER_GUIDE.md", "SAFE_ENHANCEMENT_SUCCESS.md")
foreach ($doc in $docs) {
    if (Test-Path "$projectRoot\$doc") {
        Copy-Item -Path "$projectRoot\$doc" -Destination "$releaseDir\"
    }
}

# Create ZIP
$zipName = "ProjectAURA-Release-$(Get-Date -Format 'yyyyMMdd')"
Compress-Archive -Path "$releaseDir\*" -DestinationPath "$projectRoot\$zipName.zip" -Force

Write-Host "Release created: $zipName.zip" -ForegroundColor Green
