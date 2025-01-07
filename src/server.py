#!/usr/bin/env python3

import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs, urlparse
from http import HTTPStatus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server configuration
HOST = os.getenv('HOST', 'localhost')
PORT = int(os.getenv('PORT', 8000))

class ChatRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for the chat application"""

    def __init__(self, *args, **kwargs):
        # Set the directory for serving static files
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), '..'), **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            # Serve the main page
            self.serve_file('templates/index.html')
        elif parsed_path.path == '/messages':
            # Return messages as JSON
            self.send_json_response({'messages': []})  # Placeholder for message list
        else:
            # Serve static files
            super().do_GET()

    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                if self.path == '/messages':
                    # Handle new message
                    response_data = {'status': 'success', 'message': 'Message received'}
                    self.send_json_response(response_data)
                    return
                
            except json.JSONDecodeError:
                self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON data")
                return
        
        self.send_error(HTTPStatus.BAD_REQUEST, "Invalid request")

    def serve_file(self, filepath):
        """Serve a file with appropriate content type"""
        try:
            with open(os.path.join(os.path.dirname(__file__), '..', filepath), 'rb') as f:
                content = f.read()
                self.send_response(HTTPStatus.OK)
                
                if filepath.endswith('.html'):
                    self.send_header('Content-Type', 'text/html')
                elif filepath.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript')
                elif filepath.endswith('.css'):
                    self.send_header('Content-Type', 'text/css')
                
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")

    def send_json_response(self, data, status=HTTPStatus.OK):
        """Send a JSON response with appropriate headers"""
        response = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)

def run_server():
    """Start the HTTP server"""
    handler = ChatRequestHandler
    
    with socketserver.TCPServer((HOST, PORT), handler) as httpd:
        print(f"Server running at http://{HOST}:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()

if __name__ == '__main__':
    run_server()
