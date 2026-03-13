"""Cognitive Layer Integration - Bias Engine クライアントラッパー

Bias Engine MCP の Python API を直接呼び出すクライアント。
MCP プロトコル経由にする場合はこのモジュールのみ差し替える。
"""

import sys
import logging
import os

logger = logging.getLogger(__name__)

_BIAS_ENGINE_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "bias-engine-mcp")
)

# bias-engine-mcp を sys.path の先頭に挿入してから import する。
# cognitive-layer 自身の cognitive_core/ は "core" という名前を持たないため競合しない。
if _BIAS_ENGINE_ROOT not in sys.path:
    sys.path.insert(0, _BIAS_ENGINE_ROOT)

try:
    from bias_core.bias_engine import BiasEngine  # noqa: E402 (intentional late import)
    _BIAS_ENGINE_AVAILABLE = True
except Exception as e:
    logger.warning(
        "bias-engine-mcp が見つかりません。スタブモードで動作します。\n"
        "期待パス: %s\n理由: %s", _BIAS_ENGINE_ROOT, e
    )
    _BIAS_ENGINE_AVAILABLE = False


class BiasEngineClient:
    """Bias Engine へのアクセスを提供するクライアント。"""

    def __init__(self, persist: bool = False) -> None:
        if _BIAS_ENGINE_AVAILABLE:
            self._engine = BiasEngine(persist=persist)
        else:
            self._engine = None
            self._stub_biases: dict[str, float] = {}

    def get_biases(self) -> dict[str, float]:
        """アクティブなバイアスと重みを返す。"""
        if self._engine is None:
            return dict(self._stub_biases)
        return self._engine.get_biases()

    def set_bias(self, name: str, weight: float) -> None:
        """バイアスをセット/更新する。weight は 0.0〜1.0 でクランプ済み。"""
        weight = max(0.0, min(1.0, weight))
        if self._engine is None:
            self._stub_biases[name] = weight
            logger.debug("スタブ: set_bias %s=%.2f", name, weight)
            return
        self._engine.set_bias(name, weight)

    def adjust_bias(self, name: str, delta: float) -> None:
        """既存バイアスに delta を加算する（クランプあり）。"""
        current = self.get_biases().get(name, 0.0)
        self.set_bias(name, current + delta)

    def reset_biases(self) -> None:
        """全バイアスをリセットする。"""
        if self._engine is None:
            self._stub_biases = {}
            return
        self._engine.reset_biases()

    def activate_preset(self, preset_name: str) -> dict[str, float]:
        """プリセットを適用する。"""
        if self._engine is None:
            logger.debug("スタブ: activate_preset %s", preset_name)
            return {}
        return self._engine.activate_preset(preset_name)
