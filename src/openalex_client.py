"""Retrieve journal articles from the OpenAlex REST API."""

# 本模块负责连接 OpenAlex、分页获取论文，并把接口返回值整理成统一的 Paper 字典。
# 它不做关键词筛选和历史去重，那些工作交给 paper_processor.py。

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests


def parse_abstract_inverted_index(inverted_index: Dict[str, List[int]]) -> str:
    """把 OpenAlex 的“倒排索引摘要”还原成正常阅读顺序的摘要。

    参数 inverted_index：单词和它在摘要中出现位置的对应表。
    返回值：按位置重新排列后的完整摘要；没有摘要时返回空字符串。
    """
    if not inverted_index:
        return ""
    # OpenAlex 保存的是“单词 -> 出现位置”，这里按位置重新排回正常句子。
    positioned_words = [
        (position, word)
        for word, positions in inverted_index.items()
        for position in positions
    ]
    return " ".join(word for _, word in sorted(positioned_words))


def normalize_doi(value: Optional[str]) -> str:
    """把不同写法的 DOI 统一成小写的标准值，方便准确去重。

    例如 https://doi.org/10.X/ABC 会变成 10.x/abc；没有 DOI 时返回空字符串。
    """
    if not value:
        return ""
    value = value.strip()
    # 去掉 DOI URL 前缀并转成小写，确保同一 DOI 能被稳定去重。
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.lower().startswith(prefix):
            value = value[len(prefix) :]
            break
    return value.lower()


def _paper_from_work(work: Dict[str, Any]) -> Dict[str, Any]:
    """把 OpenAlex 返回的一条原始记录整理成本项目统一使用的 Paper 字典。

    输入是接口原始数据，输出包含 DOI、标题、摘要、作者、期刊和后续处理所需的空字段。
    统一格式后，筛选、翻译和报告模块就不必理解 OpenAlex 复杂的嵌套结构。
    """
    # OpenAlex 的字段嵌套较深，先安全地取出期刊来源信息。
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    issns = source.get("issn") or []
    return {
        "doi": normalize_doi(work.get("doi")),
        "openalex_id": work.get("id") or "",
        "title": work.get("title") or "Untitled",
        "title_zh": work.get("title") or "Untitled",
        "abstract": parse_abstract_inverted_index(work.get("abstract_inverted_index") or {}),
        "authors": [
            item.get("author", {}).get("display_name", "")
            for item in work.get("authorships", [])
            if item.get("author", {}).get("display_name")
        ],
        "journal_name": source.get("display_name") or "Unknown journal",
        "journal_issn": source.get("issn_l") or (issns[0] if issns else ""),
        "publication_date": work.get("publication_date") or "",
        "if": None,
        "if_year": None,
        "rank": None,
        "rank_year": None,
        "rank_detail": None,
        "other_rank": None,
        "score": 0,
        "matched_topics_title": [],
        "matched_topics_abstract": [],
        "ai_summary": None,
    }


class OpenAlexClient:
    """负责向 OpenAlex 分页请求论文，并在临时网络错误时自动重试。"""

    def __init__(self, config: Dict[str, Any], logger: logging.Logger) -> None:
        """保存接口地址、API Key 和日志工具，为后续请求做准备。"""
        self.base_url = config["base_url"]
        self.api_key = config["api_key"]
        self.logger = logger
        self.session = requests.Session()

    def _get_page(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """请求一页 OpenAlex 数据；最多重试三次，仍失败则返回 None。"""
        # 单页最多尝试三次，等待时间依次为 1 秒、2 秒，第三次失败后放弃该期刊。
        for attempt in range(1, 4):
            try:
                response = self.session.get(
                    self.base_url,
                    params=params,
                    timeout=(5, 30),
                )
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, ValueError) as exc:
                self.logger.warning(
                    "OpenAlex attempt %d/3 failed: %s", attempt, type(exc).__name__
                )
                if attempt < 3:
                    time.sleep(2 ** (attempt - 1))
        return None

    def fetch_journal(
        self, issn: str, journal_name: str, start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """获取一个期刊在 [start, end) 时间范围内的全部论文。

        方括号表示包含 start，圆括号表示不包含 end，这样相邻两周不会重复。
        函数会自动翻页，并返回统一 Paper 字典组成的列表。
        """
        # API 端先限制日期和 ISSN，本地端再检查一次右侧开区间，避免边界重复。
        papers: List[Dict[str, Any]] = []
        page = 1
        while True:
            params = {
                "filter": (
                    "primary_location.source.issn:{},from_publication_date:{},"
                    "to_publication_date:{}"
                ).format(
                    issn,
                    start.strftime("%Y-%m-%d"),
                    (end - timedelta(days=1)).strftime("%Y-%m-%d"),
                ),
                "api_key": self.api_key,
                "per_page": 50,
                "page": page,
            }
            self.logger.info("Querying OpenAlex: %s page %d", journal_name, page)
            payload = self._get_page(params)
            if payload is None:
                self.logger.error("Skipping journal after retries: %s", journal_name)
                break
            results = payload.get("results") or []
            # 把当前页每条记录转换为统一结构，并只保留 [start, end) 范围。
            for work in results:
                paper = _paper_from_work(work)
                publication_date = paper["publication_date"]
                if publication_date and start.date() <= datetime.strptime(
                    publication_date, "%Y-%m-%d"
                ).date() < end.date():
                    papers.append(paper)
            # 不满 50 条表示已经到最后一页。
            if len(results) < 50:
                break
            page += 1
        self.logger.info("Retrieved %d dated works from %s", len(papers), journal_name)
        return papers

    def fetch_all(
        self, journals: List[Dict[str, Any]], start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """依次检索配置中的全部白名单期刊，并把论文合并成一个列表。"""
        # 逐个查询白名单期刊；单个期刊失败不会阻断其他期刊。
        papers: List[Dict[str, Any]] = []
        for journal in journals:
            papers.extend(
                self.fetch_journal(journal["issn"], journal["name"], start, end)
            )
        return papers
