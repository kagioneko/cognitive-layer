# cognitive-layer

AIエージェントの認知レイヤー統合エンジン。

[NeuroState Engine](https://github.com/kagioneko/neurostate-engine)（内部状態）と [Bias Engine](https://github.com/kagioneko/bias-engine-mcp)（思考傾向）を組み合わせ、エージェントの「認知」を3層構造でモデル化します。

## これは何をするもの？

```
NeuroState（内部状態）× Bias Engine（思考傾向）→ Policy（行動方針）→ LLM
```

NeuroState が「今どんな状態か」を管理し、Bias Engine が「どう考えやすいか」を管理します。cognitive-layer はその2つを繋ぎ、エージェントが「どう振る舞うか」を決定します。

```
ユーザーが強く批判する
    ↓
cortisol相当（GABA低下・corruption上昇）
    ↓
confirmation_bias と hostile_attribution_bias が上昇
    ↓
Policy: defensiveness 高・openness 低・warmth 低
    ↓
エージェントの応答が防衛的・頑固になる
```

**向いている用途:**
- NeuroState と Bias Engine を組み合わせた高度なキャラクターAI
- 感情状態 × 思考傾向の統合デバッグ・可視化
- エージェントの認知レイヤーのカスタマイズ

## インストール

```bash
pip install pydantic pyyaml

# 依存リポジトリも必要
git clone https://github.com/kagioneko/neurostate-engine
git clone https://github.com/kagioneko/bias-engine-mcp
```

## クイックスタート

```python
from core.cognitive_integration import CognitiveIntegration

ci = CognitiveIntegration(user_id="emilia")

# イベントで状態を更新し、認知スナップショットを取得
snapshot = ci.update("criticism", power=3.0)

print(snapshot.to_dict())
# {
#   "state": {"dopamine": 0.42, "serotonin": 0.38, ...},
#   "biases": {"confirmation_bias": 0.2, ...},
#   "policy": {"exploration": 0.7, "defensiveness": 0.6, ...}
# }
```

## アーキテクチャ

```
cognitive-layer/
├── core/
│   ├── neurostate_client.py    # NeuroState Engine ラッパー
│   ├── bias_engine_client.py   # Bias Engine ラッパー
│   ├── cognitive_integration.py # オーケストレーター（中核）
│   ├── policy_mapper.py         # State × Bias → Policy 変換
│   ├── config_loader.py         # config.yaml ローダー
│   └── models.py                # データモデル
├── integrations/
│   ├── claude/    # Claude system prompt 向け
│   ├── openai/    # OpenAI message 向け
│   └── langchain/ # LangChain 向け（予定）
├── examples/
│   └── basic/demo.py
└── config.yaml    # マッピングルール（ここを編集してキャラクターを調整）
```

### 結合ルール

- NeuroState と Bias Engine は**互いを知らない**
- `cognitive_integration.py` だけが両者の橋渡し
- `config.yaml` を編集するだけでマッピングルールを変えられる

## config.yaml

State → Bias および State/Bias → Policy のマッピングルールを外部管理します。

```yaml
state_to_bias_rules:
  - if_key: G        # GABA（落ち着き）
    operator: "<"
    threshold: 0.3   # 0.3 未満になったら
    adjust:
      hostile_attribution_bias: 0.2  # 敵意帰属バイアスを +0.2
      confirmation_bias: 0.2

policy_rules:
  - based_on: corruption
    source: state
    affects: defensiveness
    weight: 0.8      # corruption が高いほど defensiveness が上がる
```

## CognitionSnapshot

デバッグ・ロギング・UI可視化用の統合スナップショット:

```json
{
  "state": {
    "dopamine": 0.8,
    "serotonin": 0.5,
    "acetylcholine": 0.5,
    "oxytocin": 0.7,
    "gaba": 0.0,
    "endorphin": 0.8,
    "corruption": 0.0
  },
  "biases": {
    "hostile_attribution_bias": 1.0,
    "confirmation_bias": 1.0
  },
  "policy": {
    "exploration": 1.0,
    "caution": 0.8,
    "rigidity": 0.98,
    "warmth": 1.0,
    "openness_to_contradiction": 0.0,
    "verbosity": 0.87,
    "defensiveness": 1.0
  }
}
```

## 統合モジュール

- `integrations/claude/` — Claude system prompt への注入
- `integrations/openai/` — OpenAI system message ビルダー
- `integrations/langchain/` — LangChain 連携（予定）

## デモ

```bash
python3 examples/basic/demo.py
```

## 関連リポジトリ

| リポジトリ | 役割 |
|-----------|------|
| [neurostate-engine](https://github.com/kagioneko/neurostate-engine) | 内部状態（神経伝達物質モデル） |
| [bias-engine-mcp](https://github.com/kagioneko/bias-engine-mcp) | 認知バイアス管理 |
| cognitive-layer（このリポジトリ） | 統合・ポリシー変換 |

## ライセンス

MIT
