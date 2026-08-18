# One-off provenance script: parses charset_raw.json (checked in) from a
# local nonpareil clone. nonpareil/ is gitignored (see
# CLAUDE.md/.gitignore) and not needed to use charset_41.py - only to
# re-derive it. Re-clone with:
#   git clone --depth 1 https://github.com/brouhaha/nonpareil.git
import re, html, json

SRC = "/Users/jake/magellan/nonpareil/ncd/41c/41cv.ncd.tmpl"
pat = re.compile(r'<char id="(0x[0-9a-f]{2})"\s+text="([^"]*)"\s*>([^<]{14})</char>(?:\s*<!--(.*?)-->)?')

entries = []
with open(SRC) as f:
    for line in f:
        m = pat.search(line)
        if not m:
            continue
        cid, text, pattern, comment = m.groups()
        text = html.unescape(text)
        segs = ''.join(ch for idx, ch in enumerate(pattern) if ch != '.')
        entries.append(dict(id=cid, text=text, segs=segs, comment=(comment or '').strip()))

print(len(entries), "entries parsed")
with open("/Users/jake/magellan/hp41-display/tools/charset_raw.json","w") as f:
    json.dump(entries, f, indent=2)
for e in entries:
    print(e['id'], repr(e['text']), e['segs'], e['comment'])
