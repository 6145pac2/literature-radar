"""Load and validate project configuration."""

# 本模块只负责一件事：读取项目根目录的 config.yaml，并检查必填板块是否存在。
# 其他模块统一从 CONFIG 取配置，避免在不同文件里重复填写参数。

import os
from pathlib import Path
from typing import Any, Dict

import yaml


# 根据当前文件位置推导项目根目录，保证从本地或 GitHub Actions 启动都能找到配置。
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"

# 配置文件只保存非敏感设置；真实凭据由本机环境变量或 GitHub Secrets 提供。
SECRET_ENV_VARS = {
    ("email", "authorization_code"): "EMAIL_AUTHORIZATION_CODE",
    ("openalex", "api_key"): "OPENALEX_API_KEY",
    ("deepseek", "api_key"): "DEEPSEEK_API_KEY",
}


class ConfigError(RuntimeError):
    """配置文件无法读取或缺少必要内容时使用的专用错误类型。"""


def load_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    """读取并检查 config.yaml。

    参数 path：配置文件路径；不传时使用项目根目录下的 config.yaml。
    返回值：Python 字典形式的全部配置，其他模块会从这里取邮箱、密钥和关键词等信息。
    读取失败或必填板块缺失时抛出 ConfigError，让主程序用退出码 2 停止。
    """
    try:
        with path.open("r", encoding="utf-8") as stream:
            config = yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigError("Unable to load config.yaml: {}".format(exc)) from exc

    # 先检查顶层配置，再检查最基本的关键词和期刊列表，尽早发现配置错误。
    required = {"email", "openalex", "deepseek", "keywords", "journals", "system"}
    if not isinstance(config, dict) or not required.issubset(config):
        raise ConfigError("config.yaml is missing one or more required sections")
    if not config["keywords"].get("topics") or not config["journals"]:
        raise ConfigError("At least one topic and one journal must be configured")

    # 强制覆盖配置文件中的凭据字段，防止以后误把密码重新写进 config.yaml。
    missing = []
    for (section, key), environment_name in SECRET_ENV_VARS.items():
        value = os.environ.get(environment_name, "").strip()
        config[section][key] = value
        if not value:
            missing.append(environment_name)
    if missing:
        raise ConfigError(
            "Missing required environment variables: {}".format(", ".join(missing))
        )
    return config


# 导入本模块时加载一次，供整个程序共享。
CONFIG = load_config()
