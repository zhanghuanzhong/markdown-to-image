# 海报生成 API 使用说明

供 iPhone 等客户端通过 HTTP 请求：先根据产品名称生成 Markdown，再渲染海报并返回图片。

## 启动条件

1. **环境变量**：在项目根目录创建 `.env`，配置 DeepSeek API Key：
   ```bash
   cp .env.example .env
   # 编辑 .env，填入 DEEPSEEK_API_KEY=sk-xxx
   ```

2. **前端服务**：渲染海报依赖前端页面，需先启动：
   ```bash
   npm run dev
   ```
   默认运行在 `http://localhost:5173`。

3. **API 服务**：在项目根目录执行：
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```
   API 默认地址：`http://localhost:8000`。iPhone 需能访问该主机（同网段时用本机 IP，如 `http://192.168.x.x:8000`）。

---

## 接口一：生成产品介绍 Markdown

**POST** `/api/generate-markdown`

**请求体（JSON）**：
```json
{
  "product_name": "你的产品名称"
}
```

**成功响应（200）**：
```json
{
  "task_id": "产品名_20250129_123456",
  "markdown_path": "generated/产品名_20250129_123456.md",
  "message": "Markdown 已生成并保存"
}
```

客户端请保存 `task_id` 或 `markdown_path`，在第二步渲染海报时使用。

---

## 接口二：渲染海报并返回图片

**POST** `/api/render-poster`

**请求体（JSON）**，二选一：
```json
{ "task_id": "产品名_20250129_123456" }
```
或
```json
{ "markdown_path": "generated/产品名_20250129_123456.md" }
```

**成功响应（200）**：直接返回 PNG 图片（`Content-Type: image/png`），可作为图片保存或展示。

**错误**：未找到文件返回 404；Markdown 无 `## ` 章节返回 422；前端未启动或渲染失败返回 503。

---

## 健康检查

**GET** `/api/health`  
返回 `{"status": "ok"}`。

---

## iPhone 端调用示例（Swift / URLSession）

```swift
// 1. 生成 Markdown
var req = URLRequest(url: URL(string: "http://YOUR_SERVER:8000/api/generate-markdown")!)
req.httpMethod = "POST"
req.setValue("application/json", forHTTPHeaderField: "Content-Type")
req.httpBody = try? JSONEncoder().encode(["product_name": "我的产品"])
let (data, _) = try await URLSession.shared.data(for: req)
let result = try JSONDecoder().decode(GenerateMarkdownResponse.self, from: data)
let taskId = result.task_id

// 2. 渲染海报并获取图片
var renderReq = URLRequest(url: URL(string: "http://YOUR_SERVER:8000/api/render-poster")!)
renderReq.httpMethod = "POST"
renderReq.setValue("application/json", forHTTPHeaderField: "Content-Type")
renderReq.httpBody = try? JSONEncoder().encode(["task_id": taskId])
let (imageData, _) = try await URLSession.shared.data(for: renderReq)
// imageData 即为 PNG 图片数据，可保存或显示
```
