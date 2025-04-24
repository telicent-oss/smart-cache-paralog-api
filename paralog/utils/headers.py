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


async def get_headers(headers):
    pass_through_headers = [
        'x-amzn-oidc-data',
        'x-amzn-oidc-identity',
        'x-amzn-oidc-accesstoken'
    ]

    forward_headers = {}
    for h in pass_through_headers:
        hv = headers.get(h)
        if hv is not None:
            forward_headers[h] = hv
    return forward_headers
