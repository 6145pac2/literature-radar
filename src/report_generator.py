"""Generate Markdown reports, plain email bodies, and the archive index."""

# 本模块负责三种输出：Markdown 周报、邮件纯文本正文和 GitHub Pages 历史索引。

import html
import re
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


# 英文主题词到周报中文栏目名的固定映射。
GROUP_LABELS = {
    "hydrothermal liquefaction": "水热转化",
    "biocrude": "生物原油",
    "waste valorization": "废弃物资源化",
    "microalgae": "微藻",
    "biochar": "生物炭",
    "biorefinery": "生物精炼",
}


# 首页和报告页共用同一套轻量样式，直接写入 HTML，避免额外前端依赖和资源路径问题。
PAGE_STYLES = """
:root {
  color-scheme: light;
  --ink: #18332d;
  --muted: #60736e;
  --brand: #147d64;
  --brand-dark: #0c5c4a;
  --accent: #d7a848;
  --line: #dce7e2;
  --surface: rgba(255, 255, 255, 0.92);
  --shadow: 0 18px 50px rgba(24, 51, 45, 0.10);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  color: var(--ink);
  background:
    radial-gradient(circle at 12% 0%, rgba(20, 125, 100, 0.12), transparent 32rem),
    linear-gradient(180deg, #f8fbf9 0%, #eef4f1 100%);
  font-family: "Segoe UI", "Microsoft YaHei", system-ui, sans-serif;
  line-height: 1.7;
  min-height: 100vh;
}
a { color: inherit; }
.container { width: min(1080px, calc(100% - 40px)); margin: 0 auto; }
.hero { padding: 72px 0 38px; }
.eyebrow {
  color: var(--brand);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}
h1 { margin: 8px 0 12px; font-size: clamp(2rem, 6vw, 3.8rem); line-height: 1.15; }
.subtitle { max-width: 680px; color: var(--muted); font-size: 1.05rem; }
.stats { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 28px; }
.stat {
  padding: 10px 16px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.7);
  color: var(--muted);
}
.stat strong { color: var(--ink); }
.report-grid { display: grid; gap: 18px; padding: 10px 0 72px; }
.report-card {
  display: grid;
  grid-template-columns: minmax(150px, 0.7fr) 1fr auto;
  gap: 24px;
  align-items: center;
  padding: 25px 28px;
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--surface);
  box-shadow: 0 8px 24px rgba(24, 51, 45, 0.06);
  text-decoration: none;
  transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
}
.report-card:hover, .report-card:focus-visible {
  transform: translateY(-3px);
  border-color: rgba(20, 125, 100, 0.45);
  box-shadow: var(--shadow);
  outline: none;
}
.card-date { font-size: 1.3rem; font-weight: 800; }
.card-meta { display: flex; flex-wrap: wrap; gap: 10px; color: var(--muted); }
.card-meta span { padding: 4px 10px; border-radius: 999px; background: #edf6f2; }
.arrow { color: var(--brand); font-weight: 800; white-space: nowrap; }
.empty { padding: 48px; border: 1px dashed var(--line); border-radius: 20px; text-align: center; color: var(--muted); }
.topbar { padding: 22px 0; border-bottom: 1px solid var(--line); background: rgba(248, 251, 249, 0.82); }
.back-link { color: var(--brand-dark); font-weight: 750; text-decoration: none; }
.report-shell { padding: 48px 0 80px; }
.report-header, .paper {
  border: 1px solid var(--line);
  border-radius: 22px;
  background: var(--surface);
  box-shadow: 0 8px 28px rgba(24, 51, 45, 0.06);
}
.report-header { padding: clamp(24px, 5vw, 44px); margin-bottom: 32px; }
.report-header h1 { font-size: clamp(1.8rem, 5vw, 3rem); }
.issue-badge { display: inline-block; padding: 5px 12px; border-radius: 999px; background: #e4f3ed; color: var(--brand-dark); font-weight: 800; }
.report-meta { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }
.report-meta span { padding: 7px 12px; border-radius: 10px; background: #f0f5f2; color: var(--muted); }
.section-title { margin: 38px 0 16px; font-size: 1.45rem; }
.section-title::before { content: ""; display: inline-block; width: 5px; height: 1.05em; margin-right: 10px; border-radius: 3px; background: var(--accent); vertical-align: -0.12em; }
.paper { padding: clamp(20px, 4vw, 30px); margin-bottom: 16px; }
.paper-title { margin: 0 0 12px; font-size: 1.12rem; font-weight: 800; line-height: 1.5; }
.paper p { margin: 7px 0; color: #405650; }
.paper .original-title { color: var(--muted); font-style: italic; }
.paper .summary { margin-top: 14px; padding: 15px 17px; border-left: 4px solid var(--brand); border-radius: 0 12px 12px 0; background: #edf6f2; color: var(--ink); }
.paper a { color: var(--brand-dark); overflow-wrap: anywhere; }
footer { padding: 28px 0 48px; color: var(--muted); text-align: center; font-size: 0.9rem; }
@media (max-width: 700px) {
  .container { width: min(100% - 24px, 1080px); }
  .hero { padding-top: 44px; }
  .report-card { grid-template-columns: 1fr; gap: 10px; padding: 21px; }
  .arrow { justify-self: start; }
}
"""


def _display(value: Any) -> str:
    """把期刊指标转换成适合显示在周报里的文字。

    参数 value：可能是影响因子数字、分区文字，也可能是空值 None。
    返回值：有数据时转成字符串；没有数据时返回“暂无配置”。
    函数名前的下划线表示它只是本文件内部使用的辅助函数。
    """
    # 这一行叫“条件表达式”：条件成立用左边的文字，否则执行右边的 str(value)。
    # None 代表“没有值”，空字符串 "" 代表“有字段但没有填写内容”。
    return "暂无配置" if value is None or value == "" else str(value)


def _paper_group(paper: Dict[str, Any], topics: Sequence[str]) -> str:
    """判断一篇论文应该放进周报的哪个主题栏目。

    参数 paper：包含标题命中词、摘要命中词等信息的一篇论文。
    参数 topics：config.yaml 中按顺序配置的全部主题关键词。
    返回值：贡献分数最高的那个主题关键词；同分时选择配置中靠前的词。
    """
    # 每个主题单独计算贡献；max 在同分时保留 topics 中更靠前的主题。
    contributions = {
        topic: (10 if topic in paper["matched_topics_title"] else 0)
        + (3 if topic in paper["matched_topics_abstract"] else 0)
        for topic in topics
    }
    return max(topics, key=lambda topic: contributions[topic])


def group_papers(
    papers: Sequence[Dict[str, Any]], topics: Sequence[str]
) -> Dict[str, List[Dict[str, Any]]]:
    """把论文列表整理成“主题关键词 -> 论文列表”的分组结果。

    参数 papers：本周所有通过筛选的新论文。
    参数 topics：全部主题关键词及它们期望的展示顺序。
    返回值：字典，每个关键词对应一个已按相关性从高到低排序的论文列表。
    每篇论文只会进入一个栏目，不会在周报中重复出现。
    """
    # OrderedDict 保持 config.yaml 中的主题顺序，空分组稍后不会显示。
    groups: Dict[str, List[Dict[str, Any]]] = OrderedDict(
        (topic, []) for topic in topics
    )
    for paper in papers:
        groups[_paper_group(paper, topics)].append(paper)
    for group in groups.values():
        group.sort(key=lambda paper: (-paper["score"], paper["doi"] or paper["openalex_id"]))
    return groups


def generate_report(
    papers: Sequence[Dict[str, Any]],
    topics: Sequence[str],
    exclusions: Sequence[str],
    start: datetime,
    end: datetime,
    retrieved_at: datetime,
    reports_dir: Path,
) -> Path:
    """根据处理完成的论文生成一份 Markdown 周报文件。

    papers 是论文数据；topics/exclusions 是主题词和排除词；start/end 是统计区间；
    retrieved_at 是实际检索时间；reports_dir 是报告保存目录。
    返回值是新生成报告的完整文件路径，主程序会继续用它发送邮件和生成网页。
    """
    # 报告文件名使用区间结束日期，即计划发送周一的日期。
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "weekly_report_{}.md".format(end.strftime("%Y-%m-%d"))
    # 理论总分：每个主题最多贡献标题 10 分和摘要 3 分。
    max_score = len(topics) * 13
    lines = [
        "# 文献雷达周报 {}".format(end.strftime("%Y-%m-%d")),
        "",
        "- 日期范围：{} 至 {}（左闭右开）".format(
            start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
        ),
        "- 论文总数：{}".format(len(papers)),
        "- 主题关键词：{}".format("、".join(topics) or "未配置"),
        "- 排除关键词：{}".format("、".join(exclusions) or "未配置"),
        "- 相关性评分：标题每命中1个主题词 +10分，摘要每命中1个主题词 +3分；"
        "本期共{}个主题词，理论总分{}分".format(len(topics), max_score),
        "- 检索时间：{}".format(retrieved_at.isoformat(timespec="seconds")),
        "",
        "---",
        "",
    ]
    # 序号跨分组连续递增；所有论文统一展示中英文标题和完整元数据。
    sequence = 1
    for topic, group in group_papers(papers, topics).items():
        if not group:
            continue
        lines.extend(["## {}".format(GROUP_LABELS.get(topic, topic)), ""])
        for paper in group:
            authors = ", ".join(paper["authors"]) or "—"
            identifier = paper["doi"] or paper["openalex_id"] or "—"
            if_text = _display(paper["if"])
            if paper.get("if_year"):
                if_text += "（{} JIF）".format(paper["if_year"])
            rank_text = _display(paper["rank"])
            if paper.get("rank_year"):
                rank_text += "（{}升级版）".format(paper["rank_year"])
            lines.extend(
                [
                    "{}. {}  ".format(sequence, paper["title_zh"]),
                    "   ({})  ".format(paper["title"]),
                    "   👤 {}  ".format(authors),
                    "   📖 **{}** | IF: {} | 中科院: {}  ".format(
                        paper["journal_name"],
                        if_text,
                        rank_text,
                    ),
                ]
            )
            if paper.get("rank_detail"):
                lines.append("   📚 小类分区: {}  ".format(paper["rank_detail"]))
            if paper.get("other_rank"):
                lines.append("   🏅 其他分级: {}  ".format(paper["other_rank"]))
            lines.extend(
                [
                    "   🔗 DOI: {}  ".format(identifier),
                    "   🎯 相关性得分: {}/{} (标题: {}; 摘要: {})  ".format(
                        paper["score"],
                        max_score,
                        ", ".join(paper["matched_topics_title"]) or "—",
                        ", ".join(paper["matched_topics_abstract"]) or "—",
                    ),
                ]
            )
            if paper["ai_summary"]:
                lines.append("   🤖 AI摘要：")
                lines.extend(
                    "   {}  ".format(section)
                    for section in paper["ai_summary"].splitlines()
                )
            else:
                lines.append("   🤖 AI摘要: 暂无（OpenAlex 未提供摘要或摘要生成失败）")
            lines.append("")
            sequence += 1
    if not papers:
        lines.extend(["本周没有检索到符合条件的新论文。", ""])
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def markdown_to_plain_text(markdown: str) -> str:
    """把 Markdown 周报转换成不支持富文本的邮箱也能阅读的纯文字。

    参数 markdown：完整的 Markdown 文本。
    返回值：去掉标题井号、分隔线和加粗符号后的普通文字。
    HTML 邮件无法显示时，邮件客户端会自动使用这个纯文字版本。
    """
    # 只去掉影响纯文本阅读的常见标记，正文和表情符号保持不变。
    text = re.sub(r"^\s*#{1,6}\s*", "", markdown, flags=re.MULTILINE)
    text = re.sub(r"^\s*---+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"(\*\*|__|`)", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _report_metadata(path: Path) -> Tuple[str, int]:
    """从一份历史周报中读取日期和论文数量，供首页卡片使用。

    参数 path：某一期 weekly_report_日期.md 文件路径。
    返回值：由“日期文字”和“论文篇数”组成的二元组，例如 ("2026-08-10", 9)。
    如果旧报告中找不到篇数，为避免程序崩溃，会暂时按 0 篇处理。
    """
    date = path.stem.replace("weekly_report_", "")
    markdown = path.read_text(encoding="utf-8")
    match = re.search(r"^- 论文总数：(\d+)\s*$", markdown, flags=re.MULTILINE)
    return date, int(match.group(1)) if match else 0


def _link_dois(text: str) -> str:
    """安全处理一段报告文字，并把 DOI 变成可以点击的网页链接。

    参数 text：论文标题、期刊信息或 DOI 等一行文字。
    返回值：经过 HTML 转义的安全文字，其中 **文字** 会变成加粗，DOI 会变成链接。
    HTML 转义可以防止标题中的特殊字符破坏网页结构。
    """
    escaped = html.escape(text.strip())
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    return re.sub(
        r"(10\.\d{4,9}/[A-Za-z0-9._;()/:+\-]+)",
        r'<a href="https://doi.org/\1" target="_blank" rel="noopener">\1</a>',
        escaped,
    )


def _report_body(markdown: str) -> str:
    """把程序生成的 Markdown 正文转换成一张张论文卡片的 HTML。

    参数 markdown：某一期周报的完整 Markdown 内容。
    返回值：只包含主题栏目和论文卡片的 HTML 片段。
    这个转换器只处理本程序固定生成的格式，不尝试支持所有 Markdown 语法。
    """
    parts: List[str] = []
    article_open = False
    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if not line or line.startswith("# ") or line.startswith("- ") or line == "---":
            continue
        if line.startswith("## "):
            if article_open:
                parts.append("</article>")
                article_open = False
            parts.append('<h2 class="section-title">{}</h2>'.format(html.escape(line[3:])))
            continue
        paper_match = re.match(r"^(\d+)\.\s+(.*)$", line)
        if paper_match:
            if article_open:
                parts.append("</article>")
            article_open = True
            fields = paper_match.group(2).split(" | ")
            parts.append('<article class="paper">')
            parts.append(
                '<h3 class="paper-title">{}. {}</h3>'.format(
                    paper_match.group(1), _link_dois(fields[0])
                )
            )
            parts.extend("<p>{}</p>".format(_link_dois(field)) for field in fields[1:])
            continue
        if article_open:
            text = line.strip()
            css_class = ""
            if text.startswith("(") and text.endswith(")"):
                css_class = ' class="original-title"'
            elif text.startswith("🤖"):
                css_class = ' class="summary"'
            parts.append("<p{}>{}</p>".format(css_class, _link_dois(text)))
    if article_open:
        parts.append("</article>")
    return "\n".join(parts) or '<div class="empty">本期没有符合条件的新论文。</div>'


def _write_report_page(path: Path, issue_number: int) -> Path:
    """为一份 Markdown 周报生成对应的美化 HTML 阅读页。

    参数 path：Markdown 周报路径；issue_number：它在历史中的期号。
    返回值：生成的 HTML 文件路径。HTML 与 Markdown 放在同一个 reports 文件夹中。
    Markdown 继续作为邮件附件，HTML 则用于本地浏览和 GitHub Pages。
    """
    markdown = path.read_text(encoding="utf-8")
    date, paper_count = _report_metadata(path)
    meta_lines = [
        html.escape(line[2:].strip())
        for line in markdown.splitlines()
        if line.startswith("- ")
    ]
    meta = "".join("<span>{}</span>".format(item) for item in meta_lines)
    page = """<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="文献雷达第 {issue} 期，共 {count} 篇论文">
    <title>文献雷达第 {issue} 期 · {date}</title>
    <style>{styles}</style>
  </head>
  <body>
    <nav class="topbar"><div class="container"><a class="back-link" href="../index.html">← 返回历史周报</a></div></nav>
    <main class="container report-shell">
      <header class="report-header">
        <span class="issue-badge">第 {issue} 期 · 共 {count} 篇</span>
        <h1>文献雷达周报</h1>
        <div class="card-date">{date}</div>
        <div class="report-meta">{meta}</div>
      </header>
      {body}
    </main>
    <footer>Literature Radar · 自动生成的每周文献档案</footer>
  </body>
</html>
""".format(
        issue=issue_number,
        count=paper_count,
        date=html.escape(date),
        styles=PAGE_STYLES,
        meta=meta,
        body=_report_body(markdown),
    )
    output_path = path.with_suffix(".html")
    output_path.write_text(page, encoding="utf-8")
    return output_path


def rebuild_index(reports_dir: Path, output_path: Path) -> None:
    """重新生成全部 HTML 报告页和历史周报首页。

    参数 reports_dir：保存所有 Markdown 周报的目录。
    参数 output_path：首页 index.html 的保存位置。
    没有返回值；函数会直接写文件。每次完整重建可避免漏掉旧报告或期号错乱。
    """
    # 按从旧到新的顺序确定固定期号，再按从新到旧的顺序展示卡片。
    chronological = sorted(reports_dir.glob("weekly_report_*.md"))
    records = []
    for issue_number, path in enumerate(chronological, start=1):
        date, count = _report_metadata(path)
        html_path = _write_report_page(path, issue_number)
        records.append((path, html_path, date, count, issue_number))
    records.reverse()
    cards = "\n".join(
        """<a class="report-card" href="reports/{filename}">
          <div class="card-date">{date}</div>
          <div class="card-meta"><span>第 {issue} 期</span><span>共 {count} 篇</span></div>
          <div class="arrow">查看完整周报 →</div>
        </a>""".format(
            filename=html.escape(html_path.name),
            date=html.escape(date),
            issue=issue_number,
            count=count,
        )
        for _, html_path, date, count, issue_number in records
    )
    content = cards or '<div class="empty">还没有历史周报，首次运行后会自动出现在这里。</div>'
    total_papers = sum(record[3] for record in records)
    output_path.write_text(
        """<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="按时间归档的文献雷达每周报告">
    <title>文献雷达历史周报</title>
    <style>{styles}</style>
  </head>
  <body>
    <main class="container">
      <header class="hero">
        <div class="eyebrow">Weekly Literature Radar</div>
        <h1>📚 历史文献周报</h1>
        <p class="subtitle">按周保存你的研究领域新文献，随时回看标题、作者、期刊信息与 AI 中文摘要。</p>
        <div class="stats">
          <div class="stat">累计 <strong>{issues}</strong> 期</div>
          <div class="stat">收录 <strong>{papers}</strong> 篇论文</div>
        </div>
      </header>
      <section class="report-grid" aria-label="历史周报列表">
        {content}
      </section>
    </main>
    <footer>Literature Radar · 每周一自动更新</footer>
  </body>
</html>
""".format(
            styles=PAGE_STYLES,
            issues=len(records),
            papers=total_papers,
            content=content,
        ),
        encoding="utf-8",
    )
