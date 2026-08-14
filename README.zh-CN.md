# 幻灯 Huandeng

**用纯文本写学术幻灯片——基于 [Touying](https://github.com/touying-typ/touying) 和 [Typst](https://typst.app)，并自带 AI 技能，让大模型帮你改稿，但方向盘始终在你手里。**

[English](README.md)

一份源文件，同时导出三种格式：现场用的 PDF、可以直接发给别人的单文件 HTML、以及某些会议非要不可的 PPTX。视频在三种格式里都能播。还有一个检查工具，帮你拦住那些本来会带上讲台的错误。

"幻灯"来自"幻灯片"，字面意思是魔术灯笼；Touying（投影）是投影这个动作，幻灯是被投出来的东西。

## 为什么做这个

Keynote 和 PowerPoint 用起来很快，直到你想让大模型帮忙的那一刻。这时候幻灯片就是一个二进制文件：模型读不了、看不了 diff、也没法只改一个词而不重写整个它并不理解的文件。LaTeX Beamer 是纯文本，但编译慢，排版也折磨人。Typst 解决了编译速度和排版，Touying 让它成为一个真正的演示框架。还缺的是外围那一圈：真实报告需要的导出格式、视频流程，以及一种让助手改稿而不会悄悄改坏的机制。

最后这点才是设计目标。**这里的每一部分都是你能手改的文本，也都是模型能替你改的文本。** 两种模式你随时都能用。构建工具存在的意义，是让模型的修改变得安全：它会检查有没有幻灯片溢出、有没有图被拉伸、页数是不是和源文件说的一致。

## 快速开始

两种用法。做出来是同一份幻灯片——都是你能打开、能读、能自己改的文本文件。

### 手动

```bash
brew install typst                                  # 其他系统见 typst.app
git clone https://github.com/chongchonghe/huandeng.git
cd huandeng
cp -r template talks/my-talk                        # 你自己的副本，别动 template/
cd talks/my-talk
make
```

这会生成 `out/my-talk.pdf`。打开看看：一份可以直接上台的幻灯片。接下来编辑 `content.typ`，再跑一次 `make`，它就是你的了。

日常只需要 `make` 这一个命令。另外三个按需使用：

| | |
| --- | --- |
| `make` | 出 PDF |
| `make watch` | 每次保存自动重新编译，可以把 PDF 开在文本旁边 |
| `make check` | 编译，然后确认没有幻灯片悄悄溢出 |
| `make all` | 同时生成 HTML 页面和 PowerPoint 文件 |

**`make` 实际执行的**就是一行：

```bash
typst compile --font-path fonts main.typ out/my-talk.pdf
```

你想自己敲这行也完全可以，没有任何东西被藏起来。用 `make` 的理由只有 `--font-path fonts`：漏掉它，Typst 会悄悄换一套字体、把整份幻灯片重新排版一遍。`make` 不会忘。

`make` 和 `make watch` 只需要 Typst；`make check` 和 `make all` 还需要 Python，见[需要装什么](#需要装什么)。

### 用大模型

用 [Claude Code](https://claude.com/claude-code) 或 Codex 打开这个文件夹，直接用大白话说你要什么。`.agents/skills/` 里的技能已经告诉它这个仓库怎么用了，你不需要解释。

> 把 `~/Desktop/group-meeting.pptx` 转成 `talks/` 下面的一份新幻灯片。

> 写一份关于开尔文-亥姆霍兹不稳定性的幻灯片，图用 `~/figs/` 里的，内容参考 `notes.md`。

> 第 12 页太挤了，在不缩小字号的前提下改一下。

它会自己跑 `make check`，所以万一它把某一页写溢出了，那是它要修的报错，而不是你上台才发现的意外。

你随时可以接管。它写出来的和你自己会写的是同样的纯文本、同样的文件，任何时候开一个 `make watch` 就能自己接着改。

`demo/` 里把所有功能都跑了一遍，细节看 [`demo/README.md`](demo/README.md)。

## 有什么

| | |
| --- | --- |
| **一份源文件，三种格式** | 同一个 `content.typ` 出 PDF、单文件 HTML、PPTX |
| **视频在哪种格式里都能播** | HTML 里是真的 `<video>`，PPTX 里是影片对象，PDF 里是抽帧翻页动画——都来自同一句 `#movie("name")` |
| **专门查"不报错的错"** | 幻灯片内容超出一页时 Typst 不会报错，它会悄悄拆成两页。`--check` 会抓出来，也会抓出被拉伸的图 |
| **带出处的插图** | `#fig("x.png", caption: [..], credit: [He et al. 2025])`——出处贴着图本身的边缘，而不是幻灯片的边缘 |
| **AI 技能** | `slide-deck` 写幻灯片，`pptx-to-typst` 转换你已有的 PPT，`touying-author` 是 Touying 本身的文档 |
| **不会随时间烂掉的幻灯片** | 每份幻灯片自带一整套辅助函数、字体和素材的副本，几年后换台电脑、挪到别处，照样渲染成原样 |

## 配合大模型使用

三个技能放在 `.agents/skills/`，`.claude/skills` 是指向它的软链接；说明文件同理，真正的文件是 `AGENTS.md`，`CLAUDE.md` 是软链接。两处都以中立名字为准，所以 Claude Code 和 Codex 读的是同一批文件，换成别的 agent 最多再加一个软链接。（Windows 上请先设好 `git config --global core.symlinks true` 再 clone，否则这两个链接会变成普通文本文件。）

- **`slide-deck`**——在这个仓库里怎么写幻灯片：那些不属于 Touying 原生的本地辅助函数、版式约定，以及那些不会报错的坑。
- **`pptx-to-typst`**——把你已有的 PowerPoint 或 Keynote 转过来。不是截图导入：它会提取媒体文件，读取 PowerPoint 自己的裁剪框，让图按你原来裁的样子出来，纠正视频的像素宽高比，并把文字重新排成真正的 Typst 源码，方便你之后继续改。
- **`touying-author`**——把 Touying 上游文档收进来，省得模型靠猜 API。

这套组合能成立，关键在检查工具。助手改幻灯片时，偶尔会多写一行，而 Typst 不会抗议——它只会把溢出的部分推到第二页，看上去还挺像回事。`--check` 会把这种情况变成一个带幻灯片名字的报错，模型可以自己找到并改掉，你根本不用看见。

## 需要装什么

- **Typst**——出 PDF 只需要它。
- **Python 3.13 和 [uv](https://docs.astral.sh/uv/)**——HTML、PPTX 和 `--check` 需要。依赖都锁在 `uv.lock` 里。
- **ffmpeg**——只有幻灯片里有视频时才需要。

## 目录结构

```
tools/build-slides.py   工具链——所有幻灯片共用，但不会被复制进任何一份
template/               起点。复制它，不要直接改。
demo/                   所有功能的可运行参考
talks/                  你自己的——已 gitignore，你的幻灯片不会进这个仓库
.agents/skills/         AI 技能（.claude/skills 是指向它的软链接）
```

一份幻灯片就是 `main.typ` + `globals.typ` + `content.typ` + `attach/`，本身不含任何构建脚本。

## 一个值得说明的设计取舍

**每份幻灯片都是自包含的，这种重复是故意的。** `globals.typ`、`main.typ` 和字体都是*副本*，不是 import。任何一份幻灯片都不读取自己目录以外的东西。

代价是实实在在的：改进 `template/` 不会自动惠及你已经复制出去的报告，要带过去只能手动复制。换来的是，讲完的报告就被冻结了。你 2026 年讲过的那份，到 2030 年在另一台电脑上、在模板早已改版之后，依然渲染成一模一样的样子——因为它依赖的东西没有一样能在它脚下变化。对于那些要反复使用、反复发出去的会议报告和讲义，这笔交易是划算的。

## 致谢

基于 touying-typ 作者们的 [Touying](https://github.com/touying-typ/touying) 和 [Typst](https://typst.app)。字体为 [Fira Sans](https://github.com/mozilla/Fira) 和 [Fira Math](https://github.com/firamath/firamath)，SIL OFL 授权。

MIT 授权，见 [LICENSE](LICENSE)。
