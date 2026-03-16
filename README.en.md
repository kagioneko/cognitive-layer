# cognitive-layer

**Cognitive integration engine for AI agents — NeuroState × BiasEngine → Policy → LLM**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 🇯🇵 [日本語版 README はこちら](README.md)

---

## What is this?

[NeuroState Engine](https://github.com/kagioneko/neurostate-engine) manages *how the agent feels*.
[Bias Engine](https://github.com/kagioneko/bias-engine-mcp) manages *how the agent tends to think*.
**cognitive-layer connects both and decides *how the agent behaves*.**

```
NeuroState (internal state) × Bias Engine (thinking tendencies) → Policy (behavior) → LLM
```

### Example

```
User delivers harsh criticism
    ↓
GABA drops / corruption rises (stress response)
    ↓
confirmation_bias + hostile_attribution_bias increase
    ↓
Policy: defensiveness ↑ / openness ↓ / warmth ↓
    ↓
Agent responds in a guarded, stubborn tone
```

---

## Use Cases

- Advanced character AI combining emotional state and thinking tendencies
- Debugging and visualizing the interaction between NeuroState and BiasEngine
- Customizing an agent's cognitive layer for specific personas

---

## Installation

```bash
pip install pydantic pyyaml

# Required dependencies
git clone https://github.com/kagioneko/neurostate-engine
git clone https://github.com/kagioneko/bias-engine-mcp
```

---

## Quick Start

```python
from cognitive_core.cognitive_integration import CognitiveIntegration
from core.state_model import NeuroState
from core.bias_engine import BiasEngine

# Initialize
neuro = NeuroState()
bias = BiasEngine()
cog = CognitiveIntegration(neuro, bias)

# Get behavioral policy
policy = cog.get_policy()
print(policy)
# {
#   "warmth": 0.7,
#   "openness": 0.6,
#   "defensiveness": 0.2,
#   "assertiveness": 0.5,
#   "empathy": 0.8
# }

# Generate a system prompt that reflects the current cognitive state
prompt = cog.generate_system_prompt()
print(prompt)
# "You are feeling calm and open. You tend to listen carefully before responding..."
```

---

## Policy Dimensions

| Dimension | Description |
|-----------|-------------|
| `warmth` | Friendliness and care in responses |
| `openness` | Willingness to consider other viewpoints |
| `defensiveness` | Tendency to guard against perceived attacks |
| `assertiveness` | Directness and confidence |
| `empathy` | Sensitivity to emotional cues |

---

## Architecture

```
NeuroState values
    ↓
CognitiveIntegration
    ├── Reads neurotransmitter levels
    ├── Syncs with BiasEngine
    ├── Computes policy dimensions
    └── Generates system prompt
```

---

## Related Projects

- [neurostate-engine](https://github.com/kagioneko/neurostate-engine) — Emotional state (required)
- [bias-engine-mcp](https://github.com/kagioneko/bias-engine-mcp) — Cognitive bias (required)
- [neurostate-sdk](https://github.com/kagioneko/neurostate-sdk) — Unified SDK (recommended)
- [memory-engine-mcp](https://github.com/kagioneko/memory-engine-mcp) — Session memory

---

## License

MIT © [Emilia Lab](https://kagioneko.com/emilia_lab/)
