import aiohttp
import yaml

from aiohttp import web
from lxml import etree

@web.middleware
async def default_headers(request, handler):
    response = await handler(request)
 
    if response is not None:
        response.headers.setdefault("Access-Control-Allow-Origin", "*")
        response.headers.setdefault("Access-Control-Allow-Headers", "*")
        response.headers.setdefault("Access-Control-Allow-Methods", "*")
        return response

async def health(request):
    return web.Response(text="Alive and healthy.")

async def process(request):
    url = request.rel_url.query.get("url")

    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(url)
            html = await resp.text()
            root = etree.fromstring(html, etree.HTMLParser())
    except aiohttp.InvalidUrlClientError:
        return web.json_response({"error": "Unable to reach URL."})

    title = root.xpath(".//title")
    description = root.xpath(".//meta[@name='description']")
    image = root.xpath(".//meta[@property='og:image']")
    icon = root.xpath(".//link[@rel='icon]")

    return web.json_response({
        "title": title[0].text if title else None,
        "description": description[0].get("content") if description else None,
        "image": image[0].get("content") if image else None,
        "error": None
    })

server = web.Application(middlewares=[default_headers])
server.add_routes([web.get("/", health)])
server.add_routes([web.post("/process", process)])


with open("config.yaml") as f:
    config = yaml.safe_load(f) or {}

if config.get("ssl") == True:
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain("certificate.pem", "certificate.key")
    default_port = 443
else:
    ssl_context = None
    default_port = 80

if __name__ == "__main__":
    web.run_app(server, port=config.get("port", default_port), ssl_context=ssl_context)
