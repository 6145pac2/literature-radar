"""Send the weekly report through an SSL SMTP connection."""

# 本模块负责组装邮件：正文使用易读纯文本，同时附上原始 Markdown 周报。

import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict


def send_report(
    config: Dict[str, Any],
    report_path: Path,
    body: str,
    report_date: str,
    html_body: str = "",
) -> None:
    """通过 QQ SMTP 发送周报邮件。

    config 提供邮箱连接信息；report_path 是要附加的 Markdown 文件；body 是纯文本正文；
    report_date 用于邮件标题；html_body 是带加粗和卡片样式的富文本正文。
    没有返回值；登录或发送失败会抛出异常，由 main.py 转换成退出码 1。
    """
    # EmailMessage 会自动处理 UTF-8 标题、正文和附件编码。
    message = EmailMessage()
    message["From"] = config["sender"]
    message["To"] = config["receiver"]
    message["Subject"] = "📅 本周文献雷达周报 {}".format(report_date)
    message.set_content(body, charset="utf-8")
    if html_body:
        # 支持 HTML 的邮箱显示加粗期刊和卡片排版，不支持时自动回退到上面的纯文本。
        message.add_alternative(html_body, subtype="html")
    message.add_attachment(
        report_path.read_bytes(),
        maintype="text",
        subtype="markdown",
        filename=report_path.name,
    )
    # QQ 邮箱 465 端口使用 SMTP_SSL；with 结束时会自动关闭连接。
    with smtplib.SMTP_SSL(
        config["smtp_server"],
        int(config["smtp_port"]),
        timeout=config.get("timeout", 30),
    ) as server:
        server.login(config["sender"], config["authorization_code"])
        server.send_message(message)
