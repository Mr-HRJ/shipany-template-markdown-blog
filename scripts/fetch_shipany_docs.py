"""Fetch ShipAny Two docs from doc.16781678.xyz and convert to MDX.

Output structure:
    content/docs/shipany-two/
      meta.json              # subcategory order
      <subcat>/meta.json     # page order
      <subcat>/<slug>.mdx    # article body with frontmatter

Usage:
    python scripts/fetch_shipany_docs.py
"""

from __future__ import annotations
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE = "https://doc.16781678.xyz"
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "content" / "docs" / "shipany-two"

# (subcat-slug, display-title, [(url-slug, display-title), ...])
# Order here = sidebar order on the source site (per user-provided listing).
SECTIONS: list[tuple[str, str, list[tuple[str, str]]]] = [
    ("getting-started", "快速开始", [
        ("readme", "仓库必读，请仔细阅读"),
        ("quick-start-guide", "项目快速上手图文教程"),
        ("update-logs", "更新日志"),
        ("have-some-pay", "必读！模版集合-老顾客优惠"),
        ("how-dev-to-production", "「一人可执行」ShipanyTwo 从 0 到上线完整闭环"),
    ]),
    ("configuration", "配置指南", [
        ("r2-storage-configuration", "项目中关于R2存储相关配置"),
        ("how-use-db-neon", "项目如何配置使用neon数据库"),
        ("how-use-local-psql", "项目本地开发时使用本地psql数据库"),
        ("share-about-dbbackup", "分享数据库不花钱-每天自动备份"),
        ("configuration-related-to-ai-image-generation-in-the-project", "项目中AI图像生成相关配置"),
    ]),
    ("payment", "支付集成", [
        ("stripe-configuration", "项目中关于Stripe支付相关配置"),
        ("use-pay-by-creem", "项目中关于Creem支付相关配置"),
        ("hk-bank-account-guide", "香港主流银行开户攻略"),
        ("how-to-use-creem-wise", "未办理港卡的同学看过来-试试Creem+Wise组合"),
        ("wise-card-guide", "Wise在线开卡（含PayPal无损转Wise实操视频）"),
        ("how-to-transfer-a-small-amount-of-money-back-to-china", "如何将海外挣的一点点钱弄回国内"),
        ("stripe-registration-guide", "如何用大陆护照+个人港卡注册Stripe个人账户"),
        ("stripe-registration-guide-no-company", "如何用大陆护照注册Stripe个人账户（无公司）"),
        ("how-set-stripe-radar", "Stripe雷达设置，防止封号"),
        ("saas-pay-calc", "SaaS出海收款计算器"),
        ("stripe-jiqiao", "Stripe减少客户流失+增加收入的小技巧"),
        ("stripe-re", "Stripe相关其他技巧"),
        ("how-use-paypal-cn", "Paypal.cn现在支持个人收款了"),
        ("paypal-world-china-person", "PayPal海外收款账号转至中国个人卖家"),
        ("paypal-cn-person", "Paypal.cn国内身份注册后如何接入使用"),
        ("how-china-person-pay", "国内无企业资质如何用微信支付宝收款"),
        ("how-test-pay", "支付测试卡"),
    ]),
    ("deployment", "部署指南", [
        ("deploy-to-vercel", "项目部署到Vercel"),
        ("deploy-to-cloudflare-mac", "项目部署到 Cloudflare Workers（Mac）"),
        ("deploy-to-cloudflare-windows", "项目部署到 Cloudflare Workers（Windows）"),
        ("how-to-view-project-logs-vercel-cloudflare", "项目如何查看日志（Vercel、Cloudflare）"),
    ]),
    ("video-tutorials", "视频教程", [
        ("ai-platform-tutorial", "ShipanyTwo视频实战：一站式AI生成平台"),
        ("ai-wallpaper-tutorial", "ShipanyTwo视频实战：AI壁纸生成器（含Creem）"),
        ("how-use-ai-cursor", "最全最细的Cursor AI编程零基础教程"),
        ("how-use-ai-trae", "Trae保姆级教程"),
    ]),
    ("faq", "常见问题", [
        ("problems-encountered-during-project-use", "项目使用遇到的问题"),
        ("error-api-auth-get-session", "[2025-12-13] /api/auth/get-session刷起来了"),
        ("error-get-configs", "[2025-12-24] 启动后频繁调用get-configs接口"),
    ]),
    ("others", "其他", [
        ("neon-or-supabase", "关于数据库Neon和Supabase的区别"),
        ("how-use-claude-code", "Claude Code零基础入门指南"),
        ("buy-cheap-domain", "如何购买便宜的域名"),
        ("hongkong-clubsim", "每年6块钱的香港手机号线上申请"),
        ("how-use-antigravity", "如何使用Antigravity"),
        ("chatgpt-one-year", "Chatgpt老兵认证免费一年会员"),
        ("how-desgin-webpage", "如何使用AI能力设计美化网页"),
        ("what-is-skills", "Skills到底是个啥+Antigravity安装skills"),
        ("how-use-ai-ide", "我在用的编程IDE"),
        ("how-use-clawdbot", "OpenClaw零基础入门"),
        ("ide-rules", "我对编程Agent的rules配置"),
        ("how-use-mofa", "如何买和使用魔法梯子"),
        ("saas-payment-ban-creem-database-leak-postmortem", "Creem账户被封后的完整复盘"),
    ]),
]

# Map faq slug since source URL uses 'frequently-asked-questions'
URL_SUBCAT = {
    "getting-started": "getting-started",
    "configuration": "configuration",
    "payment": "payment",
    "deployment": "deployment",
    "video-tutorials": "video-tutorials",
    "faq": "frequently-asked-questions",
    "others": "others",
}


# ---------- RSC extraction ----------

def js_unescape(s: str) -> str:
    s = s.replace("\\\\", "\x00")
    s = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)
    s = s.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
    s = s.replace('\\"', '"').replace("\\'", "'").replace("\\/", "/")
    s = s.replace("\x00", "\\")
    return s


def _extract_json_string_at(text: str, start: int) -> str | None:
    """Given `text[start] == '"'`, return decoded JSON string, or None on fail."""
    if start >= len(text) or text[start] != '"':
        return None
    i = start + 1
    out = []
    while i < len(text):
        ch = text[i]
        if ch == "\\":
            if i + 1 >= len(text):
                return None
            nxt = text[i + 1]
            if nxt == "u":
                try:
                    out.append(chr(int(text[i + 2 : i + 6], 16)))
                except ValueError:
                    return None
                i += 6
                continue
            esc = {"n": "\n", "r": "\r", "t": "\t", '"': '"',
                   "\\": "\\", "/": "/", "b": "\b", "f": "\f"}.get(nxt)
            if esc is None:
                return None
            out.append(esc)
            i += 2
            continue
        if ch == '"':
            return "".join(out)
        out.append(ch)
        i += 1
    return None


def extract_markdown(html: str) -> str | None:
    pushes = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
    if not pushes:
        return None
    full = js_unescape("".join(pushes))

    # Strategy 1: `<id>:T<hex>,<bytes>` text chunks (long-form articles).
    best = None
    best_score = -1
    for m in re.finditer(r"(?m)^([0-9a-f]+):T([0-9a-f]+),", full):
        byte_len = int(m.group(2), 16)
        start = m.end()
        tail = full[start:].encode("utf-8")
        content = tail[:byte_len].decode("utf-8", errors="replace")
        score = content.count("\n#") + content.count("```") * 2 + content.count("\n\n")
        if score > best_score and byte_len > 200:
            best_score = score
            best = content
    if best:
        return best

    # Strategy 2: `"content":"<json-string>"` (shorter pages). The value is a
    # JSON-encoded string so we parse it properly to keep escapes intact.
    # The article body comes from a MarkdownRenderer component, so the JSON
    # context before it contains `,null,{` — meta / i18n matches don't.
    best = None
    best_len = 0
    for m in re.finditer(r'"content":', full):
        ctx = full[max(0, m.start() - 60) : m.start()]
        if '"meta"' in ctx or '"fields":' in ctx or '"posts":' in ctx:
            continue
        if ",null,{" not in ctx:
            continue
        val = _extract_json_string_at(full, m.end())
        if val and len(val) > best_len:
            best_len = len(val)
            best = val
    return best


# ---------- Content transforms (match existing convert_markdown.py) ----------

_REMOTE_IMG_RE = re.compile(r"!\[([^\]]*)\]\((https?://[^)\s]+)(?:\s+\"[^\"]*\")?\)")
_LANG_REWRITE = {"dot": "text", "graphviz": "text"}
_FENCE_RE = re.compile(r"^(\s*```|\s*~~~)([A-Za-z0-9_+\-]*)(.*)$")
_FULL_TAG_RE = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)\b([^<>]*?)(/?)>")
_VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


_SUBCATS = {"getting-started", "configuration", "payment", "deployment",
            "video-tutorials", "frequently-asked-questions", "others"}
# Rewrite in-source relative links like `(/payment/foo)` → `(/docs/shipany-two/payment/foo)`.
# Map `frequently-asked-questions` → our slug `faq`.
_REL_LINK_RE = re.compile(r"\]\(/([a-z0-9\-]+)/([a-z0-9\-]+)(#[^)]*)?\)")


def rewrite_internal_links(body: str) -> str:
    def repl(m: re.Match) -> str:
        subcat, page, anchor = m.group(1), m.group(2), m.group(3) or ""
        if subcat not in _SUBCATS:
            return m.group(0)
        local = "faq" if subcat == "frequently-asked-questions" else subcat
        return f"](/docs/shipany-two/{local}/{page}{anchor})"
    return _REL_LINK_RE.sub(repl, body)


def rewrite_remote_images(body: str) -> str:
    def repl(m: re.Match) -> str:
        alt = m.group(1).replace('"', "&quot;")
        url = m.group(2)
        return f'<img src="{url}" alt="{alt}" />'
    return _REMOTE_IMG_RE.sub(repl, body)


def rewrite_fence_langs(body: str) -> str:
    out = []
    for line in body.split("\n"):
        m = _FENCE_RE.match(line)
        if m:
            prefix, lang, rest = m.group(1), m.group(2), m.group(3)
            if lang in _LANG_REWRITE:
                lang = _LANG_REWRITE[lang]
            out.append(f"{prefix}{lang}{rest}")
        else:
            out.append(line)
    return "\n".join(out)


_BARE_LT_RE = re.compile(r"<(?=[0-9!@#$%^&*(),\s])")
_BRACE_RE = re.compile(r"[{}]")


def _escape_prose_segment(seg: str) -> str:
    # First pass: escape bare `<` followed by digit/punctuation/whitespace so MDX
    # doesn't treat it as a tag start (e.g. "<1000 美元" in prose).
    seg = _BARE_LT_RE.sub("&lt;", seg)
    # Second pass: escape every `{` / `}` in prose so MDX doesn't try to parse
    # them as JSX expressions. Imported markdown frequently contains JSON
    # snippets or error payloads with `{"key":"value"}` which would otherwise
    # crash the MDX expression parser.
    seg = _BRACE_RE.sub(lambda m: "\\" + m.group(0), seg)

    def repl(m: re.Match) -> str:
        is_close = bool(m.group(1))
        name = m.group(2)
        self_close = bool(m.group(4))
        if self_close or is_close:
            # Self-closing or close tag — pass through. Multi-line tags
            # (e.g. an `</iframe>` closing an open tag from a prior line)
            # must NOT be escaped.
            return m.group(0)
        if name.lower() in _VOID_ELEMENTS:
            return m.group(0)
        close_re = re.compile(rf"</{re.escape(name)}\s*>", re.IGNORECASE)
        if close_re.search(seg, m.end()):
            return m.group(0)
        return "\\" + m.group(0)
    return _FULL_TAG_RE.sub(repl, seg)


# ---------- Additional MDX safety transforms ----------

_SMART_QUOTES_RE = re.compile(r"(<[a-zA-Z][^<>]*?)([“”‘’])")


def fix_smart_quotes_in_tags(body: str) -> str:
    """Inside HTML opening tags, replace unicode smart quotes with ASCII ``"``.

    Source pages occasionally have `src="//..p=1"` where the closing `"` is a
    Chinese right-double-quote (U+201D). MDX then fails to parse the attribute.
    Run in a loop because tags may contain multiple smart quotes.
    """
    def sub_in_tags(s: str) -> str:
        def repl(m: re.Match) -> str:
            tag_open = m.group(0)
            # Replace *all* smart quotes inside just this tag match
            fixed = re.sub(r"[“”‘’]", '"', tag_open)
            return fixed
        # Match a full opening tag `<name ...>` (non-greedy, no nested >)
        return re.sub(r"<[a-zA-Z][^<>]*>", repl, s)
    return sub_in_tags(body)


def self_close_void_tags(body: str) -> str:
    """Rewrite `<br>` → `<br />` (and `<hr>`) so MDX accepts them in prose.

    Only rewrites instances outside fenced code blocks.
    """
    out_lines: list[str] = []
    in_fence = False
    for line in body.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        line = re.sub(r"<(br|hr)\s*>", r"<\1 />", line, flags=re.IGNORECASE)
        out_lines.append(line)
    return "\n".join(out_lines)


_ESM_RESERVED = ("export ", "import ", "const ", "let ", "var ", "function ")


def wrap_bare_esm_lines(body: str) -> str:
    """Wrap bare top-of-line `export FOO=...` / `import ...` blocks in a fence.

    MDX parses `export`/`import` at column 0 as ES module syntax and breaks
    when it's really a shell snippet pasted without a code fence.
    """
    lines = body.split("\n")
    out: list[str] = []
    in_fence = False
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue
        if not in_fence and any(line.startswith(k) for k in _ESM_RESERVED):
            block = []
            while i < len(lines) and any(lines[i].startswith(k) for k in _ESM_RESERVED):
                block.append(lines[i])
                i += 1
            out.append("```bash")
            out.extend(block)
            out.append("```")
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def escape_prose_html(body: str) -> str:
    out_lines: list[str] = []
    in_fence = False
    for line in body.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        parts = line.split("`")
        for i in range(0, len(parts), 2):
            parts[i] = _escape_prose_segment(parts[i])
        out_lines.append("`".join(parts))
    return "\n".join(out_lines)


# ---------- Fetch + write ----------

def fetch_html(url: str, retries: int = 3) -> str:
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (doc-importer)",
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"failed fetching {url}: {last}")


def yaml_quote(s: str) -> str:
    # Single-quoted YAML: escape ' -> ''
    return s.replace("'", "''")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # Index page for this section
    (OUT / "index.mdx").write_text(
        "---\ntitle: 'ShipAny Two 使用手册'\n---\n\n"
        "ShipAny Two 模板的快速开始、配置、支付、部署与常见问题指南。\n",
        encoding="utf-8",
    )

    fail: list[tuple[str, str]] = []
    subcats: list[str] = []

    for subcat_slug, subcat_title, pages in SECTIONS:
        url_subcat = URL_SUBCAT[subcat_slug]
        sub_dir = OUT / subcat_slug
        sub_dir.mkdir(parents=True, exist_ok=True)
        page_slugs: list[str] = []

        for url_slug, title in pages:
            url = f"{BASE}/shipany-two/{url_subcat}/{url_slug}"
            print(f"[fetch] {url}")
            try:
                html = fetch_html(url)
                md = extract_markdown(html)
                if not md:
                    raise RuntimeError("no markdown chunk found")
            except Exception as e:
                print(f"  FAIL: {e}")
                fail.append((url, str(e)))
                continue

            body = rewrite_internal_links(md)
            body = rewrite_remote_images(body)
            body = rewrite_fence_langs(body)
            body = fix_smart_quotes_in_tags(body)
            body = self_close_void_tags(body)
            body = wrap_bare_esm_lines(body)
            body = escape_prose_html(body)
            out_file = sub_dir / f"{url_slug}.mdx"
            out_file.write_text(
                f"---\ntitle: '{yaml_quote(title)}'\n---\n\n{body}".rstrip() + "\n",
                encoding="utf-8",
            )
            page_slugs.append(url_slug)
            time.sleep(0.5)  # be polite

        (sub_dir / "meta.json").write_text(
            json.dumps({"title": subcat_title, "pages": page_slugs}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        subcats.append(subcat_slug)
        print(f"[{subcat_slug}] {len(page_slugs)} page(s)")

    (OUT / "meta.json").write_text(
        json.dumps({"title": "ShipAny Two 手册", "pages": subcats}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if fail:
        print("\n=== FAILED ===")
        for u, e in fail:
            print(f"  {u}  ->  {e}")
    print(f"\n=== done: {sum(len(p) for _,_,p in SECTIONS) - len(fail)} files ===")


if __name__ == "__main__":
    main()
