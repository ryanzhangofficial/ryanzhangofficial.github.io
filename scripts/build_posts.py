from datetime import datetime
from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"

NAV = """                <ul>
                    <li><a href="index.html">blog</a></li>
                    <li><a href="about.html">about me</a></li>
                    <li><a href="archives.html">archives</a></li>
                    <li><a href="https://github.com/ryanzhangofficial" target="_blank" rel="noreferrer">github</a></li>
                    <li><a href="https://scholar.google.com/citations?user=0kTN35wAAAAJ&amp;hl=en" target="_blank" rel="noreferrer">scholar</a></li>
                    <li><a href="https://www.linkedin.com/in/ryan-zhang-44557727b/" target="_blank" rel="noreferrer">linkedin</a></li>
                </ul>"""


def numbered_posts():
    files = []
    for path in POSTS_DIR.glob("*.txt"):
        match = re.fullmatch(r"(\d+)\.txt", path.name)
        if match:
            files.append((int(match.group(1)), path))
    return sorted(files, reverse=True)


def parse_post(number, path):
    text = path.read_text(encoding="utf-8").strip()
    title = f"Post {number}"
    date = datetime.fromtimestamp(path.stat().st_mtime).strftime("%B %Y")

    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)

    if lines and lines[0].lower().startswith("title:"):
        title = lines.pop(0).split(":", 1)[1].strip() or title
    if lines and lines[0].lower().startswith("date:"):
        date = lines.pop(0).split(":", 1)[1].strip() or date
    if lines and not lines[0].strip():
        lines.pop(0)

    body = "\n".join(lines).strip()
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
    return {
        "id": f"post-{number}",
        "title": title,
        "date": date,
        "paragraphs": paragraphs,
    }


def render_nav():
    return f"""        <div class="navbar">
            <nav>
{NAV}
            </nav>
        </div>"""


def render_post(post):
    paragraphs = "\n".join(f"                    <p>{escape(p)}</p>" for p in post["paragraphs"])
    return f"""                <article id="{post["id"]}">
                    <p class="date">{escape(post["date"])}</p>
                    <h1>{escape(post["title"])}</h1>
{paragraphs}
                </article>"""


def page(title, body):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)}</title>
    <link rel="stylesheet" href="styles/index.css">
</head>
<body>
    <div class="page">
{render_nav()}

        <main>
{body}
        </main>
    </div>
</body>
</html>
"""


def build():
    posts = [parse_post(number, path) for number, path in numbered_posts()]

    article_html = "\n\n".join(render_post(post) for post in posts)
    index_body = f"""            <section class="intro">
                <p>Notes by Ryan Zhang.</p>
                <p>Computer science, math, economics, research, current events, and whatever I am learning slowly enough to write down.</p>
            </section>

            <div class="articles">
{article_html}
            </div>"""

    archive_items = "\n".join(
        f'                <li><span>{escape(post["date"])}</span> <a href="index.html#{post["id"]}">{escape(post["title"])}</a></li>'
        for post in posts
    )
    archives_body = f"""            <section class="intro">
                <h1>Archives</h1>
                <p>All posts, newest first.</p>
            </section>

            <ul class="archive-list">
{archive_items}
            </ul>"""

    (ROOT / "index.html").write_text(page("Ryan Zhang", index_body), encoding="utf-8")
    (ROOT / "archives.html").write_text(page("archives", archives_body), encoding="utf-8")


if __name__ == "__main__":
    build()
