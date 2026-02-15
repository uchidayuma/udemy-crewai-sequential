# SDLC自動化エージェント — crewAI サンプルプロジェクト

crewAI を使って、ソフトウェア開発ライフサイクル（SDLC）の全工程を
マルチエージェントで自動化するサンプルプロジェクトです。

架空の企業「株式会社ルート・テック」の開発依頼を題材に、
要件定義からインフラ設計まで6つの専門エージェントがドキュメントを自動生成します。

---

## エージェント構成

| エージェント | 役割 | 使用モデル | 出力ファイル |
|---|---|---|---|
| Requirements Analyst | 要件定義書（RDD）の作成 | MODEL_LARGE | docs/RDD.md |
| System Architect | システム設計書の作成 | MODEL_LARGE | docs/ARCHITECTURE.md |
| UI Designer | UI/UX設計仕様書の作成 | MODEL_LARGE | docs/UI_DESIGN.md |
| Developer | プロトタイプ実装仕様書の作成 | MODEL_SMALL | docs/IMPLEMENTATION.md |
| QA Specialist | QAレポートの作成 | MODEL_SMALL | docs/QA_REPORT.md |
| Infra Specialist | インフラ設計書の作成 | MODEL_LARGE | docs/INFRA.md |

各タスク完了後に人間（PM）が承認するゲートが入ります（`human_input: true`）。

---

## セットアップ

### 1. 前提条件

- Python 3.11以上（[pyenv](https://github.com/pyenv/pyenv) 推奨）
- [uv](https://docs.astral.sh/uv/) パッケージマネージャー

```bash
pip install uv
```

### 2. 依存パッケージのインストール

```bash
crewai install
```

### 3. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、APIキーを設定します。

```bash
cp .env.example .env
```

`.env` を編集して使用するプロバイダーのAPIキーを入力してください。

---

## 対応LLMプロバイダー

このプロジェクトは crewAI 内部の **LiteLLM** により、複数のLLMプロバイダーに対応しています。
`.env` の `MODEL_LARGE` / `MODEL_SMALL` を書き換えるだけで切り替えられます。

| プロバイダー | MODEL_LARGE の例 | 必要な環境変数 | 追加パッケージ |
|---|---|---|---|
| Anthropic（デフォルト） | `anthropic/claude-sonnet-4-5-20250929` | `ANTHROPIC_API_KEY` | 不要 |
| OpenAI | `openai/gpt-4o` | `OPENAI_API_KEY` | 不要 |
| Google Gemini | `gemini/gemini-2.5-flash` | `GOOGLE_API_KEY` | 要インストール |
| Ollama（ローカル・無料） | `ollama/qwen3:4b` | 不要 | 不要（Ollama アプリのみ） |

### プロバイダーの切り替え手順

**Anthropic → OpenAI に切り替える場合**

`.env` を以下のように変更し、`crewai run` を実行するだけです。

```bash
OPENAI_API_KEY=sk-...
MODEL_LARGE=openai/gpt-4o
MODEL_SMALL=openai/gpt-4o-mini
```

**Anthropic → Google Gemini に切り替える場合**

Gemini は追加パッケージが必要です。`.env` の変更に加えて以下を実行してください。

```bash
uv add "crewai[google-genai]"
```

```bash
GOOGLE_API_KEY=your-google-api-key
MODEL_LARGE=gemini/gemini-2.5-flash
MODEL_SMALL=gemini/gemini-2.5-flash
```

> **注意**: `blake2s` / `blake2b` に関するワーニングが表示される場合がありますが、
> 実行には影響しないため無視して問題ありません。

> **Gemini 無料プランご利用の方へ**: `gemini-2.5-flash` は無料プランのレート制限（10 RPM / 500 RPD）が
> 厳しく、6エージェントの連続実行で 429 エラーが発生しやすいです。
> `gemini/gemini-2.0-flash` または `gemini/gemini-1.5-flash`（15 RPM / 1500 RPD）への
> 変更をお試しください。

**Ollama（ローカル・完全無料）に切り替える場合**

APIキー不要でローカルで動かせます。レート制限もありません。

1. [Ollama](https://ollama.com) をインストールして起動する
2. 使用するモデルを pull する

```bash
ollama pull qwen3:4b
```

3. `.env` を以下のように設定する（APIキー不要）

```bash
MODEL_LARGE=ollama/qwen3:4b
MODEL_SMALL=ollama/qwen3:4b
```

4. Ollama アプリを起動した状態で `crewai run` を実行する

> **注意**: ローカルモデルはクラウドモデルと比べて出力品質が下がる場合があります。
> 動作確認・学習用途での使用を推奨します。

---

## トラブルシューティング

### OpenAI で 401 エラーが出る場合

`401 Incorrect API key provided` が出る場合は以下を確認してください。

**よくある原因と対処:**

| 原因 | 確認・対処 |
|---|---|
| APIキーの貼り付けミス | `.env` を開いてキーの前後に余分なスペースや改行がないか確認する |
| ChatGPT と API は別課金 | ChatGPT Plus があっても API 利用は別途 [課金設定](https://platform.openai.com/settings/organization/billing) が必要 |
| 残高が $0 | 同上のページで残高を確認し、$5 以上チャージする |
| 発行直後 | 新しいキーは反映まで数秒かかる場合がある。少し待ってから再試行する |

APIキーが正しいかどうかは以下のコマンドで確認できます:

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if 'data' in d else d['error']['message'])"
```

`OK` と表示されれば有効です。

---

## 実行方法

```bash
crewai run
```

実行が完了すると `docs/` 以下に各フェーズのドキュメントが生成されます。

### その他のコマンド

```bash
# 前回実行のタスクIDを確認（途中から再開したい場合）
crewai log-tasks-outputs

# 特定のタスクから再実行
crewai replay -t <task_id>
```

---

## ファイル構成

```
.
├── .env.example                  # 環境変数のテンプレート
├── knowledge/
│   └── project_context.md        # エージェントに渡すプロジェクト仕様
├── docs/                         # 生成されるドキュメント（実行後に作成）
│   ├── RDD.md
│   ├── ARCHITECTURE.md
│   ├── UI_DESIGN.md
│   ├── IMPLEMENTATION.md
│   ├── QA_REPORT.md
│   └── INFRA.md
└── src/sdlc_test/
    ├── crew.py                   # エージェント・タスクの定義
    ├── main.py                   # エントリーポイント
    └── config/
        ├── agents.yaml           # エージェントの役割・目標・背景
        └── tasks.yaml            # タスクの詳細・期待する出力
```

---

## カスタマイズ方法

別のプロジェクトに適用したい場合は `knowledge/project_context.md` を書き換えるだけです。
エージェントやタスクの追加・変更は `config/agents.yaml` と `config/tasks.yaml` で行います。

---

## 参考リンク

- [crewAI 公式ドキュメント](https://docs.crewai.com)
- [LiteLLM 対応プロバイダー一覧](https://docs.litellm.ai/docs/providers)
