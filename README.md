# Good Default

Good Default is the public apex site for `gooddefault.com`: a searchable catalog of better household defaults plus entry points into the Good Default Substack.

This repo is the continuation of the older household product catalog project, with the site rebuilt around the Good Default name, domain, design, and catalog experience.

## Site Structure

- `index.html` is the apex homepage.
- `catalog.html` is the searchable product catalog.
- `compare.html` is the side-by-side comparison tool.
- `404.html` is the custom GitHub Pages 404 page.
- `dark-mode.css` adds `prefers-color-scheme: dark` support across the static pages.
- `data/products.csv` and `data/pfas-free-products.csv` contain the catalog seed data.
- `data/product-images.json` maps catalog rows to local product images in `assets/products/`.
- `scripts/check-internal-links.py` checks local links, anchors, assets, and product-image references.

## Domains

- `gooddefault.com`: this static apex site.
- `www.gooddefault.com`: should point to the apex site.
- `blog.gooddefault.com`: Good Default on Substack.

The repo includes `CNAME` for GitHub Pages.

## Local Preview

This is a static site. From the repo root:

```sh
python3 -m http.server 8091
```

Then open `http://localhost:8091/`.

## Checks

Run the internal link check before pushing:

```sh
python3 scripts/check-internal-links.py
```

GitHub Actions runs the same check on pushes and pull requests.
