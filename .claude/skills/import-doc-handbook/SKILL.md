---
name: import-doc-handbook
description: Use when given a doc.16781678.xyz site URL (e.g. /joyflix, /gpt-image2, /nanobanana) and asked to import the whole handbook into this project under content/docs/<slug>/ with all external images rehosted on Cloudflare R2, then ship via git push to auto-deploy on Vercel.
---

# Import doc.16781678.xyz Handbook → R2 → Vercel

End-to-end pipeline for adopting another `doc.16781678.xyz/<site>` handbook into this repo. The two scripts (`fetch_doc_sites.py`, `migrate_images.py`) do the heavy lifting; this skill is the wrapper checklist.

## Inputs

- A site URL like `https://doc.16781678.xyz/<slug>`. The site slug is the path segment (e.g. `gpt-image2`).
- Display title in Chinese (e.g. `"GPT Image 2 手册"`).

## Output

- `content/docs/<slug>/` populated with `index.mdx`, `meta.json`, and 7 subcategory folders (`getting-started`, `configuration`, `payment`, `deployment`, `video-tutorials`, `faq`, `others`) — only those that exist on source.
- All `<img>` and `![]()` URLs rewritten to `https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/<sha>.<ext>`.
- Handbook registered in 2 source files so the page header + middleware behave correctly.

## Steps

1. **Confirm it's a handbook root, not a leaf page.** A leaf page (e.g. `/gpt-image2/payment/foo`) has 3+ path segments. The root has just one. If user passes a leaf URL, ask whether they want the leaf or the whole site.

2. **Register the slug in `scripts/fetch_doc_sites.py` `SITE_TITLES`:**
   ```py
   SITE_TITLES = {
     ...
     "gpt-image2": "GPT Image 2 手册",
   }
   ```

3. **Fetch the whole site:**
   ```bash
   python scripts/fetch_doc_sites.py <slug>
   ```
   Expect: `harvested N urls`, then per-category counts. A handful of `[fail]` entries on **truncated** URL variants is normal — the harvester picks up partial sidebar hits and they 404. The full URL succeeds for the same page. Real failures (a unique URL that 404s) should be investigated.

4. **Migrate images to R2:**
   ```bash
   python scripts/migrate_images.py
   ```
   Idempotent — already-uploaded URLs are reused via `scripts/image_migration_manifest.json` (gitignored). Dead `github.com/user-attachments/...` links return 404 from source and stay external; everything else lands on R2.

5. **Strip anchor-in-anchor in headings:**
   ```bash
   python scripts/fix_heading_links.py
   ```
   Source pages frequently have headings like `## 访问 http://localhost:3000` or `## [Vercel](https://vercel.com/new) 创建项目`. fumadocs wraps every heading in an `<a href="#anchor">` for the TOC; if the heading already contains an `<a>` (from GFM auto-link or markdown link), you get nested `<a>` and a hydration error. The script unwraps `[text](url)` to text and wraps bare URLs in `` `code` ``.

6. **Verify zero remaining external images for the new slug:**
   ```bash
   python -c "import re,pathlib; root=pathlib.Path('content/docs/<slug>'); ext=[]; [ext.extend([(str(f),(m.group(1) or m.group(2))) for m in re.finditer(r'<img[^>]*src=\"(https?://[^\"]+)\"|!\[[^\]]*\]\((https?://[^)\s]+)', f.read_text(encoding='utf-8')) if 'pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev' not in (m.group(1) or m.group(2))]) for f in root.rglob('*.mdx')]; print(len(ext))"
   ```
   Should print `0`.

7. **Register the slug in 4 source files (all required):**

   - `src/components/docs/dynamic-app-name.tsx` — append to `HANDBOOK_TITLES` so the header renders the Chinese title.
   - `src/middleware.ts` — append to the `isHandbookRoot` regex so the root redirect stays uncached.
   - `src/app/[locale]/(landing)/page.tsx` — append a card object to the `featuredDocs` array (no `target` field on this page; matches existing entries).
   - `src/app/[locale]/(landing)/blog/page.tsx` — append a card object to the `featuredDocs` array (with `target: '_self'`; matches existing entries on this page).

   All four are next to the existing handbooks (`shipany-two`, `joyflix`, `nanobanana`, `gamiary`, `blog`, `markdown-blog`). The two card lists are NOT auto-derived from docs metadata — if you skip them, the new handbook is browsable by URL but invisible in the home/blog landing card grid. **Don't skip.**

8. **Local sanity check.**
   ```bash
   # Kill any stale dev servers (Windows):
   taskkill //F //IM node.exe
   # Clear Turbopack/fumadocs caches — Turbopack does NOT fully invalidate when whole content trees are added, leading to 404s on every /docs/* deep route:
   rm -rf .next .source
   pnpm dev
   ```
   Then `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000/docs/<slug>/getting-started/readme` should be `200`. If a sibling handbook (e.g. `joyflix`) also 404s, you skipped the cache wipe.

9. **Commit + push.** Vercel auto-deploys on push to `main`.
   ```bash
   git add scripts/fetch_doc_sites.py \
           src/components/docs/dynamic-app-name.tsx \
           src/middleware.ts \
           src/app/[locale]/\(landing\)/page.tsx \
           src/app/[locale]/\(landing\)/blog/page.tsx \
           content/docs/<slug>
   git commit -m "feat(docs): import <Slug> handbook with R2-hosted images"
   git push origin main
   ```
   Do **not** add `.claude/scheduled_tasks.lock` or `scripts/image_migration_manifest.json` (already gitignored).

## Common pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| `harvested 0 urls` | Wrong slug or site doesn't exist | Curl the root URL manually; confirm slug matches path segment |
| `[fail] /<slug>/<cat>/<truncated>` | Sidebar links contain partial paths | Ignore — full URL succeeds, no action needed |
| MDX parse error after fetch | Source page has unusual JSX/HTML | The `escape_prose_html` and friends in `fetch_shipany_docs.py` handle most cases; if a specific file breaks, hand-edit to escape `{`/`<` in prose |
| `migrate_images.py` says `missing scripts/.r2-creds.json` | R2 creds not configured locally | File exists in repo, ignored by git; ask user if missing |
| Vercel build fails on `*.md` exclusion | `vercel.json` was historically excluding md | Already fixed (commit `8032ad4`); don't re-introduce |
| Header shows English slug not Chinese title | Forgot step 6 (`HANDBOOK_TITLES`) | Add the entry, push again |
| New handbook missing from home/blog card grid | Forgot the two `featuredDocs` arrays in step 6 | Add cards to both `(landing)/page.tsx` and `(landing)/blog/page.tsx` |
| Local `/docs/<slug>/...` 404 (and joyflix etc. also 404) | Stale `.next` / `.source` after content tree added | `taskkill //F //IM node.exe && rm -rf .next .source && pnpm dev` |
| Sidebar shows "AI 出海手册" / `must-read` / `ideas` instead of the handbook's own categories | `content/docs/<slug>/meta.json` missing `"root": true` — folder gets merged into parent tree | Add `"root": true` to the root `meta.json`; this is now done by `fetch_doc_sites.py` automatically |
| Console: `<a> cannot be a descendant of <a>` / hydration error | Heading contains `[text](url)` or a bare URL → fumadocs TOC wraps it in another `<a>` | `python scripts/fix_heading_links.py` (always run after a fresh import) |

## Reference: site/category mapping

`fetch_doc_sites.py` translates URL segments to local folder names:

| URL segment | Local folder | Sidebar title |
|---|---|---|
| `getting-started` | `getting-started` | 快速开始 |
| `configuration` | `configuration` | 配置指南 |
| `payment` | `payment` | 支付集成 |
| `deployment` | `deployment` | 部署指南 |
| `video-tutorials` | `video-tutorials` | 视频教程 |
| `frequently-asked-questions` | `faq` | 常见问题 |
| `others` | `others` | 其他 |

Internal links of form `/cat/page` in source markdown are rewritten to `/docs/<slug>/cat/page`.

## Files this skill touches

- `scripts/fetch_doc_sites.py` (1 line: `SITE_TITLES`)
- `src/components/docs/dynamic-app-name.tsx` (1 line: `HANDBOOK_TITLES`)
- `src/middleware.ts` (1 token added to regex)
- `content/docs/<slug>/**` (created by script)
- `scripts/image_migration_manifest.json` (rewritten by image migrator; gitignored)
