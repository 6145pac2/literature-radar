"""Generate concise Chinese summaries through the DeepSeek API."""

# 本模块只为相关性最高且有摘要的论文调用 DeepSeek，并把结果写入 ai_summary。

import logging
import re
from typing import Any, Dict, List

from openai import OpenAI


# 统一提示词保证不同论文都能按相同顺序快速阅读。
PROMPT = """Create a rapid-reading summary in Chinese based only on the title and abstract below.
The summary should contain 450-700 Chinese characters and use exactly these four labels in this order:
研究目的：
研究方法：
关键结果：
主要结论：

Write concise complete sentences after each label. Prefer specific information about research objects,
materials, experimental conditions, methods, control groups, numerical results, units, limitations,
and practical significance. Avoid generic filler. Never cut off a number, unit, parenthesis, or sentence.
Do not invent information; if the abstract does not provide a requested detail, state “原摘要未说明”.
Use plain text without Markdown or bullet points. Keep key technical terms such as HTL and biocrude
in English.

Title: {title}
Abstract: {abstract}
"""

# 首次结果不合格时只重写一次，避免无限调用 API 和产生不可控费用。
REWRITE_PROMPT = """Rewrite the draft below as a complete Chinese rapid-reading summary.
Use exactly these four labels in order: 研究目的：研究方法：关键结果：主要结论：
Keep the total length between 450 and 700 Chinese characters. Preserve research objects, materials,
experimental conditions, methods, comparisons, numerical results, units, limitations, and practical
significance. Remove generic filler, end every section with a complete sentence, and never use an
ellipsis. Base the rewrite only on the supplied title and abstract; do not invent facts. Output plain
text only.

Title: {title}
Abstract: {abstract}
Draft: {draft}
"""

REQUIRED_SECTIONS = ("研究目的：", "研究方法：", "关键结果：", "主要结论：")
MIN_SUMMARY_LENGTH = 400
MAX_SUMMARY_LENGTH = 850


def clean_summary(text: str) -> str:
    """清理 AI 返回内容中的 Markdown 符号和多余空格，得到适合邮件展示的纯文字。"""
    # 邮件需要纯文本显示，因此去掉常见 Markdown 符号并合并多余空白。
    text = re.sub(r"(\*\*|__|`|#+)", "", text or "")
    return re.sub(r"\s+", " ", text).strip()


def _summary_is_complete(text: str) -> bool:
    """确认四个板块顺序正确，且正文没有省略号或残缺结尾。"""
    positions = [text.find(label) for label in REQUIRED_SECTIONS]
    return (
        all(position >= 0 for position in positions)
        and positions == sorted(positions)
        and all(text.count(label) == 1 for label in REQUIRED_SECTIONS)
        and text.endswith(("。", "！", "？", ".", "!", "?"))
        and "..." not in text
        and "…" not in text
    )


def summary_needs_rewrite(text: str) -> bool:
    """检查摘要是否达到建议长度并具有完整、固定的四板块结构。"""
    return not (
        MIN_SUMMARY_LENGTH <= len(text) <= MAX_SUMMARY_LENGTH
        and _summary_is_complete(text)
    )


def format_summary(text: str) -> str:
    """把四个摘要标题加粗并分别放到新行，方便在邮件和周报中快速浏览。"""
    for label in REQUIRED_SECTIONS:
        text = text.replace(label, "\n**{}**：".format(label[:-1]), 1)
    return text.lstrip()


def _request_summary(
    client: OpenAI,
    config: Dict[str, Any],
    prompt: str,
) -> str:
    """向 DeepSeek 发送一次提示词，并返回清理后的纯文本摘要。"""
    response = client.chat.completions.create(
        model=config["model"],
        messages=[
            {
                "role": "system",
                "content": "You are a precise scientific literature summarization assistant.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=config.get("max_tokens", 1600),
        temperature=config.get("temperature", 0.3),
    )
    return clean_summary(response.choices[0].message.content or "")


def summarize_top_papers(
    papers: List[Dict[str, Any]],
    top_k: int,
    config: Dict[str, Any],
    logger: logging.Logger,
) -> None:
    """为得分最高的若干篇论文生成中文 AI 摘要。

    papers 是已按相关性排序的论文；top_k 是最多处理篇数；config 是 DeepSeek 配置。
    摘要会直接写入 paper["ai_summary"]；没有原始摘要或 API 失败时跳过并记录警告。
    """
    # 使用 OpenAI 兼容 SDK 连接 DeepSeek，自定义地址和超时时间来自配置文件。
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
        timeout=config.get("timeout", 30),
        max_retries=0,
    )
    # papers 已按相关性排序，所以只处理列表最前面的 top_k 篇。
    for paper in papers[:top_k]:
        if not paper["abstract"]:
            logger.warning("Skipping summary without abstract: %s", paper["title"])
            continue
        try:
            summary = _request_summary(
                client,
                config,
                PROMPT.format(title=paper["title"], abstract=paper["abstract"]),
            )
            if summary_needs_rewrite(summary):
                logger.warning(
                    "Summary quality check requested one rewrite: %s", paper["title"]
                )
                summary = _request_summary(
                    client,
                    config,
                    REWRITE_PROMPT.format(
                        title=paper["title"],
                        abstract=paper["abstract"],
                        draft=summary,
                    ),
                )
            # 二次结果允许略微超出建议长度，但绝不再硬截断半句话。
            if len(summary) < 100 or not _summary_is_complete(summary):
                raise ValueError("summary remains incomplete after one rewrite")
            paper["ai_summary"] = format_summary(summary)
            logger.info("Generated summary: %s", paper["title"])
        except Exception as exc:
            logger.warning("Summary failed for %s: %s", paper["title"], exc)
