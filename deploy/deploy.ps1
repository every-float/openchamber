param(
    [Parameter(Position=0)]
    [ValidateSet("deploy", "build", "start", "stop", "restart", "logs", "status", "help")]
    [string]$Command = "deploy"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

function Write-LogInfo {
    param([string]$Message)
    Write-Host "[INFO] " -ForegroundColor Blue -NoNewline
    Write-Host $Message
}

function Write-LogSuccess {
    param([string]$Message)
    Write-Host "[SUCCESS] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-LogWarning {
    param([string]$Message)
    Write-Host "[WARNING] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-LogError {
    param([string]$Message)
    Write-Host "[ERROR] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Test-Docker {
    try {
        $null = docker info 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-LogError "Docker is not running. Please start Docker Desktop."
            exit 1
        }
    }
    catch {
        Write-LogError "Docker is not installed. Please install Docker Desktop first."
        exit 1
    }

    $composeCmd = Get-DockerComposeCommand
    if (-not $composeCmd) {
        Write-LogError "Docker Compose is not available."
        exit 1
    }

    Write-LogSuccess "Docker environment check passed"
}

function Get-DockerComposeCommand {
    try {
        $null = docker compose version 2>&1
        if ($LASTEXITCODE -eq 0) {
            return "docker compose"
        }
    }
    catch {}

    try {
        $null = docker-compose --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            return "docker-compose"
        }
    }
    catch {}

    return $null
}

function Invoke-DockerCompose {
    param([string]$Arguments)
    
    $composeCmd = Get-DockerComposeCommand
    $fullCmd = "$composeCmd $Arguments"
    
    Push-Location $ProjectRoot
    try {
        Invoke-Expression $fullCmd
    }
    finally {
        Pop-Location
    }
}

function New-DeploymentDirectories {
    Write-LogInfo "Creating necessary directories..."
    
    $directories = @(
        "data/openchamber",
        "data/opencode/share",
        "data/opencode/state",
        "data/opencode/config",
        "data/ssh",
        "workspaces"
    )
    
    foreach ($dir in $directories) {
        $fullPath = Join-Path $ProjectRoot $dir
        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        }
    }
    
    Write-LogSuccess "Directories created"
}

function Build-Image {
    Write-LogInfo "Building Docker image..."
    Invoke-DockerCompose "build --no-cache"
    Write-LogSuccess "Docker image built successfully"
}

function Start-Service {
    Write-LogInfo "Starting OpenChamber service..."
    Invoke-DockerCompose "up -d"
    Write-LogSuccess "OpenChamber service started"
}

function Stop-Service {
    Write-LogInfo "Stopping OpenChamber service..."
    Invoke-DockerCompose "down"
    Write-LogSuccess "OpenChamber service stopped"
}

function Restart-Service {
    Write-LogInfo "Restarting OpenChamber service..."
    Stop-Service
    Start-Service
    Write-LogSuccess "OpenChamber service restarted"
}

function View-Logs {
    Invoke-DockerCompose "logs -f"
}

function Show-Status {
    Write-LogInfo "OpenChamber service status:"
    Invoke-DockerCompose "ps"
}

function Show-Help {
    Write-Host "OpenChamber Docker Deployment Script"
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 [command]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  deploy    - Full deployment (build and start)"
    Write-Host "  build     - Build Docker image"
    Write-Host "  start     - Start service"
    Write-Host "  stop      - Stop service"
    Write-Host "  restart   - Restart service"
    Write-Host "  logs      - View logs"
    Write-Host "  status    - Show service status"
    Write-Host "  help      - Show this help message"
    Write-Host ""
    Write-Host "Environment Variables:"
    Write-Host "  UI_PASSWORD    - Set UI authentication password"
    Write-Host "  CF_TUNNEL      - Enable Cloudflare Tunnel (true/qr/password)"
    Write-Host "  OH_MY_OPENCODE - Enable oh-my-opencode (true)"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\deploy.ps1 deploy                    # Deploy with default settings"
    Write-Host '  $env:UI_PASSWORD="mypassword"; .\deploy.ps1 deploy  # Deploy with password'
}

function Invoke-FullDeploy {
    Write-LogInfo "Starting full deployment..."
    Test-Docker
    New-DeploymentDirectories
    Build-Image
    Start-Service
    
    Write-Host ""
    Write-LogSuccess "=========================================="
    Write-LogSuccess "OpenChamber deployed successfully!"
    Write-LogSuccess "=========================================="
    Write-Host ""
    Write-LogInfo "Access OpenChamber at: http://localhost:3000"
    Write-Host ""
    Write-LogInfo "Useful commands:"
    Write-Host "  View logs:     .\deploy.ps1 logs"
    Write-Host "  Stop service:  .\deploy.ps1 stop"
    Write-Host "  Restart:       .\deploy.ps1 restart"
    Write-Host "  Status:        .\deploy.ps1 status"
    Write-Host ""
}

switch ($Command) {
    "deploy" {
        Invoke-FullDeploy
    }
    "build" {
        Test-Docker
        Build-Image
    }
    "start" {
        Test-Docker
        New-DeploymentDirectories
        Start-Service
    }
    "stop" {
        Stop-Service
    }
    "restart" {
        Restart-Service
    }
    "logs" {
        View-Logs
    }
    "status" {
        Show-Status
    }
    "help" {
        Show-Help
    }
}
