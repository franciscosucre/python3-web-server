# Standard libs imports
import json
import posixpath
from email.message import Message
from typing import Any, Dict, List, Callable, cast, Optional
from http.server import BaseHTTPRequestHandler

from urllib.parse import parse_qs, urlsplit

class Request():
    _server: BaseHTTPRequestHandler
    command: str
    headers: Message
    path: str
    request_version: str
    query: Dict[(str, List[str])]
    params: Dict[str, Any]
    raw_body: str
    data: Dict[str, Any]

    def __init__(self: 'Request', server: BaseHTTPRequestHandler):
        self._server = server
        self.command = server.command
        self.headers = server.headers
        self.path = posixpath.normpath(server.path)
        self.request_version = server.request_version
        self.scheme, self.netloc, self.path, query, self.fragment = urlsplit(self.path)
        self.query = parse_qs(query)
        self.params = dict()
        self.data = dict()
        body_in_bytes: bytes = self._server.rfile.read(int(int(cast(str, self.headers.get('Content-Length')))))
        self.raw_body = body_in_bytes.decode('utf-8')
        hola = json.loads(self.raw_body)
        print(self.raw_body)

    


class Response():
    status_code: int = 200
    message: str = ''

    def __init__(self: 'Response', server: BaseHTTPRequestHandler, request: Request):
        self._request = request
        self._server = server

    def status(self: 'Response', status_code: int, message: Optional[str] = None) -> 'Response':
        self.status_code = status_code
        if not message:
            phrase, description = self._server.responses[status_code]
            message = phrase + ", " + description
        self.message = message
        return self

    def json(self: 'Response', data: dict) -> 'Response':
        stringData: str = json.dumps(data)
        encodedData: bytes = stringData.encode('utf-8')
        self._server.send_response(self.status_code, self.message)
        self._server.wfile.write(encodedData)
        self._server.end_headers()
        return self

Middleware = Callable[[Request, Response], None]

class Server(BaseHTTPRequestHandler):
    middlewares: List[Middleware] = list()

    def do_HEAD(self: 'Server') -> None:
        return

    def do_GET(self: 'Server') -> None:
        self.respond()

    def do_POST(self: 'Server') -> None:
        self.respond()

    def respond(self: 'Server'):
        request = Request(self)
        response = Response(self, request)
        response.status(200).json({"hello": "probando como loco"})

    def use_middleware(self: 'Server', middleware: Middleware) -> None:
        self.middlewares.append(middleware)
        return
