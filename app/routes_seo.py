from urllib.parse import urlparse
from flask import Blueprint, render_template, request, Response
from app.routes_auth import login_required, app_access_required

seo_bp = Blueprint('seo', __name__, url_prefix='/seo')
seo_api_bp = Blueprint('seo_api', __name__, url_prefix='/seo/api')

FETCH_TIMEOUT = 15
FETCH_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def _is_safe_url(url):
    """Allow only http/https with a public hostname."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False
        host = parsed.hostname or ''
        # Block private/loopback ranges
        private = ('localhost', '127.', '10.', '192.168.', '172.16.',
                   '172.17.', '172.18.', '172.19.', '172.20.', '172.21.',
                   '172.22.', '172.23.', '172.24.', '172.25.', '172.26.',
                   '172.27.', '172.28.', '172.29.', '172.30.', '172.31.',
                   '0.0.0.0', '::1', 'metadata.google.internal')
        if any(host == p or host.startswith(p) for p in private):
            return False
        return True
    except Exception:
        return False


# ─── Pages ────────────────────────────────────────────────────────────

@seo_bp.route('/')
@login_required
@app_access_required('seo')
def index():
    return render_template('seo/index.html')


# ─── API ──────────────────────────────────────────────────────────────

@seo_api_bp.route('/proxy')
@login_required
@app_access_required('seo')
def proxy():
    url = request.args.get('url', '').strip()

    if not url:
        return Response('Missing url parameter', status=400)

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    if not _is_safe_url(url):
        return Response('URL not allowed', status=403)

    try:
        import requests
        resp = requests.get(
            url,
            headers=FETCH_HEADERS,
            timeout=FETCH_TIMEOUT,
            allow_redirects=True,
        )
        content_type = resp.headers.get('Content-Type', 'text/html; charset=utf-8')
        # Always return 200 so the JS can parse the HTML regardless of target status.
        # Include the real target status in a header for reference.
        proxy_resp = Response(resp.content, status=200, content_type=content_type)
        proxy_resp.headers['X-Target-Status'] = str(resp.status_code)
        return proxy_resp

    except requests.exceptions.Timeout:
        return Response('Timed out after 15 s', status=504)
    except requests.exceptions.TooManyRedirects:
        return Response('Too many redirects', status=502)
    except requests.exceptions.ConnectionError as e:
        msg = str(e)
        if 'Name or service not known' in msg or 'nodename nor servname' in msg:
            return Response('Domain not found (DNS error)', status=502)
        return Response(f'Connection error: {msg[:120]}', status=502)
    except requests.exceptions.RequestException as e:
        return Response(f'Fetch error: {str(e)[:120]}', status=502)
