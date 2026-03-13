"""OpenAI 向け Cognitive Layer インテグレーション"""

from cognitive_core.models import CognitionSnapshot


def build_system_message(snapshot: CognitionSnapshot) -> dict:
    """CognitionSnapshot を OpenAI system message 形式で返す。"""
    from integrations.claude import build_cognition_context
    content = build_cognition_context(snapshot)
    return {"role": "system", "content": content}
