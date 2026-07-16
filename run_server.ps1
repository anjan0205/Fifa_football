# FIFA World Cup AI Command Center - Native PowerShell Web Server
# Serves the static high-fidelity SPA on http://localhost:8080

$port = 8080
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")

try {
    $listener.Start()
    Write-Host "=============================================" -ForegroundColor Green
    Write-Host "FIFA World Cup AI Command Center Server Online" -ForegroundColor Green
    Write-Host "Server running at: http://localhost:$port/" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C in this terminal to stop the server" -ForegroundColor Yellow
    Write-Host "=============================================" -ForegroundColor Green
    
    $rootFolder = Join-Path $PSScriptRoot "frontend"

    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response
        
        $urlPath = $request.Url.LocalPath
        # Default routing to index.html
        if ($urlPath -eq "/" -or [string]::IsNullOrEmpty($urlPath)) {
            $urlPath = "/index.html"
        }
        
        # Resolve target file path
        $cleanPath = $urlPath.TrimStart('/')
        $filePath = Join-Path $rootFolder $cleanPath
        
        if (Test-Path $filePath -PathType Leaf) {
            # Read file bytes
            $bytes = [System.IO.File]::ReadAllBytes($filePath)
            
            # Identify MIME content types
            if ($filePath.EndsWith(".html")) {
                $response.ContentType = "text/html; charset=utf-8"
            } elseif ($filePath.EndsWith(".css")) {
                $response.ContentType = "text/css; charset=utf-8"
            } elseif ($filePath.EndsWith(".js")) {
                $response.ContentType = "text/javascript; charset=utf-8"
            } elseif ($filePath.EndsWith(".png")) {
                $response.ContentType = "image/png"
            } elseif ($filePath.EndsWith(".jpg") -or $filePath.EndsWith(".jpeg")) {
                $response.ContentType = "image/jpeg"
            }
            
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        } else {
            # File Not Found response
            $response.StatusCode = 404
            $errBytes = [System.Text.Encoding]::UTF8.GetBytes("404 - File Not Found: $urlPath")
            $response.ContentLength64 = $errBytes.Length
            $response.OutputStream.Write($errBytes, 0, $errBytes.Length)
        }
        $response.OutputStream.Close()
    }
} catch {
    Write-Host "Error starting web server: $_" -ForegroundColor Red
} finally {
    if ($listener) {
        $listener.Close()
    }
}
