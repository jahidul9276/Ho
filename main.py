#!/usr/bin/env python3
"""
Simple Python web server that shows IP and connection info
"""

import socket
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

class InfoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL
        parsed_path = urlparse(self.path)
        
        # Get client IP address
        client_ip = self.client_address[0]
        
        # Get server IP
        server_ip = socket.gethostbyname(socket.gethostname())
        
        # Determine if local or remote
        is_local = client_ip in ['127.0.0.1', 'localhost', '::1'] or client_ip.startswith('192.168.') or client_ip.startswith('10.')
        
        # Create HTML response
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VPS Connection Info</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; }}
        .info-box {{
            background: #e8f4fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 20px 0;
        }}
        .local {{ border-left-color: #4CAF50; }}
        .remote {{ border-left-color: #FF9800; }}
        .label {{ font-weight: bold; color: #555; }}
        .value {{ color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 VPS Connection Information</h1>
        
        <div class="info-box {'local' if is_local else 'remote'}">
            <h2>{'📍 Local Access' if is_local else '🌍 Remote Access'}</h2>
            <p>You are accessing this server {'from within the VPS/local network' if is_local else 'remotely'}.</p>
        </div>
        
        <table>
            <tr>
                <td class="label">Your IP Address:</td>
                <td class="value">{client_ip}</td>
            </tr>
            <tr>
                <td class="label">Server IP:</td>
                <td class="value">{server_ip}</td>
            </tr>
            <tr>
                <td class="label">Server Port:</td>
                <td class="value">{self.server.server_port}</td>
            </tr>
            <tr>
                <td class="label">Request Path:</td>
                <td class="value">{self.path}</td>
            </tr>
            <tr>
                <td class="label">Connection Type:</td>
                <td class="value">{'Local' if is_local else 'Remote'}</td>
            </tr>
        </table>
        
        <h3>Quick Links:</h3>
        <p>
            <a href="/">Home</a> | 
            <a href="/json">JSON Data</a> | 
            <a href="/network">Network Info</a>
        </p>
        
        <div style="margin-top: 30px; padding: 15px; background: #f9f9f9; border-radius: 5px;">
            <small>
                <strong>Note:</strong> To access this from internet, ensure:<br>
                1. VPS firewall allows port {self.server.server_port}<br>
                2. Port is forwarded if behind NAT<br>
                3. Use your VPS public IP: <code>{server_ip}</code>
            </small>
        </div>
    </div>
</body>
</html>"""
        
        # JSON endpoint
        if parsed_path.path == '/json':
            data = {
                "client_ip": client_ip,
                "server_ip": server_ip,
                "server_port": self.server.server_port,
                "is_local": is_local,
                "path": self.path
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2).encode())
            return
        
        # Network info endpoint
        elif parsed_path.path == '/network':
            try:
                # Get public IP (requires internet)
                import urllib.request
                public_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf-8')
            except:
                public_ip = "Unable to determine"
            
            network_html = f"""<!DOCTYPE html>
<html>
<head><title>Network Info</title></head>
<body>
    <h1>Network Information</h1>
    <p><strong>Server Hostname:</strong> {socket.gethostname()}</p>
    <p><strong>Public IP:</strong> {public_ip}</p>
    <p><strong>Local IP:</strong> {server_ip}</p>
    <a href="/">Back to Home</a>
</body>
</html>"""
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(network_html.encode())
            return
        
        # Default HTML response
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        # Custom logging to show IP addresses
        client_ip = self.client_address[0]
        print(f"{client_ip} - - [{self.log_date_time_string()}] {format % args}")

def run_server(port=8080):
    """Start the web server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, InfoHandler)
    
    print(f"""
╔══════════════════════════════════════════╗
║    Simple VPS Info Server Running!       ║
╠══════════════════════════════════════════╣
║ Local:  http://localhost:{port}          ║
║ Local:  http://127.0.0.1:{port}          ║
║ Network: http://<your-ip>:{port}         ║
║                                          ║
║ Press Ctrl+C to stop the server          ║
╚══════════════════════════════════════════╝
    """)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == '__main__':
    # Get port from command line or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
