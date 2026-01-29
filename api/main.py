"""
FastAPI 服务：接收 iPhone 端请求
1. 根据产品名称调用 DeepSeek 生成产品介绍 Markdown
2. 根据 Markdown 文件渲染海报并返回图片
"""
import re
import sys
from pathlib import Path
from datetime import datetime

try:
  from dotenv import load_dotenv
  load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
  pass

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# 项目根目录，保证可导入 scripts 下的模块
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from poster_render import render_section_to_image, split_markdown_by_section

app = FastAPI(title="海报生成 API", description="产品介绍 Markdown 生成与海报渲染")
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

GENERATED_DIR = ROOT / "generated"
POSTER_OUTPUT_DIR = ROOT / "output_posters"
TEMPLATE_PATH = ROOT / "docs" / "product_intro_template.md"
FRONTEND_BASE_URL = "http://localhost:5173"

GENERATED_DIR.mkdir(exist_ok=True)


def _slug(name: str) -> str:
  """产品名称转成安全文件名片段。"""
  s = re.sub(r"[^\w\s\u4e00-\u9fff-]", "", name)
  s = re.sub(r"\s+", "_", s.strip())[:32]
  return s or "product"


class GenerateMarkdownRequest(BaseModel):
  product_name: str


class GenerateMarkdownResponse(BaseModel):
  task_id: str
  markdown_path: str
  message: str


class RenderPosterRequest(BaseModel):
  markdown_path: str | None = None
  task_id: str | None = None


def _get_deepseek_client():
  from openai import OpenAI
  import os
  api_key = os.environ.get("DEEPSEEK_API_KEY")
  if not api_key:
    raise HTTPException(
      status_code=503,
      detail="未配置 DEEPSEEK_API_KEY，请在环境变量或 .env 中设置",
    )
  return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def _generate_markdown_with_deepseek(product_name: str) -> str:
  """使用 DeepSeek 按固定模板格式生成产品介绍 Markdown。"""
  template = TEMPLATE_PATH.read_text(encoding="utf-8")
  client = _get_deepseek_client()
  system_prompt = (
    "你是一位专业的产品文案撰写员。请严格按照用户提供的「产品介绍模板」格式，"
    "只输出一份完整的产品介绍 Markdown 文档。不要输出任何解释或多余内容，不要保留模板中的占位符（如 {{...}}），"
    "全部替换为针对该产品的具体、得体、简洁的文案。文档必须包含多个以「## 海报N」开头的二级标题章节。"
  )
  user_prompt = f"产品名称：{product_name}\n\n请根据以下模板格式，为该产品生成完整的产品介绍 Markdown（仅输出 Markdown，不要其他说明）：\n\n{template}"
  resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_prompt},
    ],
    temperature=0.6,
  )
  content = (resp.choices[0].message.content or "").strip()
  if not content:
    raise HTTPException(status_code=502, detail="DeepSeek 返回内容为空")
  return content


@app.post("/api/generate-markdown", response_model=GenerateMarkdownResponse)
def generate_markdown(req: GenerateMarkdownRequest):
  """接收产品名称，调用 DeepSeek 生成产品介绍 Markdown 并保存，返回 task_id 与 markdown_path。"""
  product_name = (req.product_name or "").strip()
  if not product_name:
    raise HTTPException(status_code=400, detail="product_name 不能为空")
  try:
    markdown_content = _generate_markdown_with_deepseek(product_name)
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=502, detail=f"调用 DeepSeek 失败: {e}") from e

  ts = datetime.now().strftime("%Y%m%d_%H%M%S")
  task_id = f"{_slug(product_name)}_{ts}"
  md_path = GENERATED_DIR / f"{task_id}.md"
  md_path.write_text(markdown_content, encoding="utf-8")
  return GenerateMarkdownResponse(
    task_id=task_id,
    markdown_path=str(md_path.relative_to(ROOT)),
    message="Markdown 已生成并保存",
  )


@app.post("/api/render-poster")
def render_poster(req: RenderPosterRequest):
  """根据 markdown_path 或 task_id 找到 Markdown 文件，渲染第一张海报并返回图片。"""
  if req.markdown_path:
    full_path = ROOT / req.markdown_path
  elif req.task_id:
    full_path = GENERATED_DIR / f"{req.task_id}.md"
  else:
    raise HTTPException(status_code=400, detail="请提供 markdown_path 或 task_id")

  if not full_path.is_file():
    raise HTTPException(status_code=404, detail=f"未找到文件: {full_path}")

  sections = split_markdown_by_section(full_path)
  if not sections:
    raise HTTPException(
      status_code=422,
      detail="Markdown 中未解析到任何章节（需以 ## 开头的二级标题）",
    )

  # 为本次请求单独建一个输出目录，避免并发覆盖；只渲染第一张并返回
  ts = datetime.now().strftime("%Y%m%d_%H%M%S")
  out_dir = POSTER_OUTPUT_DIR / "api" / ts
  out_dir.mkdir(exist_ok=True, parents=True)
  try:
    img_path = render_section_to_image(
      sections[0], 1, out_dir, base_url=FRONTEND_BASE_URL
    )
  except Exception as e:
    raise HTTPException(
      status_code=503,
      detail=f"海报渲染失败（请确认前端 npm run dev 已启动）: {e}",
    ) from e

  return FileResponse(
    img_path,
    media_type="image/png",
    filename=img_path.name,
  )


@app.get("/api/health")
def health():
  return {"status": "ok"}
