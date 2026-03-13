"""Cognitive Layer Integration - NeuroState クライアントラッパー

NeuroState MCP サーバーの Python API を直接呼び出すクライアント。
MCP プロトコル経由にする場合はこのモジュールのみ差し替える。
"""

import sys
import os
import logging
from typing import Any

from cognitive_layer.models import NeuroStateNormalized

logger = logging.getLogger(__name__)

# NeuroState エンジンのパスを追加（standalone 動作用）
_NEUROSTATE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "neurostate-engine"
)
sys.path.insert(0, os.path.abspath(_NEUROSTATE_PATH))

try:
    from core.state_model import NeuroState
    from core.update_engine import (
        compute_next_neuro_state,
        evaluate_ethics_gate,
        event_to_power,
    )
    _NEUROSTATE_AVAILABLE = True
except ImportError:
    logger.warning(
        "neurostate-engine が見つかりません。スタブモードで動作します。\n"
        "期待パス: %s", _NEUROSTATE_PATH
    )
    _NEUROSTATE_AVAILABLE = False


class NeuroStateClient:
    """NeuroState エンジンへのアクセスを提供するクライアント。"""

    def __init__(self, user_id: str = "default") -> None:
        self.user_id = user_id
        if _NEUROSTATE_AVAILABLE:
            self._state = NeuroState(D=50, S=50, C=50, O=20, G=50, E=50, corruption=0)
        else:
            self._state = None

    def get_state(self) -> NeuroStateNormalized:
        """現在の NeuroState を正規化して返す。"""
        if self._state is None:
            logger.debug("スタブ: デフォルト NeuroState を返します")
            return NeuroStateNormalized()
        return NeuroStateNormalized.from_raw(self._state.to_dict())

    def stimulate(self, event_type: str, power: float = 1.0) -> NeuroStateNormalized:
        """
        イベントで NeuroState を更新し、新しい状態を返す。

        Args:
            event_type: praise / criticism / bonding / stress / relaxation
            power: 刺激強度 (0.1〜10.0)
        """
        if self._state is None:
            logger.debug("スタブ: stimulate をスキップします (event=%s)", event_type)
            return NeuroStateNormalized()

        ethics = evaluate_ethics_gate(self._state)
        if ethics.status == "BLOCK" and event_type != "relaxation":
            logger.warning(
                "EthicsGate BLOCK のため更新スキップ (reason=%s)", ethics.reason
            )
            return NeuroStateNormalized.from_raw(self._state.to_dict())

        try:
            input_power = event_to_power(event_type, power)
        except ValueError as e:
            raise ValueError(f"不正なイベントタイプ: {event_type}") from e

        self._state = compute_next_neuro_state(self._state, input_power)
        return NeuroStateNormalized.from_raw(self._state.to_dict())

    def reset(self) -> None:
        """NeuroState を初期値にリセットする。"""
        if _NEUROSTATE_AVAILABLE:
            self._state = NeuroState(D=50, S=50, C=50, O=20, G=50, E=50, corruption=0)
        logger.info("NeuroState をリセットしました (user=%s)", self.user_id)

    def raw_dict(self) -> dict[str, Any]:
        """生の NeuroState 値（0-100）を辞書で返す。デバッグ用。"""
        if self._state is None:
            return {}
        return self._state.to_dict()
