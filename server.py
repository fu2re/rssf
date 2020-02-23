import asyncio
import logging
import re
from collections.abc import Mapping
from operator import itemgetter

from bs4 import BeautifulSoup
import sys
import re
import aiohttp
from aiohttp import web
from multidict import CIMultiDictProxy, CIMultiDict

logging.basicConfig(level=logging.DEBUG)
routes = web.RouteTableDef()

headers_restricted = {
    b'Transfer-Encoding',
    b'Content-Encoding',
}

replacement_dict = {
    '?': '&#63;',
    '&': '&amp;'
}


def multiple_replace(patterns, text):
    cp = re.compile("(%s)" % "|".join(map(re.escape, patterns.keys())))
    return cp.sub(lambda mo: patterns[mo.string[mo.start():mo.end()]], text)


def fix_text(text):
    soup = BeautifulSoup(text, features="xml")
    for p in soup.find_all('title'):
        p.string = multiple_replace(replacement_dict, p.string)
    return soup.prettify(formatter=None)


@routes.get('/')
async def handle(request):
    url = request.query.get('url')
    if not url:
        return web.Response(
            status=403
        )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            _m = [
                (k.decode("utf-8"), v.decode("utf-8")) for k, v in
                response.raw_headers if k not in headers_restricted
            ]
            headers = CIMultiDictProxy(CIMultiDict(_m))
            text = await response.text()
            return web.Response(
                headers=headers,
                text=fix_text(text)
            )

app = web.Application()
app.add_routes(routes)


if __name__ == '__main__':
    web.run_app(app, port=8001)
