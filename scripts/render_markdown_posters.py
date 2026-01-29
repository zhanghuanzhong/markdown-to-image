from pathlib import Path

from poster_render import (
  DEFAULT_BASE_URL,
  render_section_to_image,
  split_markdown_by_section,
)


BASE_URL = DEFAULT_BASE_URL
OUTPUT_DIR = Path("output_posters")


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
    render_section_to_image(sec_md, i, OUTPUT_DIR, BASE_URL)

  print(f"完成！共生成 {len(sections)} 张海报，输出目录：{OUTPUT_DIR}")


if __name__ == "__main__":
  main()

