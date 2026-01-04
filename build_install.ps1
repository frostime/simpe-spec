rm dist
uv build
# find whl file in dist folder
$whl = Get-ChildItem -Path dist -Filter *.whl | Select-Object -First 1
pipx install $whl --force
