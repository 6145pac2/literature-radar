"""Orchestrate the complete weekly literature radar run."""

# 这是程序总入口，按照“加载配置 → 检索 → 处理 → 记历史 → 生成内容 → 发邮件”的顺序调度模块。

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def setup_logging(logs_dir: Path, now: datetime) -> logging.Logger:
    """建立同时输出到屏幕和日志文件的记录器，并返回给主流程使用。"""
    # 同一条日志同时写入文件和控制台，便于本地排错及查看 GitHub Actions 输出。
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("literature_radar")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler(
        logs_dir / "run_{}.log".format(now.strftime("%Y-%m-%d")),
        encoding="utf-8",
    )
    console_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def run() -> int:
    """按顺序执行一次完整文献雷达任务。

    返回 0 表示成功；1 表示邮件失败；2 表示配置或依赖加载失败；99 表示其他意外错误。
    这是 src/main.py 中最重要的总调度函数，各功能细节由其他模块完成。
    """
    # 第一板块：导入配置和功能模块。这里失败统一返回配置错误码 2。
    try:
        from config import CONFIG, PROJECT_ROOT
        from ai_summarizer import summarize_top_papers
        from email_sender import send_report
        from openalex_client import OpenAlexClient
        from paper_processor import (
            calculate_date_range,
            get_timezone,
            load_history,
            process_papers,
            record_papers,
            remove_historical,
        )
        from report_generator import (
            generate_report,
            markdown_to_plain_text,
            rebuild_index,
        )
        from translator import translate_titles
    except Exception as exc:
        print("{} [ERROR] Configuration or dependency loading failed: {}".format(
            datetime.now().isoformat(timespec="seconds"), exc
        ))
        return 2

    # 第二板块：建立北京时间日志，并计算上一个完整周的时间范围。
    timezone = get_timezone(CONFIG["system"]["timezone"])
    retrieved_at = datetime.now(timezone)
    logger = setup_logging(PROJECT_ROOT / "logs", retrieved_at)
    try:
        start, end = calculate_date_range(CONFIG["system"]["timezone"], retrieved_at)
        logger.info("Starting literature run for [%s, %s)", start.date(), end.date())

        # 第三板块：从所有白名单期刊检索原始论文。
        raw_papers = OpenAlexClient(CONFIG["openalex"], logger).fetch_all(
            CONFIG["journals"], start, end
        )
        # 第四板块：排除无关论文，计算相关性得分并补充期刊指标。
        papers = process_papers(
            raw_papers,
            CONFIG["keywords"]["topics"],
            CONFIG["keywords"].get("exclude", []),
            CONFIG["journals"],
            logger,
        )

        # 第五板块：过滤历史记录，并在调用外部内容服务前立即保存本批论文 ID。
        history_path = PROJECT_ROOT / "history.json"
        history = load_history(history_path, logger)
        papers = remove_historical(papers, history)
        logger.info("Historical deduplication retained %d new papers", len(papers))
        record_papers(history_path, history, papers, retrieved_at)
        logger.info("History persisted before report delivery")

        # 第六板块：翻译所有标题，并为得分最高且有摘要的论文生成中文 AI 摘要。
        translate_titles(papers, logger)
        summarize_top_papers(
            papers,
            int(CONFIG["system"].get("top_k_summaries", 10)),
            CONFIG["deepseek"],
            logger,
        )
        # 第七板块：生成 Markdown 周报，同时完整重建 GitHub Pages 索引。
        report_path = generate_report(
            papers,
            CONFIG["keywords"]["topics"],
            CONFIG["keywords"].get("exclude", []),
            start,
            end,
            retrieved_at,
            PROJECT_ROOT / "reports",
        )
        rebuild_index(PROJECT_ROOT / "reports", PROJECT_ROOT / "index.html")
        logger.info("Generated report and rebuilt archive index: %s", report_path)

        # 第八板块：发送邮件。邮件是关键步骤，失败时明确返回退出码 1。
        try:
            send_report(
                CONFIG["email"],
                report_path,
                markdown_to_plain_text(report_path.read_text(encoding="utf-8")),
                end.strftime("%Y-%m-%d"),
                report_path.with_suffix(".html").read_text(encoding="utf-8"),
            )
        except Exception as exc:
            logger.error("Email sending failed: %s", exc)
            return 1
        logger.info("Email sent successfully")
        logger.info("Run completed; GitHub Actions will commit generated files")
        return 0
    # 未被单独处理的异常统一记录完整堆栈，并返回退出码 99。
    except Exception:
        logger.exception("Unexpected literature radar failure")
        return 99


if __name__ == "__main__":
    sys.exit(run())
