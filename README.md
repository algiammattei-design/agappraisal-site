# A.G. Appraisal Group website

Static site for agappraisalgroupllc.com, hosted on Vercel.

- Edit page content in `src/pages/` (one file per page; first line is JSON metadata: URL, title, description).
- Shared quote form: `src/partials/order.html`. Header, footer and SEO tags: `build.py`.
- Run `python3 build.py` to regenerate `public/` and `public/sitemap.xml`, then commit. Vercel serves `public/`.
- Web3Forms key: set `WEB3FORMS_KEY` in `build.py`.
