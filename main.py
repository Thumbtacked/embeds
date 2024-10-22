import aiohttp
import aiohttp_cors
import ssl
import urllib
import yaml

from aiohttp import web
from lxml import etree

async def health(request):
    return web.json_response({
        "version": "0.1.0",
        "description": "Microservice for scraping HTML metadata and proxying media."
    })

async def metadata(request):
    url = request.rel_url.query.get("url")

    if not url:
        return web.json_response({"error": "No URL provided."}, status=400)

    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(url)
            html = await resp.text()
    except aiohttp.ClientConnectionError:
        return web.json_response({"error": "Unable to reach URL."}, status=400)
    except (aiohttp.InvalidUrlClientError, aiohttp.NonHttpUrlClientError):
        return web.json_response({"error": "Unrecognized URL format."}, status=400)

    if not resp.headers.get("Content-Type", "").startswith("text/html"):
        return web.json_response({"error": "The provided URL is not an HTML document."}, status=400)

    root = etree.fromstring(html, etree.HTMLParser())
    url = str(resp.url)
    title = root.xpath(".//meta[@name='og:title']") or root.xpath(".//title")
    description = root.xpath(".//meta[@name='og:description']") or root.xpath(".//meta[@name='description']")
    image = root.xpath(".//meta[@property='og:image']")
    favicon = root.xpath(".//link[@rel='icon']") or root.xpath(".//link[@rel='shortcut icon']")

    return web.json_response({
        "url": url,
        "title": title[0].text if title else None,
        "description": description[0].get("content") if description else None,
        "image": image[0].get("content") if image else None,
        "favicon": urllib.parse.urljoin(url, favicon[0].get("href")) if favicon else None
    })

async def fetch(request):
    url = request.rel_url.query.get("url")

    if not url:
        return web.json_response({"error": "No URL provided."}, status=400)

    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(url)
            content = await resp.read()
    except aiohttp.ClientConnectionError:
        return web.json_response({"error": "Unable to reach URL."}, status=400)
    except (aiohttp.InvalidUrlClientError, aiohttp.NonHttpUrlClientError):
        return web.json_response({"error": "Unrecognized URL format."}, status=400)

    content_type = resp.headers.get("Content-Type").split(";")[0]

    return web.Response(body=content, content_type=content_type)

server = web.Application()
server.router.add_get("/", health)
server.router.add_get("/metadata", metadata)
server.router.add_get("/fetch", fetch)

cors = aiohttp_cors.setup(server, defaults={
   "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*"
    )
})

for route in list(server.router.routes()):
    cors.add(route)

with open("config.yaml") as f:
    config = yaml.safe_load(f) or {}

if config.get("ssl") == True:
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain("certificate.pem", "certificate.key")
else:
    ssl_context = None

if __name__ == "__main__":
    web.run_app(server, port=config["port"], ssl_context=ssl_context)
