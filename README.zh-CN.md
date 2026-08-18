# 幻灯 Huandeng

**用纯文本写学术幻灯片——基于 [Quarto](https://quarto.org/) 和 [reveal.js](https://revealjs.com/)，自带一个专查"不报错的错"的检查工具，并自带 AI 技能，让大模型帮你改稿，但方向盘始终在你手里。**

[English](README.md)

一份 Markdown 文件，同时导出：现场用的网页、可以直接发给别人的单文件 HTML、两份保留了逐步动画的 PDF，以及某些会议非要不可的 PPTX。视频能播。还有一个检查工具，帮你拦住那些本来会带上讲台的错误。

"幻灯"来自"幻灯片"，字面意思是魔术灯笼。

## 为什么做这个

Keynote 和 PowerPoint 用起来很快，直到你想让大模型帮忙的那一刻。这时候幻灯片就是一个二进制文件：模型读不了、看不了 diff、也没法只改一个词而不重写整个它并不理解的文件。LaTeX Beamer 是纯文本，但编译慢，排版也折磨人。Quarto 给你 Markdown，reveal.js 给你 CSS——也就是说，你能想到的版式都能做出来。还缺的是外围那一圈：真实报告需要的导出格式，以及一种让助手改稿而不会悄悄改坏的机制。

最后这点才是设计目标。**这里的每一部分都是你能手改的文本，也都是模型能替你改的文本。** 两种模式你随时都能用。构建工具存在的意义，是让模型的修改变得安全：它会检查有没有幻灯片溢出、有没有图被拉伸、有没有图片根本没加载出来。

## 快速开始

```bash
brew install --cask quarto                  # 其他系统见 quarto.org
git clone <这个仓库>
cd huandeng
cp -r themes/university talks/my-talk       # 也可以是 paper、swiss、nord……见下
cd talks/my-talk
mv template.qmd talk.qmd
make preview
```

浏览器会打开这份幻灯片，你每次保存它都会自动刷新。编辑 `talk.qmd`，它就是你的了。

| | |
| --- | --- |
| `make` | 生成 `out/talk.html` |
| `make preview` | 同上，保存即刷新 |
| `make check` | 渲染，然后逐页检查那些不会报错的问题 |
| `make all` | 同时生成两份 PDF 和一份图片版 PowerPoint |
| `make standalone` | 一个可以直接发邮件的单文件 `.html` |
| `make png` | 每页一张 PNG，方便你逐页看 |
| `make theme THEME=nord` | 给这份幻灯片换一套外观（`make themes` 列出全部） |
| `make gallery` | 每套主题并排摆开，看一眼就能挑 |

`make` 和 `make preview` 只需要 Quarto。其余的需要 Python 和一个无头浏览器，见[需要装什么](#需要装什么)。

`demo/` 里把所有功能都跑了一遍，细节看 [`demo/README.md`](demo/README.md)。

### 用大模型

用 [Claude Code](https://claude.com/claude-code) 或 Codex 打开这个文件夹，直接用大白话说你要什么。`.agents/skills/` 里的技能已经告诉它这个仓库怎么用了，你不需要解释——**`quarto-deck`** 讲机制（本地的排版类、构建流程、那些不会报错的坑），**`quarto-academic-style`** 讲怎么写（要点要短、叙述放进演讲者备注、公式怎么写才好读）。`quarto-deck` 自带一整套参考文档，所以模型基本不需要上网查。两个技能都随仓库走，所以别人 clone 下来得到的指引和你完全一样。

> 写一份关于开尔文-亥姆霍兹不稳定性的幻灯片，图用 `~/figs/` 里的，内容参考 `notes.md`。

> 第 12 页太挤了，在不缩小字号的前提下改一下。

它会自己跑 `make check`，所以万一它把某一页写溢出了，那是它要修的报错，而不是你上台才发现的意外。

## 有什么

| | |
| --- | --- |
| **一份源文件，五种输出** | HTML、单文件 HTML、两份 PDF、一份图片版 PPTX，都来自同一个 `talk.qmd` |
| **保留逐步动画的 PDF** | `make pdf` 生成两份：一份每个动画步骤一页，用来上台；一份每页一张完整幻灯片，用来发给别人。都是用无头 Chromium 从真实的幻灯片打印出来的，所见即所得，全程不碰 LaTeX |
| **视频不需要任何流程** | 把 `.mp4` 放进 `attach/`，写一个 `<video>` 标签就行。如果动画也要在 PDF 里活下来，就用图片序列做成翻页动画：现场原地播放，纸上每帧一页 |
| **专门查"不报错的错"** | reveal.js 遇到装不下的幻灯片既不报错也不缩小，多出来的部分直接挂到边缘外，而观众能看到多少取决于屏幕的宽高比。`make check` 会抓出来，也会抓出被拉伸的图和根本没加载的图 |
| **看得见的页面边界** | 每页都在精确的 1280 × 720 里排版再整体缩放到屏幕；写稿时按 **X** 就能把这个框画出来 |
| **带出处的插图** | `::: {.fig}` 让出处贴着图本身的边缘，而不是幻灯片的边缘 |
| **和幻灯片长得一样的 PPTX** | 每页一张 4K 满幅图片。因为版式是 CSS，任何 PowerPoint 写出器都读不懂 CSS。不可编辑，但逐像素一致 |
| **十套外观，都不锁死** | 默认的一套，加上 `paper`、`swiss`、`whiteprint`、`solarized`、`nord`、`blueprint`、`signal`、`monochrome`、`cobalt` 九套。`make gallery` 把它们全部并排渲染出来，看着挑。`make theme THEME=paper` 把其中一套复制到你已经写好的幻灯片上，复制完这份幻灯片依然自己拥有它。见 [`themes/README.md`](themes/README.md) |
| **不会随时间烂掉的幻灯片** | 每份幻灯片自带主题、字体和素材的副本，几年后换台电脑、挪到别处，照样渲染成原样 |

## 目录结构

```
tools/build-slides.py   工具链——所有幻灯片共用，但不会被复制进任何一份
themes/                 十个起点。复制其中一个，不要直接改。
demo/                   所有功能的可运行参考
talks/                  你自己的——已 gitignore，你的幻灯片不会进这个仓库
trash/                  走不通的路，附一份说明为什么走不通
.agents/skills/         AI 技能（.claude/skills 是指向它的软链接）
Makefile                make check 一次检查所有幻灯片
```

一份幻灯片就是 `talk.qmd` + `_quarto.yml` + `theme.scss` + `fonts.html` + `guides.html` + `attach/`，外加一个只是包装上述命令、本身不含构建逻辑的 `Makefile`。

## 主题

每个报告都从复制其中一套开始。每一套都是一份能直接渲染、先看后用的完整幻灯片。

| | |
| --- | --- |
| `university` | 白底配 azure 蓝、Fira Sans、标题下一条细线——最朴素的院校风格 |
| `paper` | 像一页印出来的期刊论文：暖白纸、衬线正文、深蓝标题、深红强调 |
| `swiss` | 白、黑、一点红；粗线条，紧排标题 |
| `whiteprint` | 工程图纸：白底深蓝，直角，所有标注类文字用等宽字体 |
| `solarized` | 低对比的米色配青色，适合亮房间或长报告 |
| `nord` | 冷调深灰蓝，霜蓝色点缀 |
| `blueprint` | 深蓝底、等宽标题、琥珀色点缀 |
| `signal` | 像一份简报：暖米底、深藏青、一点古金；衬线标题，等宽标注 |
| `monochrome` | 象牙白配黑，完全没有颜色——整页唯一的颜色来自你的图 |
| `cobalt` | 方格纸：整页浅浅的网格，标题用钴蓝斜体衬线 |

复制其中一套就可以开始——`cp -r themes/paper talks/my-talk`；要给已经写好的幻灯片换一套：

```bash
cd talks/my-talk
make themes                  # 有哪些
make theme THEME=paper       # 把外观复制进来，复制完这份幻灯片依然自己拥有它
make check
```

里面放了两套深色主题，因为总有人要，但白底存下来的图放在深色页面上就是一块刺眼的白方块，这一点没有任何样式表能补救。细节见 [`themes/README.md`](themes/README.md)。

## 需要装什么

- **[Quarto](https://quarto.org/docs/get-started/)**——只要 HTML 的话，装它就够了。
- **Python 3.13、[uv](https://docs.astral.sh/uv/) 和 Chromium**——`make check`、`make pdf`、`make png`、`make pptx` 需要：

  ```bash
  uv sync
  uv run playwright install chromium
  ```

  浏览器在这里不是可选项：幻灯片的版式是 CSS，别的东西既没法忠实地打印它，也没法告诉你某一页的内容到底落在了哪里。
- **ffmpeg**——只有当你需要把视频转成浏览器能播的格式时才需要。

不需要 Node.js，也不需要 LaTeX。从 reveal.js 导出 PDF 的常规做法是 `decktape`，那需要 npm；用 Playwright 驱动 reveal 自己的 `?print-pdf` 版式能做同样的事，而且用的是检查工具本来就要用的依赖。

## 每份幻灯片都是自包含的

一份幻灯片被复制到任何地方，多年以后都应该还能正确渲染。`theme.scss`、`_quarto.yml`、`fonts.html`、`guides.html`、`fonts/` 和所有素材都是*副本*，不是 import，任何一份幻灯片都不读取自己目录以外的东西。

代价是实实在在的：改进 改进主题不会自动惠及你已经复制出去的报告，要带过去只能手动复制。换来的是，讲完的报告就被冻结了。你 2026 年讲过的那份，到 2030 年在另一台电脑上、在模板早已改版之后，依然渲染成一模一样的样子——因为它依赖的东西没有一样能在它脚下变化。对于那些要反复使用、反复发出去的会议报告和讲义，这笔交易是划算的。

`out/` 不进版本库，也从来不需要进。

## 致谢

基于 [Quarto](https://quarto.org/) 和 [reveal.js](https://revealjs.com/)。字体为 [Fira Sans](https://github.com/mozilla/Fira)，SIL OFL 授权。`themes/` 里有六套主题的配色和字体气质来自 lewis 的 [html-ppt-skill](https://github.com/lewislulu/html-ppt-skill)（MIT）；`signal`、`monochrome`、`cobalt` 三套来自 zarazhangrui 的 [beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates)（MIT），经由 [frontend-slides](https://github.com/zarazhangrui/frontend-slides)。都没有直接搬用代码——借的是配色和想法，在这里用 Quarto SCSS 重写。

MIT 授权，见 [LICENSE](LICENSE)。
