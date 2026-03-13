"""Claude 向け Cognitive Layer インテグレーション

Usage:
    from integrations.claude import build_cognition_context

    context = build_cognition_context(snapshot)
    # system prompt に追記して使う
"""

from cognitive_core.models import CognitionSnapshot


def build_cognition_context(snapshot: CognitionSnapshot) -> str:
    """CognitionSnapshot を Claude の system prompt 用テキストに変換する。"""
    s = snapshot.state
    p = snapshot.policy

    lines = [
        "[Cognitive State]",
        f"  dopamine={s.D:.2f}  serotonin={s.S:.2f}  acetylcholine={s.C:.2f}",
        f"  oxytocin={s.O:.2f}  gaba={s.G:.2f}  endorphin={s.E:.2f}  corruption={s.corruption:.2f}",
        "",
        "[Active Biases]",
    ]
    active_biases = {k: v for k, v in snapshot.biases.items() if v > 0.0}
    if active_biases:
        for name, weight in active_biases.items():
            lines.append(f"  {name}: {weight:.2f}")
    else:
        lines.append("  (none)")

    lines += [
        "",
        "[Policy]",
        f"  exploration={p.exploration:.2f}  caution={p.caution:.2f}  rigidity={p.rigidity:.2f}",
        f"  warmth={p.warmth:.2f}  openness={p.openness_to_contradiction:.2f}",
        f"  verbosity={p.verbosity:.2f}  defensiveness={p.defensiveness:.2f}",
    ]

    return "\n".join(lines)
