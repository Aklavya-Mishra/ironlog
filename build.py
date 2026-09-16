"""
Builds the hosted legal pages from the app's own PRIVACY.md.

Play requires the hosted policy and the in-app policy to say the same thing, so the page
is generated rather than retyped: edit PRIVACY.md, re-run this, push.
"""
import html
import io
import re
import pathlib

SRC = pathlib.Path(r"C:\Users\Admin\AndroidStudioProjects\ironlog-public\PRIVACY.md")

STYLE = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 0 20px 72px;
  font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #1b1f33; background: #f4f5fb;
}
main { max-width: 760px; margin: 0 auto; }
header { padding: 48px 0 8px; }
h1 { font-size: 30px; line-height: 1.2; margin: 0 0 8px; letter-spacing: -0.02em; }
h2 { font-size: 21px; margin: 40px 0 10px; letter-spacing: -0.01em; }
p, li { color: #2c3149; }
em { color: #6b7192; font-style: normal; font-size: 14px; }
a { color: #5b3df5; }
blockquote { display: none; }
table { border-collapse: collapse; width: 100%; margin: 16px 0; display: block; overflow-x: auto; }
th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #dfe2ef; vertical-align: top; }
th { font-size: 13px; text-transform: uppercase; letter-spacing: .04em; color: #6b7192; }
.card { background: #fff; border: 1px solid #e4e7f2; border-radius: 16px; padding: 24px; margin: 24px 0; }
.back { display: inline-block; margin-top: 40px; font-size: 14px; }
footer { margin-top: 56px; font-size: 13px; color: #6b7192; }
"""


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"&lt;(https?://[^&]+)&gt;", r'<a href="\1">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"<em>\1</em>", text)
    return text


def convert(md: str) -> str:
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("> "):                       # editor notes, not for the public page
            i += 1
        elif line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>")
            i += 1
        elif line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[2:]]
            out.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>")
            for r in body:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            out.append("</tbody></table>")
        elif line.startswith("- "):
            out.append("<ul>")
            while i < len(lines) and lines[i].startswith("- "):
                item = lines[i][2:]
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                    item += " " + lines[i].strip()
                    i += 1
                out.append(f"<li>{inline(item)}</li>")
            out.append("</ul>")
        elif not line:
            i += 1
        else:
            para = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "-", "|", ">")):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)


def page(title: str, body: str, back: bool = True) -> str:
    link = '<a class="back" href="./">&larr; Ironlog</a>' if back else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<style>{STYLE}</style>
</head>
<body>
<main>
{body}
{link}
<footer>Ironlog — a training log for Android. Contact: <a href="mailto:aklavya.mishra123@gmail.com">aklavya.mishra123@gmail.com</a></footer>
</main>
</body>
</html>
"""


md = SRC.read_text(encoding="utf-8")
pathlib.Path("privacy.html").write_text(page("Privacy Policy — Ironlog", convert(md)), encoding="utf-8")
print("privacy.html", len(md), "chars of markdown converted")
