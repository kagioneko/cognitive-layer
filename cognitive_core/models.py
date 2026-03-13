"""Cognitive Layer Integration - 統合データモデル"""

from dataclasses import dataclass, field


@dataclass
class NeuroStateNormalized:
    """
    NeuroState の値を 0.0〜1.0 に正規化したスナップショット。

    NeuroState 実フィールド対応:
        D: Dopamine      - 報酬・動機づけ
        S: Serotonin     - 安定・幸福感
        C: Acetylcholine - 集中・認知
        O: Oxytocin      - 絆・共感
        G: GABA          - 抑制・落ち着き
        E: Endorphin     - 快感・鎮痛
        corruption       - 状態汚染度（高いほど不安定）
    """
    D: float = 0.5
    S: float = 0.5
    C: float = 0.5
    O: float = 0.2
    G: float = 0.5
    E: float = 0.5
    corruption: float = 0.0

    def to_dict(self) -> dict:
        return {
            "dopamine": self.D,
            "serotonin": self.S,
            "acetylcholine": self.C,
            "oxytocin": self.O,
            "gaba": self.G,
            "endorphin": self.E,
            "corruption": self.corruption,
        }

    @classmethod
    def from_raw(cls, raw: dict) -> "NeuroStateNormalized":
        """NeuroState の生値（0-100）から正規化スナップショットを生成する。"""
        return cls(
            D=raw.get("D", 50.0) / 100.0,
            S=raw.get("S", 50.0) / 100.0,
            C=raw.get("C", 50.0) / 100.0,
            O=raw.get("O", 20.0) / 100.0,
            G=raw.get("G", 50.0) / 100.0,
            E=raw.get("E", 50.0) / 100.0,
            corruption=raw.get("corruption", 0.0) / 100.0,
        )


@dataclass
class Policy:
    """
    State × Bias から導出されるエージェントの行動方針。

    各値は 0.0〜1.0。高いほどその傾向が強い。
    """
    exploration: float = 0.5           # 探索・新規性の追求
    caution: float = 0.5               # 慎重さ
    rigidity: float = 0.5              # 頑固さ・変化抵抗
    warmth: float = 0.5                # 感情的温かさ
    openness_to_contradiction: float = 0.5  # 反論への開放性
    verbosity: float = 0.5             # 饒舌さ
    defensiveness: float = 0.5         # 防衛的姿勢

    def to_dict(self) -> dict:
        return {
            "exploration": self.exploration,
            "caution": self.caution,
            "rigidity": self.rigidity,
            "warmth": self.warmth,
            "openness_to_contradiction": self.openness_to_contradiction,
            "verbosity": self.verbosity,
            "defensiveness": self.defensiveness,
        }


@dataclass
class CognitionSnapshot:
    """
    デバッグ・可視化・ロギング用の統合認知スナップショット。
    State + Biases + Policy を一括で保持する。
    """
    state: NeuroStateNormalized = field(default_factory=NeuroStateNormalized)
    biases: dict[str, float] = field(default_factory=dict)
    policy: Policy = field(default_factory=Policy)

    def to_dict(self) -> dict:
        return {
            "state": self.state.to_dict(),
            "biases": self.biases,
            "policy": self.policy.to_dict(),
        }
