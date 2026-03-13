"""Cognitive Layer Integration - ポリシーマッパー

NeuroState + Bias の値から Policy オブジェクトを生成する。
マッピングルールは config.yaml から読み込む。
"""

import logging
from dataclasses import fields

from cognitive_core.models import NeuroStateNormalized, Policy
from cognitive_core.config_loader import CognitiveConfig, PolicyRule

logger = logging.getLogger(__name__)

# Policy フィールド名の集合（不正なフィールドへのアクセスを防ぐ）
_POLICY_FIELDS = {f.name for f in fields(Policy)}


def _get_state_value(state: NeuroStateNormalized, key: str) -> float | None:
    return getattr(state, key, None)


def _get_bias_value(biases: dict[str, float], key: str) -> float | None:
    return biases.get(key)


def _apply_rule(
    policy_values: dict[str, float],
    rule: PolicyRule,
    state: NeuroStateNormalized,
    biases: dict[str, float],
) -> None:
    """1つの policy_rule を policy_values に適用する（イミュータブルパターン）。"""
    if rule.affects not in _POLICY_FIELDS:
        logger.warning("不正な policy フィールド: %s（スキップ）", rule.affects)
        return

    if rule.source == "state":
        source_value = _get_state_value(state, rule.based_on)
    elif rule.source == "bias":
        source_value = _get_bias_value(biases, rule.based_on)
    else:
        logger.warning("不正な source: %s（スキップ）", rule.source)
        return

    if source_value is None:
        return

    contribution = source_value * rule.weight
    policy_values[rule.affects] = policy_values[rule.affects] + contribution


def compute_policy(
    state: NeuroStateNormalized,
    biases: dict[str, float],
    config: CognitiveConfig,
) -> Policy:
    """
    NeuroState と Bias から Policy を計算する。

    各 policy フィールドは 0.5 をベースラインとし、
    ルールの寄与を加算したうえで 0.0〜1.0 にクランプする。
    """
    # ベースライン: 全フィールドを 0.5 で初期化
    policy_values: dict[str, float] = {f.name: 0.5 for f in fields(Policy)}

    for rule in config.policy_rules:
        _apply_rule(policy_values, rule, state, biases)

    # クランプ
    clamped = {k: max(0.0, min(1.0, v)) for k, v in policy_values.items()}

    return Policy(**clamped)
