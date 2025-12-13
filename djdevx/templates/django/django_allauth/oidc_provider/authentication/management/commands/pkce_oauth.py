import base64
import hashlib
import json
import secrets
import string
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Annotated

import typer
from django_typer.management import TyperCommand


# === PKCE helpers ===
def generate_code_verifier():
    verifier = "".join(
        secrets.choice(string.ascii_letters + string.digits + "-._~") for _ in range(64)
    )
    return verifier


def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return challenge


# === Simple web server to capture the callback ===
class OAuthCallbackHandler(BaseHTTPRequestHandler):
    server_version = "OAuthCallbackHandler/1.0"

    def do_GET(self):
        if self.path.startswith("/callback"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            self.server.auth_code = params.get("code", [None])[0]  # type: ignore

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>You can close this window now.</h1>")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging
        pass


def run_server(callback_host: str, callback_port: int):
    server = HTTPServer((callback_host, callback_port), OAuthCallbackHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


class Command(TyperCommand):
    """
    Test PKCE OAuth flow with authorization server
    """

    def handle(
        self,
        authorization_url: Annotated[
            str, typer.Option(help="Authorization endpoint URL", prompt=True)
        ] = "http://localhost:8000/auth/identity/o/authorize",
        token_url: Annotated[
            str, typer.Option(help="Token endpoint URL", prompt=True)
        ] = "http://localhost:8000/auth/identity/o/api/token",
        client_id: Annotated[
            str, typer.Option(help="OAuth client ID", prompt=True)
        ] = "",
        userinfo_url: Annotated[
            str, typer.Option(help="UserInfo endpoint URL", prompt=True)
        ] = "http://localhost:8000/auth/identity/o/api/userinfo",
        scope: Annotated[
            str, typer.Option(help="OAuth scopes", prompt=True)
        ] = "openid profile email",
        callback_host: Annotated[
            str, typer.Option(help="Host for callback server", prompt=True)
        ] = "localhost",
        callback_port: Annotated[
            int, typer.Option(help="Port for callback server", prompt=True)
        ] = 8080,
        redirect_uri: Annotated[
            str, typer.Option(help="Redirect URI for callback", prompt=True)
        ] = "http://localhost:8080/callback",
    ):
        """
        Test PKCE OAuth flow
        """
        code_verifier = generate_code_verifier()
        code_challenge = generate_code_challenge(code_verifier)

        # Start local HTTP server
        server = run_server(callback_host, callback_port)

        try:
            # Build authorization URL
            params = {
                "client_id": client_id,
                "response_type": "code",
                "redirect_uri": redirect_uri,
                "scope": scope,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            }
            auth_url = f"{authorization_url}?{urllib.parse.urlencode(params)}"

            typer.echo("Opening browser for authorization...")
            webbrowser.open(auth_url)

            # Wait until we receive the code (2 second timeout)
            typer.echo("Waiting for the authorization code...")
            start_time = time.time()
            timeout = 2
            while not hasattr(server, "auth_code"):
                if time.time() - start_time > timeout:
                    raise RuntimeError(
                        f"No callback received within {timeout} seconds. "
                        "Check authorization URL and client ID."
                    )
                time.sleep(0.1)

            auth_code = server.auth_code  # type: ignore
            if not auth_code:
                raise RuntimeError("Failed to receive authorization code")

            typer.echo(f"Received authorization code: {auth_code}")

            # Exchange the authorization code for tokens
            token_data = {
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": redirect_uri,
                "client_id": client_id,
                "code_verifier": code_verifier,
            }
            encoded_data = urllib.parse.urlencode(token_data).encode("utf-8")
            request = urllib.request.Request(token_url, data=encoded_data)
            try:
                with urllib.request.urlopen(request) as response:
                    tokens = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as e:  # type: ignore
                error_msg = e.read().decode("utf-8")
                raise RuntimeError(f"Token request failed: {error_msg}")

            access_token = tokens.get("access_token")
            if not access_token:
                raise RuntimeError("No access_token returned!")

            typer.echo(f"\nAccess Token: {access_token}")

            # === Use the access token to call the UserInfo endpoint ===
            request = urllib.request.Request(userinfo_url)
            request.add_header("Authorization", f"Bearer {access_token}")
            request.add_header("Accept", "application/json")
            try:
                with urllib.request.urlopen(request) as response:
                    userinfo = json.loads(response.read().decode("utf-8"))
                    typer.echo("\nUser Info:")
                    typer.echo(userinfo)
            except urllib.error.HTTPError as e:  # type: ignore
                error_msg = e.read().decode("utf-8")
                raise RuntimeError(f"UserInfo request failed: {error_msg}")
        finally:
            try:
                server.shutdown()
            except Exception:
                pass
