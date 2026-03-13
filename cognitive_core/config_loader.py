"""Cognitive Layer Integration - 設定ローダー"""

import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    logger.warning("PyYAML が見つかりません。デフォルト設定で動作します。pip install pyyaml")
    _YAML_AVAILABLE = False


@dataclass
class StateToBiasRule:
    """state_to_bias_rules の1エントリ"""
    if_key: str
    operator: str   # ">" / "<" / ">=" / "<="
    threshold: float
    adjust: dict[str, float] = field(default_factory=dict)

    def matches(self, value: float) -> bool:
        ops = {
            ">": value > self.threshold,
            "<": value < self.threshold,
            ">=": value >= self.threshold,
            "<=": value <= self.threshold,
        }
        return ops.get(self.operator, False)


@dataclass
class PolicyRule:
    """policy_rules の1エントリ"""
    based_on: str
    source: str   # "state" or "bias"
    affects: str
    weight: float


@dataclass
class CognitiveConfig:
    neurostate_defaults: dict[str, float] = field(default_factory=lambda: {
        "D": 50, "S": 50, "C": 50, "O": 20, "G": 50, "E": 50, "corruption": 0
    })
    bias_limits: dict[str, float] = field(default_factory=lambda: {
        "default_min": 0.0, "default_max": 1.0
    })
    state_to_bias_rules: list[StateToBiasRule] = field(default_factory=list)
    policy_rules: list[PolicyRule] = field(default_factory=list)


_DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_config(path: Path | str | None = None) -> CognitiveConfig:
    """
    config.yaml を読み込み CognitiveConfig を返す。
    ファイルが存在しないか yaml が利用不可の場合はデフォルトを返す。
    """
    config_path = Path(path) if path else _DEFAULT_CONFIG_PATH

    if not _YAML_AVAILABLE or not config_path.exists():
        logger.info("デフォルト設定を使用します (path=%s)", config_path)
        return CognitiveConfig()

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("config.yaml の読み込みに失敗しました: %s", e)
        return CognitiveConfig()

    state_rules = [
        StateToBiasRule(
            if_key=r["if_key"],
            operator=r["operator"],
            threshold=float(r["threshold"]),
            adjust={k: float(v) for k, v in r.get("adjust", {}).items()},
        )
        for r in raw.get("state_to_bias_rules", [])
    ]

    policy_rules = [
        PolicyRule(
            based_on=r["based_on"],
            source=r["source"],
            affects=r["affects"],
            weight=float(r["weight"]),
        )
        for r in raw.get("policy_rules", [])
    ]

    return CognitiveConfig(
        neurostate_defaults=raw.get("neurostate_defaults", {}),
        bias_limits=raw.get("bias_limits", {}),
        state_to_bias_rules=state_rules,
        policy_rules=policy_rules,
    )
