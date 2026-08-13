#!/usr/bin/env python3
import http.server
import socketserver
import os
import socket

PORT = 8000

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "localhost"
    finally:
        s.close()

os.chdir("generated")

with socketserver.TCPServer(("0.0.0.0", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print(f"On your phone: http://{get_lan_ip()}:{PORT}")
    httpd.serve_forever()
