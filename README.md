# Thumbtacked Embed Service

Microservice for scraping HTML metadata and proxying media.

## Endpoints

<details>
<summary><code>GET</code> <code><b>/</b></code></summary><br />

Responds with the server status.

### JSON Response

| name        | description            |
|-------------|------------------------|
| version     | The server version.    |
| description | Purpose of the server. |

</details>

<details>
<summary><code>GET</code> <code><b>/metadata</b></code></summary><br />

Scrapes the metadata at a specific URL.

### Query Parameters

| name | description                             |
|------|-----------------------------------------|
| url  | The URL of an HTML document to process. |

### JSON Response

| name        | description                                                                         |
|-------------|-------------------------------------------------------------------------------------|
| url         | The URL of the processed page, taking into account redirects and proper formatting. |
| title       | The title of the processed HTML document.                                           |
| description | The description for the processed HTML document.                                    |
| image       | The URL of the OpenGraph image.                                                     |
| favicon     | The URL of the website favicon.                                                     |

</details>

<details>
<summary><code>GET</code> <code><b>/fetch</b></code></summary><br />

Fetches the media content at specific URL.

### Query Parameters

| name | description                     |
|------|---------------------------------|
| url  | The URL of the page to process. |

### Raw Response

The raw bytes content of the media being fetched, with the appropriate Content-Type header.

</details>
