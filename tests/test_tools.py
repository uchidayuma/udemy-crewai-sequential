"""MCPServerTool / StitchMCPTool の単体テスト。

実際の MCP サーバーには接続せず、MCPServerAdapter をモックして
パラメータの組み立てロジックだけを検証する。
"""

from unittest.mock import MagicMock, patch

import pytest

from sdlc_test.tools.mcp_tool import MCPServerTool, MermaidMCPTool, StitchMCPTool, StdioMCPServerTool


# ── フィクスチャ ─────────────────────────────────────────


class _AuthenticatedMCPTool(MCPServerTool):
    """APIキーありのテスト用具象クラス"""

    server_url = "https://example.com/mcp"
    transport = "streamable-http"
    api_key_env = "MY_API_KEY"
    api_key_header = "X-Api-Key"


class _PublicMCPTool(MCPServerTool):
    """APIキーなしのテスト用具象クラス"""

    server_url = "https://public.example.com/mcp"
    transport = "sse"


# ── MCPServerTool（基底クラス）のテスト ──────────────────


class TestMCPServerTool:
    def test_correct_params_with_api_key(self):
        """APIキーあり: MCPServerAdapter に正しいパラメータが渡されること"""
        mock_tools = [MagicMock(), MagicMock()]

        with patch("sdlc_test.tools.mcp_tool.MCPServerAdapter") as mock_cls:
            mock_cls.return_value.tools = mock_tools

            with patch.dict("os.environ", {"MY_API_KEY": "secret-key"}):
                result = _AuthenticatedMCPTool().get_tools()

        mock_cls.assert_called_once_with(
            {
                "url": "https://example.com/mcp",
                "transport": "streamable-http",
                "headers": {"X-Api-Key": "secret-key"},
            }
        )
        assert result == mock_tools

    def test_correct_params_without_api_key(self):
        """APIキーなし: headers キーが含まれないこと"""
        with patch("sdlc_test.tools.mcp_tool.MCPServerAdapter") as mock_cls:
            mock_cls.return_value.tools = []

            result = _PublicMCPTool().get_tools()

        mock_cls.assert_called_once_with(
            {
                "url": "https://public.example.com/mcp",
                "transport": "sse",
            }
        )
        assert result == []

    def test_returns_adapter_tools(self):
        """get_tools() が adapter.tools をそのまま返すこと"""
        expected = [MagicMock(name="tool_a"), MagicMock(name="tool_b")]

        with patch("sdlc_test.tools.mcp_tool.MCPServerAdapter") as mock_cls:
            mock_cls.return_value.tools = expected

            with patch.dict("os.environ", {"MY_API_KEY": "key"}):
                result = _AuthenticatedMCPTool().get_tools()

        assert result is expected

    def test_missing_env_var_sends_empty_string(self):
        """環境変数が未設定の場合、空文字列がヘッダーにセットされること"""
        with patch("sdlc_test.tools.mcp_tool.MCPServerAdapter") as mock_cls:
            mock_cls.return_value.tools = []

            # MY_API_KEY を環境から除外した状態で実行
            with patch.dict("os.environ", {}, clear=True):
                _AuthenticatedMCPTool().get_tools()

        called_params = mock_cls.call_args[0][0]
        assert called_params["headers"]["X-Api-Key"] == ""


# ── StitchMCPTool のテスト ───────────────────────────────


class TestStitchMCPTool:
    def test_class_variables(self):
        """クラス変数が Google Stitch の仕様通りに設定されていること"""
        tool = StitchMCPTool()
        assert tool.server_url == "https://stitch.googleapis.com/mcp"
        assert tool.transport == "streamable-http"
        assert tool.api_key_env == "STITCH_API_KEY"
        assert tool.api_key_header == "X-Goog-Api-Key"

    def test_uses_stitch_api_key_env(self):
        """STITCH_API_KEY 環境変数の値が X-Goog-Api-Key ヘッダーに渡されること"""
        with patch("sdlc_test.tools.mcp_tool.MCPServerAdapter") as mock_cls:
            mock_cls.return_value.tools = []

            with patch.dict("os.environ", {"STITCH_API_KEY": "stitch-secret"}):
                StitchMCPTool().get_tools()

        called_params = mock_cls.call_args[0][0]
        assert called_params["headers"]["X-Goog-Api-Key"] == "stitch-secret"

    def test_uses_streamable_http_transport(self):
        """Stitch は SSE ではなく streamable-http を使うこと"""
        with patch("sdlc_test.tools.mcp_tool.MCPServerAdapter") as mock_cls:
            mock_cls.return_value.tools = []

            with patch.dict("os.environ", {"STITCH_API_KEY": "key"}):
                StitchMCPTool().get_tools()

        called_params = mock_cls.call_args[0][0]
        assert called_params["transport"] == "streamable-http"


# ── StdioMCPServerTool のテスト ──────────────────────────


class TestStdioMCPServerTool:
    def test_builds_stdio_server_parameters(self):
        """StdioServerParameters が正しいコマンド・引数で生成されること"""
        class MyLocalTool(StdioMCPServerTool):
            command = "npx"
            args = ["-y", "my-mcp-server"]

        mock_tools = [MagicMock()]

        with patch("sdlc_test.tools.mcp_tool.MCPServerAdapter") as mock_adapter_cls, \
             patch("sdlc_test.tools.mcp_tool.StdioServerParameters") as mock_params_cls:
            mock_adapter_cls.return_value.tools = mock_tools
            mock_params_cls.return_value = "mock_params"

            result = MyLocalTool().get_tools()

        mock_params_cls.assert_called_once_with(
            command="npx",
            args=["-y", "my-mcp-server"],
            env=None,
        )
        mock_adapter_cls.assert_called_once_with("mock_params")
        assert result == mock_tools

    def test_merges_env_vars_with_os_environ(self):
        """env_vars が os.environ にマージされて渡されること"""
        class MyToolWithEnv(StdioMCPServerTool):
            command = "npx"
            args = ["-y", "my-server"]
            env_vars = {"MY_VAR": "my-value"}

        with patch("sdlc_test.tools.mcp_tool.MCPServerAdapter") as mock_adapter_cls, \
             patch("sdlc_test.tools.mcp_tool.StdioServerParameters") as mock_params_cls:
            mock_adapter_cls.return_value.tools = []
            mock_params_cls.return_value = "mock_params"

            with patch.dict("os.environ", {"EXISTING": "existing-value"}, clear=True):
                MyToolWithEnv().get_tools()

        called_env = mock_params_cls.call_args.kwargs["env"]
        assert called_env["MY_VAR"] == "my-value"
        assert called_env["EXISTING"] == "existing-value"


# ── MermaidMCPTool のテスト ──────────────────────────────


class TestMermaidMCPTool:
    def test_class_variables(self):
        """npx で Mermaid MCP Server が起動するよう設定されていること"""
        tool = MermaidMCPTool()
        assert tool.command == "npx"
        assert "-y" in tool.args
        assert "@peng-shawn/mermaid-mcp-server" in tool.args

    def test_content_image_supported_is_false(self):
        """CONTENT_IMAGE_SUPPORTED=false が設定され、画像をファイル保存する設定になっていること"""
        tool = MermaidMCPTool()
        assert tool.env_vars.get("CONTENT_IMAGE_SUPPORTED") == "false"

    def test_get_tools_passes_env_to_server(self):
        """get_tools() 呼び出し時に CONTENT_IMAGE_SUPPORTED が環境変数に含まれること"""
        with patch("sdlc_test.tools.mcp_tool.MCPServerAdapter") as mock_adapter_cls, \
             patch("sdlc_test.tools.mcp_tool.StdioServerParameters") as mock_params_cls:
            mock_adapter_cls.return_value.tools = []
            mock_params_cls.return_value = "mock_params"

            MermaidMCPTool().get_tools()

        called_env = mock_params_cls.call_args.kwargs["env"]
        assert called_env["CONTENT_IMAGE_SUPPORTED"] == "false"
