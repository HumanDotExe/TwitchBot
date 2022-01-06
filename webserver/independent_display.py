import datetime
import logging

from aiohttp import web
from aiohttp.web_request import Request

log = logging.getLogger(__name__)

default_html = "<html><head><meta charset=\"UTF-8\"/><meta http-equiv=\"refresh\" content=\"{refresh}\" /></head><body>{content}</body></html>"


async def display_time(request: Request):
    response_html = default_html.format(refresh=1, content=f"{datetime.datetime.now().strftime('%H:%M:%S')}")
    return web.Response(text=response_html, content_type='text/html')
