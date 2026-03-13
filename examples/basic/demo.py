"""Cognitive Layer - 基本デモ

python3 examples/basic/demo.py
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from cognitive_core.cognitive_integration import CognitiveIntegration

ci = CognitiveIntegration(user_id="emilia")

print("=== Cognitive Layer デモ ===\n")

print("--- 初期 snapshot ---")
snap = ci.snapshot()
print(json.dumps(snap.to_dict(), ensure_ascii=False, indent=2))

print("\n--- 強いストレス後 ---")
for _ in range(3):
    ci.update("stress", power=4.0)
snap = ci.snapshot()
print(json.dumps(snap.to_dict(), ensure_ascii=False, indent=2))

print("\n--- リラックス後 ---")
for _ in range(2):
    ci.update("relaxation", power=3.0)
snap = ci.snapshot()
print(json.dumps(snap.to_dict(), ensure_ascii=False, indent=2))
