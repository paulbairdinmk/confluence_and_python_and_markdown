Get-ChildItem -File -Recurse | ForEach-Object {
    $newName = $_.Name -replace '\[|\]', ''

    if ($newName -ne $_.Name) {
        Rename-Item -LiteralPath $_.FullName -NewName $newName
        Write-Host "Renamed: $($_.FullName) -> $newName"
    }
}