"""海报渲染公共逻辑，供 CLI 与 FastAPI 复用。"""
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright


DEFAULT_BASE_URL = "http://localhost:5173"


def split_markdown_by_section(content_or_path: str | Path) -> list[str]:
  """按二级标题（## ）将 markdown 切分为多个章节。
  content_or_path: 文件路径或 markdown 字符串。
  """
  if isinstance(content_or_path, Path):
    text = content_or_path.read_text(encoding="utf-8")
  elif isinstance(content_or_path, str) and Path(content_or_path).exists():
    text = Path(content_or_path).read_text(encoding="utf-8")
  else:
    text = content_or_path

  sections: list[str] = []
  current: list[str] = []

  for line in text.splitlines(keepends=True):
    if line.startswith("## ") and current:
      sections.append("".join(current))
      current = [line]
    else:
      current.append(line)

  if current:
    sections.append("".join(current))

  return sections


def render_section_to_image(
  md: str,
  index: int,
  output_dir: Path,
  base_url: str = DEFAULT_BASE_URL,
) -> Path:
  """调用前端渲染单个章节并截图为图片，返回保存的图片路径。"""
  output_dir.mkdir(exist_ok=True, parents=True)
  out_path = output_dir / f"poster_{index:02d}.png"

  safe_md = quote(md)
  url = f"{base_url}/?md={safe_md}"

  with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url, wait_until="networkidle")
    try:
      page.wait_for_selector('#poster-root[data-config-ready="true"]', timeout=15000)
    except Exception as e:
      browser.close()
      raise RuntimeError(
        f"等待海报配置超时: {e}. 请确认: 1) npm run dev 已启动  2) public/poster.config.yaml 存在"
      ) from e
    page.wait_for_timeout(600)
    page.locator("#poster-root").screenshot(path=str(out_path))
    browser.close()

  return out_path
