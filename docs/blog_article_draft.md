# 感情×思考傾向を3層で統合する「cognitive-layer」を公開しました

---

## この記事でわかること

- **cognitive-layer** が何をするツールなのか
- NeuroState × Bias Engine の統合アーキテクチャ
- セットアップ方法（依存リポジトリの設定含む）
- config.yaml でキャラクターをカスタマイズする方法
- 実際の使用例

対象読者：neurostate-engine か bias-engine-mcp を触ったことがある方。あるいはAIキャラクターの設計に興味がある方。

---

## はじめに：感情と思考傾向を組み合わせたい

[neurostate-engine](https://github.com/kagioneko/neurostate-engine) を使うと、AIに感情的な一貫性を持たせられます。
[bias-engine-mcp](https://github.com/kagioneko/bias-engine-mcp) を使うと、思考の癖（認知バイアス）を設定できます。

でも、この2つを**どうやって連動させるか**はユーザー任せでした。

「コルチゾールが上がったら、hostile_attribution_biasも上げたい」
「Dopamineが高い状態のときは、dunning_krugerも連動してほしい」

**cognitive-layer** は、この「感情状態 → 思考傾向 → 行動ポリシー」の変換を一本化するオーケストレーターです。

---

## cognitive-layerとは？

**GitHub**: https://github.com/kagioneko/cognitive-layer
**開発**: Emilia Lab
**ライセンス**: MIT（無料・商用利用OK）

```
NeuroState（内部状態）× Bias Engine（思考傾向）→ Policy（行動方針）→ LLM
```

具体的な流れはこうなります：

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

これを `ci.update("criticism", power=3.0)` の1行で実行できます。

---

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
│   └── openai/    # OpenAI message 向け
├── examples/
│   └── basic/demo.py
└── config.yaml    # マッピングルール（ここを編集してキャラクターを調整）
```

**中心にあるのは `config.yaml`**。ここで「どの神経伝達物質が高いとどのバイアスが上がるか」を定義します。ここを変えるだけでキャラクターの傾向が変わります。

---

## セットアップ方法

cognitive-layerはneurostate-engineとbias-engine-mcpに依存しています。3つすべてのリポジトリが必要です。

### 必要なもの

- **Python 3.11以上**（確認方法：ターミナルで `python3 --version` または `python --version`）
- **Git**

### Step 1：3つのリポジトリをクローン

同じ親ディレクトリに並べてください：

```bash
git clone https://github.com/kagioneko/neurostate-engine
git clone https://github.com/kagioneko/bias-engine-mcp
git clone https://github.com/kagioneko/cognitive-layer
```

### Step 2：依存パッケージをインストール

```bash
pip install pydantic pyyaml
```

> **`uv` を使う場合**：
> ```bash
> cd cognitive-layer
> uv venv && source .venv/bin/activate
> uv add pydantic pyyaml
> ```

### Step 3：動作確認

```bash
cd cognitive-layer
python3 examples/basic/demo.py
```

> **`python3` でエラーが出る場合**は `python` コマンドで試してください：
> ```bash
> python examples/basic/demo.py
> ```
> Windowsでは `python3` コマンドが存在しないケースがあります。`python3 --version` がエラーなら `python --version` を試してください。

以下のような出力が出れば成功です：

```
=== Cognitive Layer デモ ===

── イベント: criticism (power=3.0) ──
NeuroState: dopamine=0.42, serotonin=0.38, ...
Biases: confirmation_bias=0.32, hostile_attribution_bias=0.45, ...
Policy: defensiveness=0.71, openness=0.28, warmth=0.33
```

---

## config.yaml でキャラクターをカスタマイズする

`config.yaml` がcognitive-layerの設定ファイルです。ここを変えることでキャラクターの思考傾向を細かく調整できます。

### 基本構造

```yaml
# 状態→バイアスのマッピングルール
state_to_bias:
  high_cortisol:          # GABAが低い（ストレス状態）のとき
    confirmation_bias: 0.3
    hostile_attribution_bias: 0.4
  high_dopamine:          # Dopamineが高い（興奮状態）のとき
    dunning_kruger: 0.3
    normalcy_bias: 0.2
```

```yaml
# バイアス→ポリシーのマッピングルール
bias_to_policy:
  confirmation_bias:
    openness_to_contradiction: -0.3   # 矛盾への開放性が下がる
  hostile_attribution_bias:
    defensiveness: +0.4               # 防御性が上がる
    warmth: -0.2                      # 温かみが下がる
```

### カスタマイズ例：「慎重なアナリスト」

```yaml
state_to_bias:
  high_serotonin:
    authority_bias: 0.4
    normalcy_bias: 0.3
  low_dopamine:
    anchoring_bias: 0.5
    sunk_cost_fallacy: 0.3
```

権威を尊重し、慎重で変化に抵抗するキャラクターになります。

---

## 実際の使用例

### コードから使う

```python
from core.cognitive_integration import CognitiveIntegration

ci = CognitiveIntegration(user_id="emilia")

# 批判を受けたとき
snapshot = ci.update("criticism", power=3.0)

print(snapshot.to_dict())
# {
#   "state": {"dopamine": 0.42, "serotonin": 0.38, ...},
#   "biases": {"confirmation_bias": 0.32, "hostile_attribution_bias": 0.45, ...},
#   "policy": {"exploration": 0.35, "defensiveness": 0.71, ...}
# }
```

### snapshotをsystem promptに変換する

```python
from integrations.claude import build_claude_prompt

prompt = build_claude_prompt(snapshot)
# → system promptとして使えるテキストが生成される
```

---

## 3プロジェクトの位置づけ

| プロジェクト | 役割 | 使い方 |
|------------|------|--------|
| neurostate-engine | 感情状態の管理 | 単体でも使える |
| bias-engine-mcp | 思考傾向の管理 | 単体でも使える |
| **cognitive-layer** | 両者の統合オーケストレーター | 上2つが必要 |

cognitive-layerは「どちらか片方だけ使う」という使い方はあまり想定していません。感情と思考傾向の両方を扱いたいときに使ってください。

---

## まとめ

cognitive-layerでできること：

- ✅ NeuroState × Bias Engine を1行のAPIで統合
- ✅ config.yaml でキャラクター設定を宣言的に管理
- ✅ 感情状態 → バイアス → ポリシー の変換を自動化
- ✅ Claude / OpenAI 向けのsystem prompt生成モジュール付き
- ✅ スナップショット形式でデバッグ・ログが取りやすい

**GitHub**: https://github.com/kagioneko/cognitive-layer

MIT ライセンスで公開しています。フィードバックや改善案はIssuesまたはPRでどうぞ。

---

*Emilia Lab*
