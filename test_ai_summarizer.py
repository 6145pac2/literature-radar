"""Run small offline checks for AI summary quality rules."""

from src.ai_summarizer import clean_summary, format_summary, summary_needs_rewrite


def main() -> None:
    """Verify that complete summaries pass and interrupted summaries are rejected."""
    complete = (
        "研究目的：本研究面向有机废物资源化难题，评估目标工艺的应用潜力与限制。"
        "研究方法：研究通过批次实验和连续反应器实验比较不同操作条件，并结合微生物"
        "群落分析解释过程变化。关键结果：优化条件使目标产物产量提高46%，水解效率为"
        "8%至26%，说明水解仍是限制步骤；各项数值和单位均得到完整保留。主要结论："
        "该工艺具有进一步开发价值，为复杂有机废物的减量化和资源化提供了实验依据，"
        "但后续研究仍需提高水解效率，并在更大规模设备中验证长期运行稳定性与经济性。"
        "研究还提示，评价资源化工艺时不能只关注单一产物产率，还应同时考虑能量投入、"
        "副产物去向、进料波动和反应器连续运行能力，以避免实验室条件下的最优结果在工程"
        "放大后失效。现有结果为后续优化提供了明确方向，也界定了当前结论可以支持的范围，"
        "便于读者快速判断该论文是否与自己的研究问题和技术路线相关。摘要同时保留了研究"
        "对象、操作条件、对照关系和主要限制，避免只给出缺少证据支持的笼统结论。"
    )
    assert len(complete) >= 200
    assert not summary_needs_rewrite(complete)
    assert summary_needs_rewrite(complete[:-1])
    assert summary_needs_rewrite(complete[:-1] + "19....")
    assert summary_needs_rewrite(complete.replace("研究目的：", "", 1))
    assert clean_summary("**研究目的：**  测试") == "研究目的： 测试"
    formatted = format_summary(complete)
    assert formatted.count("\n") == 3
    assert formatted.startswith("**研究目的**：")
    assert "\n**研究方法**：" in formatted
    assert "\n**关键结果**：" in formatted
    assert "\n**主要结论**：" in formatted
    print("PASS - AI summary quality rules")


if __name__ == "__main__":
    main()
