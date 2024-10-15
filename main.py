import aiohttp
import aiohttp_cors
import yaml

from aiohttp import web
from lxml import etree


async def health(request):
    return web.Response(text="Alive and healthy.")

async def process(request):
    url = request.rel_url.query.get("url")

    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(url)
            html = await resp.text()
    except aiohttp.ClientConnectionError:
        return web.json_response({"error": "Unable to reach URL."}, status=400)

    if not resp.headers.get("Content-Type", "").startswith("text/html"):
        return web.json_response({"error": "The provided URL is not an HTML document."}, status=400)

    root = etree.fromstring(html, etree.HTMLParser())

    title = root.xpath(".//title")
    description = root.xpath(".//meta[@name='description']")
    image = root.xpath(".//meta[@property='og:image']")


    return web.json_response({
        "url": url,
        "title": title[0].text if title else None,
        "description": description[0].get("content")[:150] + ("..." if len(description[0].get("content")) > 150 else "") if description else None,
        "image": image[0].get("content") if image else None,
        "error": None
    })

server = web.Application()
server.router.add_get("/", health)
server.router.add_post("/process", process)

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
    default_port = 443
else:
    ssl_context = None
    default_port = 80

if __name__ == "__main__":
    web.run_app(server, port=config.get("port", default_port), ssl_context=ssl_context)
