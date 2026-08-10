"""Translate paper titles while allowing graceful network failures."""

# 本模块只翻译标题。翻译服务不可用时保留英文标题，不影响整份周报继续生成。

import logging
from typing import Any, Dict, List

from deep_translator import GoogleTranslator


def translate_titles(
    papers: List[Dict[str, Any]], logger: logging.Logger
) -> None:
    """逐篇翻译论文标题，并直接写回每篇论文的 title_zh 字段。

    参数 papers 是论文列表，logger 用于记录成功或失败信息。
    没有返回值；翻译失败时保留英文原题，确保单篇失败不会终止整份周报。
    """
    # 一个运行周期复用同一个翻译器实例，逐篇写回 title_zh 字段。
    translator = GoogleTranslator(source="auto", target="zh-CN")
    for paper in papers:
        try:
            paper["title_zh"] = translator.translate(paper["title"])
            logger.info("Translated title: %s", paper["title"])
        except Exception as exc:
            paper["title_zh"] = paper["title"]
            logger.warning("Title translation failed for %s: %s", paper["title"], exc)
