from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright


BASE_URL = "http://localhost:5173"
OUTPUT_DIR = Path("output_posters")


def split_markdown_by_section(path: str) -> list[str]:
  """按二级标题（## ）将 markdown 切分为多个章节，每个章节对应一张海报。"""
  text = Path(path).read_text(encoding="utf-8")
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


def render_section_to_image(md: str, index: int) -> None:
  """调用前端渲染单个章节并截图为图片。"""
  OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

  # 约定前端使用 window.location.search 中的 ?md 参数接收 markdown
  safe_md = quote(md)
  url = f"{BASE_URL}/?md={safe_md}"

  with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url, wait_until="networkidle")
    # 等待海报容器渲染完成（App.tsx 中的 #poster-root）
    page.wait_for_selector("#poster-root")
    page.locator("#poster-root").screenshot(
      path=str(OUTPUT_DIR / f"poster_{index:02d}.png")
    )
    browser.close()


def main() -> None:
  import argparse

  parser = argparse.ArgumentParser(
    description="从 markdown 文件按章节批量生成海报图片"
  )
  parser.add_argument(
    "markdown_path", type=str, help="输入的 markdown 文件路径，例如 docs/Claude_ai.md"
  )
  parser.add_argument(
    "--base-url",
    type=str,
    default="http://localhost:5173",
    help="前端服务地址（默认为 http://localhost:5173）",
  )
  parser.add_argument(
    "--output-dir",
    type=str,
    default="output_posters",
    help="输出图片目录（默认为 output_posters）",
  )

  args = parser.parse_args()

  global BASE_URL, OUTPUT_DIR
  BASE_URL = args.base_url
  OUTPUT_DIR = Path(args.output_dir)

  sections = split_markdown_by_section(args.markdown_path)
  if not sections:
    print("未从 markdown 中解析到任何章节（以 '## ' 开头的二级标题）。")
    return

  for i, sec_md in enumerate(sections, start=1):
    print(f"渲染第 {i} 个章节为海报...")
    render_section_to_image(sec_md, i)

  print(f"完成！共生成 {len(sections)} 张海报，输出目录：{OUTPUT_DIR}")


if __name__ == "__main__":
  main()

