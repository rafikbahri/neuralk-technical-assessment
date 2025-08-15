"""
Proxy used to redirect and rewrite HTTP requests made by the client to the target Minio container
when using the pre-signed URLs
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import config

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def do_PUT(self):
        self.proxy_request()
    
    def do_DELETE(self):
        self.proxy_request()
    
    def proxy_request(self):
        # Build target URL
        target_url = f"http://{config.MINIO_HOST}{self.path}"
        
        try:
            # Create request
            req = urllib.request.Request(target_url, method=self.command)
            
            # Copy headers
            for header, value in self.headers.items():
                if header.lower() != 'host':
                    req.add_header(header, value)
            
            # Copy body for POST/PUT requests
            if self.command in ['POST', 'PUT']:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    req.data = self.rfile.read(content_length)
            
            # Make request
            with urllib.request.urlopen(req) as response:
                # Send response
                self.send_response(response.getcode())
                
                # Copy response headers
                for header, value in response.headers.items():
                    self.send_header(header, value)
                self.end_headers()
                
                # Copy response body
                self.wfile.write(response.read())
                
        except Exception as e:
            self.send_error(500, f"Proxy error: {str(e)}")

if __name__ == '__main__':
    server = HTTPServer((config.MINIO_PROXY_ADDRESS, config.MINIO_PROXY_PORT), ProxyHandler)
    print(f"Proxy server running on http://{config.MINIO_PROXY_ADDRESS}:{config.MINIO_PROXY_PORT}")
    print(f"Forwarding to http://{config.MINIO_HOST}")
    server.serve_forever()