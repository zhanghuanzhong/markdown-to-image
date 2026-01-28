# Markdown To Image / Markdown Poster

这个 React 组件库用于将 Markdown 渲染为漂亮的社交媒体图片（Poster）。此外，仓库内还包含一个基于 Next.js 的在线编辑器（Web Editor），可以一键部署，用作「Markdown 转海报图片」的在线编辑器站点。

![markdown-to-image banner](https://github.com/gcui-art/markdown-to-image/blob/main/public/banner.jpg)

- [English](./README.md) | [中文](./README_CN.md)
- [DEMO & Web Editor](https://readpo.com/zh/poster)
- [一键部署 Editor 到 Vercel](https://vercel.com/new/clone?repository-url=https://github.com/gcui-art/markdown-to-image&root-directory=example&project-name=markdown-to-image&repository-name=markdown-to-image)
- [NPM: markdown-to-image](https://www.npmjs.com/package/markdown-to-image)

⭐ 如果你觉得项目有用，欢迎点个 Star 和 Watch，方便关注后续更新。

---

## 目录

- [特性](#特性)
- [使用方式总览](#使用方式总览)
- [在你的项目中使用组件库](#在你的项目中使用组件库)
  - [安装](#安装)
  - [基础用法示例](#基础用法示例)
  - [复制图片与回调](#复制图片与回调)
  - [在 Next.js (SSR) 中使用](#在-nextjs-ssr-中使用)
- [使用 / 部署在线编辑器](#使用--部署在线编辑器)
  - [使用官方线上编辑器](#使用官方线上编辑器)
  - [一键部署到 Vercel](#一键部署到-vercel)
  - [本地运行 example 编辑器](#本地运行-example-编辑器)
- [在本仓库中本地开发组件库](#在本仓库中本地开发组件库)
  - [开发环境启动](#开发环境启动)
  - [构建组件库](#构建组件库)
  - [查看 Storybook 文档](#查看-storybook-文档)
- [常见问题 FAQ](#常见问题-faq)
- [贡献指南](#贡献指南)
- [许可证](#许可证)
- [相关链接](#相关链接)

---

## 特性

- ✅ 将 Markdown 渲染为适合社交分享的海报图片
- ✅ 内置一个模板，支持扩展更多模板
- ✅ 支持自定义主题，已内置 **9 个主题**
- ✅ 支持复制为图片（用于社交媒体分享、IM、博客封面等）
- ✅ 支持复制为 HTML 代码，可粘贴到邮件或富文本编辑器中
- ✅ 集成图片跨域代理，方便插入在线图片生成图文海报
- ✅ 支持一键部署到 Vercel 等平台
- ⏳ 更多内置模板（规划中）

---

## 使用方式总览

你可以通过两种方式使用本项目：

1. **在你的项目中集成组件库**
   - `markdown-to-image` 作为一个 React 组件库发布到 npm；
   - 你可以在自己的 React / Next.js / Vite 等项目中直接使用。

2. **作为在线编辑器使用**
   - 仓库 `example/` 目录下是一个基于 Next.js 的 Web Editor；
   - 支持一键部署到 Vercel，也可以本地运行，用作 Markdown → Poster 编辑器。

下面分别介绍这两种方式的详细使用方法。

---

## 在你的项目中使用组件库

`markdown-to-image` 导出一个主组件 `Md2Poster`，以及三个子组件：

- `Md2Poster`
- `Md2PosterHeader`
- `Md2PosterContent`
- `Md2PosterFooter`

### 安装

在你的 React 项目根目录安装依赖（任选一种包管理器）：

```bash
# npm
npm install markdown-to-image

# pnpm
pnpm install markdown-to-image

# yarn
yarn add markdown-to-image
```

> 组件库的 peerDependencies 为 `react` 和 `react-dom`，需使用 React 18 环境。

### 基础用法示例

在你的代码中引入样式及组件：

```jsx
import 'markdown-to-image/dist/style.css'
import {
  Md2Poster,
  Md2PosterContent,
  Md2PosterHeader,
  Md2PosterFooter,
} from 'markdown-to-image'

const markdown = `
# AI Morning Updates
> On April 29th, what's the latest in the AI field that should be on your radar?

1. **Tech hiccups in AI car race: NTU team misses final**
2. **AI complicates kids' online safety: Parents take charge**
...

![image](https://example.com/your-image.png)
`

export default function PosterDemo() {
  return (
    <Md2Poster theme="SpringGradientWave" size="mobile">
      <Md2PosterHeader className="flex justify-between items-center px-4">
        <span>@Nickname</span>
        <span>{new Date().toISOString().slice(0, 10)}</span>
      </Md2PosterHeader>

      <Md2PosterContent>{markdown}</Md2PosterContent>

      <Md2PosterFooter className="flex justify-center items-center gap-1">
        Powered by ReadPo.com
      </Md2PosterFooter>
    </Md2Poster>
  )
}
```

**常用 props 说明（简要）：**

- `Md2Poster`
  - `theme`: 主题名称，例如 `SpringGradientWave`
  - `size`: 海报尺寸，如 `mobile`（适配手机竖版）
  - `canCopy`: 是否开启复制为图片功能（布尔）
  - `copySuccessCallback`: 复制成功后的回调函数
  - `ref`: 通过 ref 获取内部方法（如 `handleCopy`）

- `Md2PosterHeader` / `Md2PosterFooter`
  - 接受 `className` 和 children，用于定制顶部 / 底部的信息（作者、日期、Logo 等）

- `Md2PosterContent`
  - children 为 Markdown 字符串，内部使用 `react-markdown + remark-gfm + rehype-raw` 渲染

### 复制图片与回调

组件内部基于 `modern-screenshot` 等库实现截图复制，支持「点击按钮复制为图片」。

示例（简化自仓库 `App.tsx`）：

```tsx
import React, { useRef } from 'react'
import {
  Md2Poster,
  Md2PosterContent,
  Md2PosterHeader,
  Md2PosterFooter,
} from 'markdown-to-image'
import 'markdown-to-image/dist/style.css'

export default function CopyDemo() {
  const markdownRef = useRef<any>(null)

  const markdown = `
# Markdown To Image
> 支持复制为图片的 Markdown 海报组件
`

  const handleCopy = () => {
    markdownRef?.current?.handleCopy().then(() => {
      alert('已复制为图片，可直接粘贴到支持粘贴图片的地方')
    })
  }

  const copySuccessCallback = () => {
    console.log('Copy Success')
  }

  return (
    <Md2Poster
      theme="SpringGradientWave"
      size="mobile"
      ref={markdownRef}
      canCopy
      copySuccessCallback={copySuccessCallback}
    >
      <Md2PosterHeader className="flex justify-between items-center px-4">
        <span>@Nickname</span>
        <span>{new Date().toISOString().slice(0, 10)}</span>
      </Md2PosterHeader>

      <Md2PosterContent>{markdown}</Md2PosterContent>

      <Md2PosterFooter className="flex justify-center items-center gap-1">
        <button
          onClick={handleCopy}
          className="border p-2 rounded border-white"
        >
          复制图片
        </button>
      </Md2PosterFooter>
    </Md2Poster>
  )
}
```

### 在 Next.js (SSR) 中使用

由于截图逻辑依赖浏览器环境（`window` / `document`），在 Next.js 等 SSR 框架中，**不要在服务端直接渲染组件**，而是通过 `next/dynamic` 关闭 SSR。

```tsx
// app/page.tsx 或 pages/index.tsx
import dynamic from 'next/dynamic'

const PosterEditor = dynamic(() => import('@/components/PosterEditor'), {
  ssr: false,
})

export default function Page() {
  return <PosterEditor />
}
```

`PosterEditor` 中再使用本组件：

```tsx
// components/PosterEditor.tsx
import React from 'react'
import {
  Md2Poster,
  Md2PosterContent,
  Md2PosterHeader,
  Md2PosterFooter,
} from 'markdown-to-image'
import 'markdown-to-image/dist/style.css'

function PosterEditor() {
  const markdown = `
# AI Morning Updates
> On April 29th, what's the latest in the AI field that should be on your radar?
`

  return (
    <Md2Poster theme="SpringGradientWave" size="mobile">
      <Md2PosterHeader className="flex justify-between items-center px-4">
        <span>@Nickname</span>
        <span>{new Date().toISOString().slice(0, 10)}</span>
      </Md2PosterHeader>
      <Md2PosterContent>{markdown}</Md2PosterContent>
      <Md2PosterFooter className="flex justify-center items-center gap-1">
        any children
      </Md2PosterFooter>
    </Md2Poster>
  )
}

export default PosterEditor
```

---

## 使用 / 部署在线编辑器

### 使用官方线上编辑器

如果你只想直接用，不想本地搭建或部署：

👉 打开浏览器访问：  
**[https://readpo.com/zh/poster](https://readpo.com/zh/poster)**

即可在线输入 Markdown、切换主题、预览、复制图片或 HTML。

### 一键部署到 Vercel

我们提供了 Vercel 的一键部署入口，会自动拉取本仓库并部署 `example` 目录下的 Next.js 应用：

👉 [一键部署 Editor 到 Vercel](https://vercel.com/new/clone?repository-url=https://github.com/gcui-art/markdown-to-image&root-directory=example&project-name=markdown-to-image&repository-name=markdown-to-image)

大致步骤：

1. 登录 Vercel（使用 GitHub / GitLab / Bitbucket 账号）
2. 打开上方链接
3. 按向导确认仓库与 `root-directory=example`
4. 点击 Deploy，等待构建完成
5. 部署完成后会得到一个形如 `https://your-project-name.vercel.app` 的地址，即你的在线编辑器

### 本地运行 example 编辑器

你也可以在本地运行 `example/` 项目进行二次开发或自定义：

在仓库根目录：

```bash
# 一键运行示例（脚本已封装）
npm run example
```

等价于：

```bash
cd example
npm install
npm run dev
```

浏览器访问 `http://localhost:3000` 即可看到编辑器界面。

如需单独在 `example/` 中操作：

```bash
cd example

# 安装依赖
npm install

# 开发环境
npm run dev

# 构建
npm run build

# 生产环境启动
npm run start
```

---

## 在本仓库中本地开发组件库

### 开发环境启动

在仓库根目录：

```bash
npm install

# 启动 Vite 开发环境
npm run dev
```

默认会在类似 `http://localhost:5173` 的地址启动开发服务器，渲染的是仓库根目录下 `src/App.tsx` 中的示例内容。

### 构建组件库

构建 npm 发布用的库产物：

```bash
npm run build
```

内部等价于：

- `tsc --p ./tsconfig-build.json`
- `vite build`

构建完成后，产物大致为：

- 入口：`dist/markdown-to-image.js`
- 类型声明：`dist/packages/index.d.ts`
- 样式：`dist/style.css`

### 查看 Storybook 文档

本仓库也提供 Storybook，用于以组件粒度查看示例与文档：

```bash
# 启动 Storybook
npm run storybook

# 构建静态 Storybook（可部署）
npm run build-storybook
```

Storybook 启动后通常访问：`http://localhost:6006`。

---

## 常见问题 FAQ

### 1. 在 Next.js / SSR 中报错 `ReferenceError: document is not defined`

请使用 `next/dynamic` 关闭 SSR，确保组件只在浏览器端渲染，示例见「在 Next.js (SSR) 中使用」小节。

### 2. 插入在线图片时 CORS 报错怎么办？

项目已经内置了图片跨域代理支持，一般直接使用 HTTPS 图片链接即可。如果你自建代理，请确保：

- 响应头设置了 `Access-Control-Allow-Origin: *` 或对应域名；
- 返回的是标准图片二进制内容。

### 3. 支持哪些 Markdown 特性？

依赖 `react-markdown + remark-gfm + rehype-raw`，支持：

- 标准 Markdown 语法（标题、加粗、列表、引用等）
- GFM 扩展（任务列表、表格等）
- 图片、链接以及部分内嵌 HTML（注意安全性）

### 4. 如何自定义主题和样式？

- 组件使用 TailwindCSS + `tailwind-merge`，可以通过传入 `className` 来覆写布局和样式；
- 你也可以在本仓库中扩展新的背景图片和主题配置，然后重新构建发布。

---

## 贡献指南

你可以通过以下方式支持这个项目：

1. **Fork 并提交 Pull Request**  
   - 欢迎任何让组件或编辑器变得更好、更强大的 PR（新主题、新功能、Bug 修复等）。

2. **提交 Issue**  
   - 欢迎提交 Bug 反馈、功能建议或使用问题，我们会尽量及时回复。

3. **赞助/捐赠**  
   - 仓库顶部提供了 Sponsor 按钮，如果你觉得这个项目对你有帮助，可以请我们喝一杯咖啡 ☕。

4. **推荐与传播**  
   - 向同事 / 朋友 / 社区推荐该项目；
   - 给仓库点个 Star；
   - 在使用它的项目或文章中附上仓库链接。

---

## 许可证

本项目使用 **Apache 2.0** 开源许可证，具体条款请查看仓库中的 `LICENSE` 文件。

---

## 相关链接

- 我们的其他开源项目：  
  [Suno AI API](https://github.com/gcui-art/suno-api)
- 演示站点：  
  [https://readpo.com/zh/poster](https://readpo.com/zh/poster)
- npm 包：  
  [npm: markdown-to-image](https://www.npmjs.com/package/markdown-to-image)

