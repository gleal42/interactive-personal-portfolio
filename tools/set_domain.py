#!/usr/bin/env python3
"""Move the site to its own domain in one step.

    python3 tools/set_domain.py goncaloleal.pt
    python3 tools/set_domain.py goncaloleal.pt --email ola@goncaloleal.pt

What it does:
  - rewrites every absolute link to the site (canonical, hreflang, og:image, README) to https://<domain>/
  - writes CNAME, which tells GitHub Pages to serve the site on that domain
  - writes robots.txt and sitemap.xml (only useful at the root of a domain, so they are made here)
  - with --email, adds an email line under the LinkedIn button on both pages

Run it only after the domain's DNS points at GitHub Pages (see "Custom domain" in the README):
as soon as CNAME is pushed, the github.io address starts redirecting to the new domain.
Safe to run again, e.g. to change the domain or the email.
"""
import argparse, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = {"index.html": "en", "pt/index.html": "pt"}
EMAIL_LINE = {
    "en": 'Or by email: <a href="mailto:{e}">{e}</a>',
    "pt": 'Ou por email: <a href="mailto:{e}">{e}</a>',
}


def current_base():
    m = re.search(r'<link rel="canonical" href="([^"]+)"', (ROOT / "index.html").read_text())
    if not m:
        sys.exit("No canonical link in index.html; can't tell the current address.")
    return m.group(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("domain", help="e.g. goncaloleal.pt (no https://, no path)")
    ap.add_argument("--email", help="address to show under the LinkedIn button, e.g. ola@goncaloleal.pt")
    a = ap.parse_args()

    domain = a.domain.strip().lower().removeprefix("https://").removeprefix("http://").strip("/")
    if not re.fullmatch(r"[a-z0-9-]+(\.[a-z0-9-]+)+", domain):
        sys.exit(f"'{a.domain}' doesn't look like a domain.")
    if a.email and not re.fullmatch(r"[^@\s<>\"]+@[^@\s<>\"]+\.[^@\s<>\"]+", a.email):
        sys.exit(f"'{a.email}' doesn't look like an email address.")

    old, new = current_base(), f"https://{domain}/"
    old_short = old.removeprefix("https://").rstrip("/")

    for rel, lang in PAGES.items():
        p = ROOT / rel
        s = p.read_text().replace(old, new)
        if a.email:
            line = '<p class="alt" data-email>' + EMAIL_LINE[lang].format(e=a.email) + "</p>"
            s, n = re.subn(r'<!-- domain:email -->|<p class="alt" data-email>.*?</p>', line, s)
            if n != 1:
                sys.exit(f"Couldn't find where to put the email in {rel}.")
        p.write_text(s)

    readme = ROOT / "README.md"
    readme.write_text(readme.read_text().replace(old, new).replace(f"[{old_short}]", f"[{domain}]"))

    (ROOT / "CNAME").write_text(domain + "\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {new}sitemap.xml\n")
    alts = (f'    <xhtml:link rel="alternate" hreflang="en" href="{new}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="pt" href="{new}pt/"/>\n')
    urls = "".join(f"  <url>\n    <loc>{u}</loc>\n{alts}  </url>\n" for u in (new, new + "pt/"))
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f"{urls}</urlset>\n")

    print(f"{old} -> {new}")
    print("Wrote CNAME, robots.txt, sitemap.xml" + (f"; email {a.email} on both pages" if a.email else ""))
    print("Next: commit, push to main, then Settings -> Pages -> Enforce HTTPS once the certificate is ready.")


if __name__ == "__main__":
    main()
