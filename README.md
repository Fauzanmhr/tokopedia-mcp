# tokopedia-mcp

> **Disclaimer:** Proyek ini dibuat untuk tujuan edukasi semata. Penulis tidak
> berafiliasi dengan Tokopedia dan tidak bertanggung jawab atas penyalahgunaan
> proyek ini. Gunakan dengan bijak.

Server [MCP](https://modelcontextprotocol.io) untuk pencarian produk
Tokopedia — mencakup pencarian produk, detail produk, dan ulasan pelanggan —
yang dapat langsung digunakan dari klien LLM (Claude Desktop, Claude Code,
Cursor, dan lainnya).

Dibangun dengan `mcp` 2.x (`MCPServer`), `curl-cffi` (untuk impersonasi sidik
jari TLS), dan model pydantic. Seluruh harga dalam Rupiah (IDR).

## Tools

| Tool                    | Fungsi                                                                 |
| ----------------------- | ---------------------------------------------------------------------- |
| `search_products`       | Mencari produk berdasarkan kata kunci dengan filter opsional (rentang harga, kondisi, tipe toko, rating minimum, produk baru, gratis ongkir, diskon, COD, dan lainnya). Mengembalikan `{products, count}`. |
| `get_product_details`   | Mengambil detail lengkap satu produk berdasarkan id atau URL: harga, deskripsi, varian, stok, media, dan toko. |
| `get_product_reviews`   | Mengambil ulasan pelanggan: pesan, rating, informasi pengguna, dan balasan penjual. Mengembalikan `{reviews, count}`. |

## Instalasi

Membutuhkan Python >= 3.10. Pasang [uv](https://docs.astral.sh/uv/) terlebih
dahulu (di Arch: `sudo pacman -S uv`, di macOS: `brew install uv`, atau lewat
installer resmi dari astral.sh), lalu:

```bash
uv sync            # membuat .venv sekaligus memasang dependensi
```

Tidak memakai uv? Bisa juga dengan pip biasa:

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

## Menjalankan

Menggunakan transport stdio (default — untuk klien MCP):

```bash
uv run tokopedia-mcp
# atau: uv run python -m tokopedia_mcp
```

Untuk transport jaringan:

```bash
uv run tokopedia-mcp --transport sse --port 8000
uv run tokopedia-mcp --transport streamable-http --port 8000
```

Contoh konfigurasi di Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "tokopedia": {
      "command": "/absolute/path/to/tokopedia-mcp/.venv/bin/tokopedia-mcp"
    }
  }
}
```

## Pengujian

```bash
uv run pytest                 # pengujian offline memakai fixture terekam, tanpa internet
uv run pytest -m live         # pengujian end-to-end: menjalankan server dan memanggil Tokopedia langsung
```

## Cara kerja

Tokopedia tidak menyediakan API pencarian produk publik, sehingga server ini
berkomunikasi langsung dengan GraphQL API internal yang digunakan aplikasi iOS
resmi:

- `POST gql.tokopedia.com/graphql/SearchResult/getProductResult` — pencarian
- `POST gql.tokopedia.com/graphql/ProductDetails/getPDPLayout` — detail produk
- `POST gql.tokopedia.com/graphql/ProductReview/getProductReviewReadingList` — ulasan

Lapisan edge (Akamai) menolak permintaan yang tidak menyerupai aplikasi asli.
Karena itu setiap permintaan membawa header khusus aplikasi beserta
**identitas perangkat acak yang segar** (user id, `Bd-Device-Id`, payload
fingerprint, timestamp) dan sidik jari TLS Safari melalui impersonasi
`curl-cffi`. Klien juga otomatis melakukan retry pada kegagalan sementara
(backoff eksponensial) dan membuang duplikat hasil pencarian antar halaman.

## Struktur proyek

```
src/tokopedia_mcp/
  queries.py     # query GraphQL dan path endpoint
  models.py      # model pydantic: Product, Shop, Review, SearchFilters
  extractors.py  # parsing murni: payload API -> model (dapat diuji offline)
  client.py      # TokopediaClient: HTTP asinkron, retry, paginasi
  server.py      # MCPServer + definisi tools
  __main__.py    # titik masuk CLI (stdio / sse / streamable-http)
tests/
  fixtures/      # respons asli yang terekam, dipakai pengujian offline
```

## Kredit

Query GraphQL beserta format permintaannya diambil dari
[tokopaedi](https://github.com/hilmiazizi/tokopaedi) karya
[Hilmi Azizi](https://github.com/hilmiazizi). Terima kasih!

## Lisensi

MIT
