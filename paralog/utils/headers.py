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
