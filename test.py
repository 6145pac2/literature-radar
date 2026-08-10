"""Run live configuration checks before deploying the literature radar."""

# 这是部署前的真实连通性检查：只验证服务，不执行完整周报任务，也不会发送邮件。

import json
import smtplib
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Tuple

import requests
from openai import OpenAI

from src.config import CONFIG, PROJECT_ROOT
from src.report_generator import generate_report, rebuild_index


def test_smtp() -> None:
    """测试能否连接并登录 QQ 邮箱；只验证身份，不发送邮件。"""
    # 只登录 QQ SMTP，成功后立即断开，不发送任何内容。
    config = CONFIG["email"]
    with smtplib.SMTP_SSL(
        config["smtp_server"], int(config["smtp_port"]), timeout=10
    ) as server:
        server.login(config["sender"], config["authorization_code"])


def test_openalex() -> None:
    """用 Nature 做一次最小查询，确认 OpenAlex 地址、密钥和网络可用。"""
    # 用 Nature ISSN 请求一条记录，确认地址、密钥和网络均可用。
    config = CONFIG["openalex"]
    response = requests.get(
        config["base_url"],
        params={
            "filter": "primary_location.source.issn:0028-0836",
            "api_key": config["api_key"],
            "per_page": 1,
        },
        timeout=(5, 10),
    )
    response.raise_for_status()
    if not response.json().get("results"):
        raise RuntimeError("OpenAlex returned no Nature papers")


def test_deepseek() -> None:
    """发送一句很短的测试问题，确认 DeepSeek 密钥、模型和余额可用。"""
    # 发送很短的提示词，确认 DeepSeek 密钥、余额、模型和接口地址有效。
    config = CONFIG["deepseek"]
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
        timeout=10,
        max_retries=0,
    )
    response = client.chat.completions.create(
        model=config["model"],
        messages=[
            {
                "role": "user",
                "content": "Hello, please respond with 'API is working' in Chinese.",
            }
        ],
        max_tokens=30,
        temperature=0,
    )
    answer = response.choices[0].message.content or ""
    if "API" not in answer and "工作" not in answer:
        raise RuntimeError("Unexpected DeepSeek response: {}".format(answer))


def test_directories() -> None:
    """确认 reports 和 logs 目录能够创建文件，避免运行时因权限失败。"""
    # 在输出目录创建临时文件，退出 with 后自动删除，不留下测试垃圾。
    for name in ("reports", "logs"):
        directory = PROJECT_ROOT / name
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=str(directory)):
            pass


def test_history() -> None:
    """确认 history.json 存在、能读取，并且 dois 字段是列表。"""
    # 文件不存在时建立空历史；存在时验证 dois 必须是列表。
    path = PROJECT_ROOT / "history.json"
    if not path.exists():
        path.write_text('{"dois": [], "last_updated": null}\n', encoding="utf-8")
    with path.open("r", encoding="utf-8") as stream:
        history = json.load(stream)
    if not isinstance(history.get("dois"), list):
        raise RuntimeError("history.json must contain a dois list")


def test_web_archive() -> None:
    """用临时数据验证期号、篇数、关键词、HTML 页面和 DOI 链接。"""
    # 使用临时文件验证网页生成逻辑，不读取或修改真实周报。
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        reports = root / "reports"
        topics = [
            "hydrothermal liquefaction",
            "biocrude",
            "waste valorization",
            "microalgae",
            "biochar",
            "biorefinery",
        ]
        report = generate_report(
            [
                {
                    "doi": "10.1000/test",
                    "openalex_id": "W1",
                    "title": "Example paper",
                    "title_zh": "示例论文",
                    "abstract": "",
                    "authors": ["Author"],
                    "journal_name": "Example Journal",
                    "journal_issn": "0000-0000",
                    "publication_date": "2026-08-04",
                    "if": 1.0,
                    "rank": "1区",
                    "score": 10,
                    "matched_topics_title": ["biochar"],
                    "matched_topics_abstract": [],
                    "ai_summary": None,
                }
            ],
            topics,
            ["medical"],
            datetime(2026, 8, 3),
            datetime(2026, 8, 10),
            datetime(2026, 8, 10, 9, 30),
            reports,
        )
        index = root / "index.html"
        rebuild_index(reports, index)
        index_text = index.read_text(encoding="utf-8")
        markdown_text = report.read_text(encoding="utf-8")
        report_text = (reports / "weekly_report_2026-08-10.html").read_text(
            encoding="utf-8"
        )
        if "第 1 期" not in index_text or "共 1 篇" not in index_text:
            raise RuntimeError("archive metadata is missing")
        if (
            "主题关键词：" not in markdown_text
            or "排除关键词：medical" not in markdown_text
            or "理论总分78分" not in markdown_text
        ):
            raise RuntimeError("report keyword scope is missing")
        if (
            "返回历史周报" not in report_text
            or "https://doi.org/10.1000/test" not in report_text
            or "<strong>Example Journal</strong>" not in report_text
            or "相关性得分: 10/78" not in report_text
        ):
            raise RuntimeError("styled report page is incomplete")


def main() -> int:
    """运行全部检查；全部 PASS 返回 0，只要有一项 FAIL 就返回 1。"""
    # 顺序执行所有检查，让用户一次看到全部 PASS/FAIL，而不是首错即停。
    tests: List[Tuple[str, Callable[[], None]]] = [
        ("SMTP connection", test_smtp),
        ("OpenAlex API", test_openalex),
        ("DeepSeek API", test_deepseek),
        ("Directory permissions", test_directories),
        ("history.json", test_history),
        ("Web archive rendering", test_web_archive),
    ]
    failures = 0
    for name, check in tests:
        try:
            check()
            print("PASS - {}".format(name))
        except Exception as exc:
            failures += 1
            print("FAIL - {}: {}".format(name, exc))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
