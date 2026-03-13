"""Cognitive Layer Integration - オーケストレーター

NeuroState MCP と Bias Engine MCP を協調させる統合レイヤー。
このモジュールが認知レイヤーの「司令塔」。

責務:
    1. NeuroState を取得する
    2. state_to_bias_rules に従って Bias を調整する
    3. Policy を計算する
    4. CognitionSnapshot として返す（デバッグ・観測可能）

結合ルール:
    - NeuroState ↔ Bias 間の直接結合はここにのみ存在する
    - 両 MCP サーバー本体はお互いを知らない
"""

import logging
from pathlib import Path

from cognitive_layer.models import NeuroStateNormalized, CognitionSnapshot
from cognitive_layer.neurostate_client import NeuroStateClient
from cognitive_layer.bias_engine_client import BiasEngineClient
from cognitive_layer.policy_mapper import compute_policy
from cognitive_layer.config_loader import load_config, CognitiveConfig

logger = logging.getLogger(__name__)


class CognitiveIntegration:
    """NeuroState × Bias Engine の統合オーケストレーター。"""

    def __init__(
        self,
        user_id: str = "default",
        config_path: Path | str | None = None,
        persist_biases: bool = False,
    ) -> None:
        self._config: CognitiveConfig = load_config(config_path)
        self._neurostate = NeuroStateClient(user_id=user_id)
        self._bias_engine = BiasEngineClient(persist=persist_biases)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def update(self, event_type: str, power: float = 1.0) -> CognitionSnapshot:
        """
        イベントで NeuroState を更新し、Bias と Policy を再計算して
        CognitionSnapshot を返す。

        Args:
            event_type: praise / criticism / bonding / stress / relaxation
            power: 刺激強度 (0.1〜10.0)
        """
        state = self._neurostate.stimulate(event_type, power)
        return self._sync(state)

    def snapshot(self) -> CognitionSnapshot:
        """現在の状態をそのまま CognitionSnapshot として返す（更新なし）。"""
        state = self._neurostate.get_state()
        return self._sync(state)

    def reset(self) -> CognitionSnapshot:
        """NeuroState と Bias を両方リセットして初期 snapshot を返す。"""
        self._neurostate.reset()
        self._bias_engine.reset_biases()
        return self.snapshot()

    def set_bias_override(self, name: str, weight: float) -> None:
        """外部から直接バイアスを上書きする（テスト・手動調整用）。"""
        self._bias_engine.set_bias(name, weight)

    def activate_preset(self, preset_name: str) -> CognitionSnapshot:
        """Bias プリセットを適用して snapshot を返す。"""
        self._bias_engine.activate_preset(preset_name)
        return self.snapshot()

    # ------------------------------------------------------------------ #
    # Internal
    # ------------------------------------------------------------------ #

    def _sync(self, state: NeuroStateNormalized) -> CognitionSnapshot:
        """
        state_to_bias_rules を適用して Bias を調整し、
        Policy を計算して CognitionSnapshot を返す。
        """
        self._apply_state_to_bias(state)
        biases = self._bias_engine.get_biases()
        policy = compute_policy(state, biases, self._config)
        return CognitionSnapshot(state=state, biases=biases, policy=policy)

    def _apply_state_to_bias(self, state: NeuroStateNormalized) -> None:
        """
        config.yaml の state_to_bias_rules を評価し、
        条件を満たすルールのバイアス delta を Bias Engine に適用する。
        """
        for rule in self._config.state_to_bias_rules:
            current_value = getattr(state, rule.if_key, None)
            if current_value is None:
                logger.warning("不正な NeuroState キー: %s（スキップ）", rule.if_key)
                continue

            if rule.matches(current_value):
                logger.debug(
                    "ルール適用: %s %s %.2f (値=%.2f) → %s",
                    rule.if_key, rule.operator, rule.threshold,
                    current_value, rule.adjust,
                )
                for bias_name, delta in rule.adjust.items():
                    self._bias_engine.adjust_bias(bias_name, delta)
