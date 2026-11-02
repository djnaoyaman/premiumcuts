"""Pure pre-request policy for social preview rendering; no network operations."""
from urllib.parse import urlsplit

YOUTUBE_FAMILY_HOSTS = (
    'youtube.com', 'youtu.be', 'youtube-nocookie.com', 'ytimg.com',
    'googlevideo.com', 'youtube.googleapis.com', 'youtubei.googleapis.com',
    'ggpht.com', 'yt3.googleusercontent.com', 'youtube-ui.l.google.com',
    'youtubeeducation.com', 'youtubekids.com',
)

def youtube_family_request(url):
    """Block provider pages, embeds, thumbnails, media, API and avatar hosts."""
    try:
        hostname = (urlsplit(url).hostname or '').lower().rstrip('.')
    except (ValueError, TypeError):
        return True  # Malformed requests must not pass the safety gate.
    return any(hostname == host or hostname.endswith('.' + host)
               for host in YOUTUBE_FAMILY_HOSTS)
