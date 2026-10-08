$ErrorActionPreference = "Stop"

$PT = $false
try { $PT = ((Get-UICulture).Name -like "pt*") -or ((Get-Culture).Name -like "pt*") } catch { $PT = $false }

function M($pt, $en) {
  if ($PT) { Write-Host $pt } else { Write-Host $en }
}

function Versao($Cmd, $Pre) {
  try {
    $saida = & $Cmd @Pre --version 2>&1 | Out-String
    return $saida
  } catch {
    return ""
  }
}

function Mesclar($De, $Para) {
  New-Item -ItemType Directory -Force -Path $Para | Out-Null
  Get-ChildItem -LiteralPath $De -Force | ForEach-Object {
    $alvo = Join-Path $Para $_.Name
    if ($_.PSIsContainer) { Mesclar $_.FullName $alvo } else { Copy-Item -LiteralPath $_.FullName -Destination $alvo -Force }
  }
}

$Origem = "$env:DECK".TrimEnd("/")
if (-not $Origem) {
  M 'Uso: $env:DECK="ENDERECO-DO-SITE"; irm ENDERECO-DO-SITE/instalar-windows.ps1 | iex' 'Usage: $env:DECK="SITE-ADDRESS"; irm SITE-ADDRESS/instalar-windows.ps1 | iex'
  return
}

$Exe = $null
$Pre = @()
if ((Versao "py" @("-3")) -match "Python 3") { $Exe = "py"; $Pre = @("-3") }
elseif ((Versao "python" @()) -match "Python 3") { $Exe = "python" }
elseif ((Versao "python3" @()) -match "Python 3") { $Exe = "python3" }
if (-not $Exe) {
  M "Falta o Python 3. Instale pelo python.org (marque 'Add python.exe to PATH' no instalador) e rode este comando de novo." "Python 3 is missing. Install it from python.org (check 'Add python.exe to PATH' in the installer) and run this command again."
  Start-Process "https://www.python.org/downloads/"
  return
}

$Destino = Join-Path $env:USERPROFILE "Deck"
$Tmp = Join-Path $env:TEMP ("deck-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $Tmp | Out-Null
M "Baixando o Deck…" "Downloading Deck…"
Invoke-WebRequest "$Origem/deck.zip" -OutFile (Join-Path $Tmp "deck.zip")
Expand-Archive -Path (Join-Path $Tmp "deck.zip") -DestinationPath (Join-Path $Tmp "novo") -Force
$Novo = Join-Path $Tmp "novo\deck"
if (-not (Test-Path (Join-Path $Novo "server.py"))) {
  M "O arquivo baixado não parece ser o Deck." "The downloaded file doesn't look like Deck."
  return
}
if (Test-Path (Join-Path $Destino "server.py")) {
  M "Atualizando o Deck em $Destino (seus botões e ícones ficam)…" "Updating Deck in $Destino (your buttons and icons stay)…"
  if (Test-Path (Join-Path $Destino "config.json")) { Remove-Item (Join-Path $Novo "config.json") }
} else {
  M "Instalando o Deck em $Destino…" "Installing Deck in $Destino…"
}
Mesclar $Novo $Destino
Remove-Item -Recurse -Force $Tmp
Get-ChildItem -Recurse $Destino | Unblock-File -ErrorAction SilentlyContinue
M "Pronto: $Destino" "Done: $Destino"
M "Da próxima vez, dê duplo clique em 'Iniciar no Windows.bat' dentro da pasta Deck." "Next time, double-click 'Iniciar no Windows.bat' inside the Deck folder."
M "Ligando o deck…" "Starting the deck…"
Set-Location $Destino
& $Exe @Pre server.py
