"""Filter, score, enrich, and historically deduplicate papers."""

# 本模块承担论文处理的核心规则：周时间窗、关键词筛选、相关性评分、期刊信息匹配和历史去重。

import json
import logging
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


def get_timezone(name: str) -> Any:
    """根据名称创建时区对象，确保所有日期都按北京时间等指定时区计算。"""
    # Python 3.9+ 优先使用标准库 zoneinfo；旧环境才回退到 pytz。
    try:
        from zoneinfo import ZoneInfo

        return ZoneInfo(name)
    except (ImportError, ModuleNotFoundError):
        import pytz

        return pytz.timezone(name)


def calculate_date_range(
    timezone_name: str, now: datetime = None
) -> Tuple[datetime, datetime]:
    """计算最近一个完整的“周一零点到下周一零点”检索区间。

    参数 timezone_name：时区名称；now：可选的当前时间，测试时可以传入固定值。
    返回值：(开始时间, 结束时间)，两者都带时区且固定相差七天。
    """
    timezone = get_timezone(timezone_name)
    local_now = now.astimezone(timezone) if now else datetime.now(timezone)
    # end 是最近一个周一零点，start 固定向前七天，因此不会随实际启动时间漂移。
    today = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = today - timedelta(days=today.weekday())
    start = end - timedelta(days=7)
    return start, end


def _matches(text: str, keywords: Sequence[str]) -> List[str]:
    """找出一段文字中出现的全部配置关键词，不区分英文字母大小写。"""
    # 使用不区分大小写的子串匹配，与配置中的英文短语直接对应。
    lowered = text.lower()
    return [keyword for keyword in keywords if keyword.lower() in lowered]


def attach_journal_metadata(
    paper: Dict[str, Any], journals: Sequence[Dict[str, Any]]
) -> None:
    """从 config.yaml 给论文补上影响因子和中科院分区。

    先按 ISSN 精确匹配，找不到再按期刊名匹配；配置本身为空时保留 None，报告显示“暂无配置”。
    """
    paper_issn = paper["journal_issn"].lower()
    paper_name = paper["journal_name"].lower()
    # ISSN 最可靠，优先精确匹配；找不到时再用期刊名称做宽松匹配。
    match = next(
        (item for item in journals if item["issn"].lower() == paper_issn), None
    )
    if match is None:
        match = next(
            (
                item
                for item in journals
                if item["name"].lower() in paper_name
                or paper_name in item["name"].lower()
            ),
            None,
        )
    if match:
        paper["if"] = match.get("if")
        paper["if_year"] = match.get("if_year")
        paper["rank"] = match.get("rank")
        paper["rank_year"] = match.get("rank_year")
        paper["rank_detail"] = match.get("rank_detail")
        paper["other_rank"] = match.get("other_rank")


def process_papers(
    papers: Sequence[Dict[str, Any]],
    topics: Sequence[str],
    exclusions: Sequence[str],
    journals: Sequence[Dict[str, Any]],
    logger: logging.Logger,
) -> List[Dict[str, Any]]:
    """完成论文筛选、评分、期刊指标补充和本轮去重。

    返回值只包含命中主题词、没有命中排除词的论文，并已按分数降序排列。
    """
    # 处理顺序很重要：排除词优先，然后才判断主题词、评分和本轮去重。
    processed: List[Dict[str, Any]] = []
    seen = set()
    for paper in papers:
        searchable = "{}\n{}".format(paper["title"], paper["abstract"])
        if _matches(searchable, exclusions):
            continue
        # 标题和摘要分别记录命中词，便于后续解释得分和确定报告分组。
        title_matches = _matches(paper["title"], topics)
        abstract_matches = _matches(paper["abstract"], topics)
        if not title_matches and not abstract_matches:
            continue
        unique_id = paper["doi"] or paper["openalex_id"]
        if not unique_id or unique_id in seen:
            continue
        seen.add(unique_id)
        paper["matched_topics_title"] = title_matches
        paper["matched_topics_abstract"] = abstract_matches
        # 标题命中权重更高：每个主题词 10 分；摘要命中每个主题词 3 分。
        paper["score"] = len(title_matches) * 10 + len(abstract_matches) * 3
        attach_journal_metadata(paper, journals)
        processed.append(paper)
    # 先按分数降序；同分时按 DOI/ID 排序，保证每次结果顺序一致。
    processed.sort(key=lambda paper: (-paper["score"], paper["doi"] or paper["openalex_id"]))
    logger.info("Keyword filtering retained %d of %d works", len(processed), len(papers))
    return processed


def load_history(path: Path, logger: logging.Logger) -> Dict[str, Any]:
    """读取 history.json；文件缺失或损坏时自动建立空历史并继续运行。"""
    # history.json 缺失或损坏时自动恢复为空历史，让任务可以继续执行。
    try:
        with path.open("r", encoding="utf-8") as stream:
            history = json.load(stream)
        if not isinstance(history.get("dois"), list):
            raise ValueError("dois must be a list")
        return history
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        logger.warning("Resetting unavailable or corrupted history: %s", exc)
        history = {"dois": [], "last_updated": None}
        save_history(path, history)
        return history


def remove_historical(
    papers: Sequence[Dict[str, Any]], history: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """删除已经推送过的论文，只返回历史记录中从未出现的新论文。"""
    known = set(history.get("dois", []))
    return [
        paper
        for paper in papers
        if (paper["doi"] or paper["openalex_id"]) not in known
    ]


def save_history(path: Path, history: Dict[str, Any]) -> None:
    """用原子替换方式保存历史，避免中途异常把 history.json 写坏。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    # 先写同目录临时文件，再用 os.replace 一次性替换，防止中途断电留下半个 JSON。
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name, suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(history, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary_name, str(path))
    except BaseException:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def record_papers(
    path: Path,
    history: Dict[str, Any],
    papers: Sequence[Dict[str, Any]],
    timestamp: datetime,
) -> None:
    """把本批论文 DOI（无 DOI 时用 OpenAlex ID）加入历史并立即保存。"""
    # 在翻译、摘要和邮件之前落盘，确保后续失败时也不会重复记录同一批论文。
    identifiers = history.setdefault("dois", [])
    known = set(identifiers)
    for paper in papers:
        unique_id = paper["doi"] or paper["openalex_id"]
        if unique_id and unique_id not in known:
            identifiers.append(unique_id)
            known.add(unique_id)
    history["last_updated"] = timestamp.isoformat()
    save_history(path, history)
