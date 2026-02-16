"""MCP サーバー接続を抽象化するカスタムツール。

MCP サーバーには接続方式が2種類ある:
  - HTTP系（streamable-http / sse）: クラウドサービス等に接続する場合
  - stdio: ローカルでプロセスを起動して接続する場合

それぞれ MCPServerTool / StdioMCPServerTool を継承し、
クラス変数を上書きするだけで新しい MCP サーバーを追加できる。

使用例（HTTP）:
    class MyMCPTool(MCPServerTool):
        server_url = "https://example.com/mcp"
        api_key_env = "MY_API_KEY"
        api_key_header = "X-Api-Key"

使用例（stdio）:
    class MyLocalMCPTool(StdioMCPServerTool):
        command = "npx"
        args = ["-y", "my-mcp-server"]

    tools = MyLocalMCPTool().get_tools()  # Agent の tools= に渡せる形式で返る
"""

import os

from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter


class MCPServerTool:
    """HTTP系トランスポート（streamable-http / sse）の MCP サーバーへの接続を抽象化するベースクラス。

    crewAI は内部で mcpadapt を使い MCP ツールを crewAI 互換形式に変換する。
    transport には "streamable-http"（新プロトコル）と "sse"（旧プロトコル）が選べる。
    接続先サーバーがどちらに対応しているかは各サービスのドキュメントを参照すること。
    """

    server_url: str = ""
    transport: str = "streamable-http"
    api_key_env: str = ""     # APIキーを格納する環境変数名（例: "STITCH_API_KEY"）
    api_key_header: str = ""  # APIキーを渡す HTTP ヘッダー名（例: "X-Goog-Api-Key"）

    def get_tools(self) -> list:
        """MCP サーバーからツール一覧を取得し、crewAI 互換形式で返す。"""
        params: dict = {
            "url": self.server_url,
            "transport": self.transport,
        }

        if self.api_key_env and self.api_key_header:
            params["headers"] = {
                self.api_key_header: os.environ.get(self.api_key_env, "")
            }

        adapter = MCPServerAdapter(params)
        return adapter.tools


class StdioMCPServerTool:
    """stdio トランスポートの MCP サーバーへの接続を抽象化するベースクラス。

    ローカルでプロセスを起動して接続する MCP サーバーに使用する。
    Node.js の npx コマンドで起動するサーバーが典型例。
    """

    command: str = ""         # 実行コマンド（例: "npx", "uvx"）
    args: list = []           # コマンド引数（例: ["-y", "@some/mcp-server"]）
    env_vars: dict = {}       # 追加の環境変数（例: {"KEY": "value"}）

    def get_tools(self) -> list:
        """ローカル MCP サーバーを起動してツール一覧を取得し、crewAI 互換形式で返す。"""
        env = {**os.environ, **self.env_vars} if self.env_vars else None

        params = StdioServerParameters(
            command=self.command,
            args=self.args,
            env=env,
        )

        adapter = MCPServerAdapter(params)
        return adapter.tools


class StitchMCPTool(MCPServerTool):
    """Google Stitch MCP サーバーへの接続。

    環境変数 STITCH_API_KEY が必要。
    Stitch は Streamable HTTP（MCP の新プロトコル）のみ対応しており、
    旧プロトコルの SSE では接続できない点に注意。

    既知の問題:
        Anthropic の JSON Schema draft 2020-12 と MCP が返すスキーマの間に
        非互換があり、現時点では ui_designer エージェントへの組み込みを停止中。
        スキーマ変換ラッパーを実装後に crew.py の _get_stitch_tools() を有効化する。
    """

    server_url = "https://stitch.googleapis.com/mcp"
    transport = "streamable-http"
    api_key_env = "STITCH_API_KEY"
    api_key_header = "X-Goog-Api-Key"


class MermaidMCPTool(StdioMCPServerTool):
    """Mermaid MCP Server への接続。

    Mermaid 記法の図を PNG / SVG に変換する `generate` ツールを提供する。
    Node.js（npx）が必要。初回実行時にパッケージが自動ダウンロードされる。

    CONTENT_IMAGE_SUPPORTED=false に設定することで、画像をファイルとして保存する。
    エージェントが generate ツールを呼ぶ際は name と folder の指定が必要。

    使用例（エージェントへのツール登録）:
        tools=MermaidMCPTool().get_tools()

    generate ツールのパラメータ:
        code   : Mermaid 記法のダイアグラムコード（必須）
        name   : 出力ファイル名（CONTENT_IMAGE_SUPPORTED=false 時に必須）
        folder : 出力先ディレクトリ（CONTENT_IMAGE_SUPPORTED=false 時に必須）
        theme  : "default" | "forest" | "dark" | "neutral"（省略可）
        outputFormat : "png" | "svg"（省略可、デフォルトは png）
    """

    command = "npx"
    args = ["-y", "@peng-shawn/mermaid-mcp-server"]
    env_vars = {"CONTENT_IMAGE_SUPPORTED": "false"}
