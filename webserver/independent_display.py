from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING

from aiohttp import web

if TYPE_CHECKING:
    from aiohttp.web_request import Request

log = logging.getLogger(__name__)

default_html = "<html><head><meta charset=\"UTF-8\"/><meta http-equiv=\"refresh\" content=\"{refresh}\" /></head><body>{content}</body></html>"


async def display_time(_: Request):
    response_html = default_html.format(refresh=1, content=f"{datetime.datetime.now().strftime('%H:%M:%S')}")
    return web.Response(text=response_html, content_type='text/html')
