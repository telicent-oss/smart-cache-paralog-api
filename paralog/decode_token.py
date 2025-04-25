import logging

import jwt
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
from jwt import PyJWKClient

__license__ = """
Copyright (c) Telicent Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


class AccessMiddleware:
    """
    Simple middleware to validate and decode tokens
    """
    def __init__(self, app, jwt_header: str, jwks_url: str = None, public_key_url: str = None):
        self.app = app
        self.jwks_url = jwks_url
        self.public_key_url = public_key_url
        if self.public_key_url is not None:
            self.public_key_url = self.public_key_url.strip("/")

        self.jwt_header = jwt_header
        self.logger = logging.getLogger(__name__)

        if not self.jwks_url and not self.public_key_url:
            self.logger.warning(
                "Both JWK_URL and PUBLIC_KEY_URL are missing, starting paralog without auth",
                extra={'method': 'STARTUP', 'type': 'GENERAL'}
            )
            self.run_auth = False
        elif (self.jwks_url or self.public_key_url) and self.jwt_header:
            self.logger.debug(
                f"Configuring auth with using header {self.jwt_header}",
                extra={'method': 'STARTUP', 'type': 'GENERAL'}
            )
            if self.jwks_url and not self.public_key_url:
                self.logger.warning(
                    "Both JWK_URL and PUBLIC_KEY_URL passed, JWK_URL takes preference",
                    extra={'method': 'STARTUP', 'type': 'GENERAL'}
                )
            if self.jwks_url:
                self.logger.debug(
                    f"Auth configured with jwks endpoint {self.jwks_url}",
                    extra={'method': 'STARTUP', 'type': 'GENERAL'}
                )
            if self.public_key_url:
                self.logger.debug(
                    f"Auth configured with load-balancer public key endpoint {self.public_key_url}",
                    extra={'method': 'STARTUP', 'type': 'GENERAL'}
                )
            self.run_auth = True
        else:
            self.logger.warning(
                "JWT_HEADER is missing, starting paralog without auth",
                extra={'method': 'STARTUP', 'type': 'GENERAL'}
            )
            self.run_auth = False

    async def __call__(self, request: Request, call_next):
        if self.run_auth:
            if self.jwt_header not in request.headers:
                self.logger.info(
                    f'Unauthorized access: No required header: {self.jwt_header}',
                    extra={'method': 'Authenticator', 'type': 'UNAUTHORIZED'}
                )
                return JSONResponse(content={"message": f"missing auth header: {self.jwt_header}"}, status_code=400)

            encoded = request.headers[self.jwt_header]
            try:
                token = await self.validate_token(encoded)
                if token is None:
                    self.logger.info(
                        "Unauthorized access: token not valid",
                        extra={'method': 'Authenticator', 'type': 'UNAUTHORIZED'}
                    )
                    return JSONResponse(content={"message": "unauthorised, invalid token"}, status_code=401)
            except (jwt.exceptions.InvalidTokenError, jwt.exceptions.PyJWKClientError):
                return JSONResponse(content={"message": "unauthorised, invalid token"}, status_code=401)

        response = await call_next(request)
        return response

    async def validate_token(self, token):
        try:
            headers = jwt.get_unverified_header(token)
            if self.jwks_url is not None:
                self.logger.debug(
                    "Validating token with jwks_url",
                    extra={'method': 'Authenticator', 'type': 'GENERAL'}
                )
                jwks_client = PyJWKClient(self.jwks_url)
                signing_key = jwks_client.get_signing_key_from_jwt(token)
                key = signing_key.key
            elif self.public_key_url is not None:
                self.logger.debug(
                    "Validating token with elb public key",
                    extra={'method': 'Authenticator', 'type': 'GENERAL'}
                )
                public_key_ep = "{}{}".format(self.public_key_url, headers['kid'])
                req = requests.get(public_key_ep)
                key = req.text
            else:
                raise RuntimeError("Token decoding requires either a jwks_url or public_key_url")
            data = jwt.decode(token, key, algorithms=[headers['alg']])
        except Exception as e:
            self.logger.error(
                f'Exception validating token: {str(e)}',
                extra={'method': 'Authenticator', 'type': 'UNAUTHORIZED'}
            )
            raise
        return data
