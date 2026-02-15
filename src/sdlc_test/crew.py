import os
from pathlib import Path

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, before_kickoff, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from sdlc_test.tools.mcp_tool import MermaidMCPTool, StitchMCPTool


@CrewBase
class SdlcTest():
    """SdlcTest crew — Route Tech Inc. 架電レコメンドツール SDLC自動化"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def _get_stitch_tools(self) -> list:
        return StitchMCPTool().get_tools()

    def _get_llm(self, model_env: str = "MODEL_LARGE") -> LLM:
        # crewAI は内部で LiteLLM を使用しており、モデル文字列のプレフィックス
        # （例: "anthropic/", "openai/", "gemini/"）に応じて対応する API キーを
        # 環境変数から自動取得する。
        # プロバイダーを切り替える場合は .env の MODEL_LARGE / MODEL_SMALL を
        # 書き換えるだけでよく、コードの変更は不要。
        # 対応する環境変数: ANTHROPIC_API_KEY / OPENAI_API_KEY / GOOGLE_API_KEY
        # 参考: https://docs.crewai.com/concepts/llms
        #
        # Ollama（ローカル）の場合:
        #   Ollama は OpenAI 互換 API を localhost:11434/v1 で提供している。
        #   crewAI のネイティブ Ollama プロバイダーが未実装のため、
        #   openai/ プレフィックス + base_url でローカルエンドポイントに接続する。
        model = os.environ.get(model_env, "anthropic/claude-sonnet-4-5-20250929")

        if model.startswith("ollama/"):
            model_name = model.removeprefix("ollama/")
            return LLM(
                model=f"openai/{model_name}",
                base_url="http://localhost:11434/v1",
                api_key="ollama",  # Ollama はキー不要だが形式上必要
            )

        return LLM(model=model)

    @before_kickoff
    def prepare_output_dir(self, inputs):
        """成果物出力先ディレクトリを事前に作成する"""
        Path("docs").mkdir(exist_ok=True)
        return inputs

    # ── Agents ──────────────────────────────────────────────

    @agent
    def requirements_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['requirements_analyst'],
            llm=self._get_llm("MODEL_LARGE"),  # 判断・構造化
            max_rpm=10,
            verbose=True,
        )

    @agent
    def system_architect(self) -> Agent:
        # TODO: Mermaid MCP ツールはツール呼び出し能力が高いモデル（Claude Sonnet / GPT-4o 等）
        #       でのみ安定動作する。qwen3:4b 等の小型ローカルモデルでは呼び出されないため無効化中。
        #       Anthropic / OpenAI 利用時は tools=MermaidMCPTool().get_tools() を復活させる。
        return Agent(
            config=self.agents_config['system_architect'],
            llm=self._get_llm("MODEL_LARGE"),  # 設計判断・技術選定
            max_rpm=10,
            verbose=True,
        )

    @agent
    def ui_designer(self) -> Agent:
        # TODO: Stitch MCP ツールは mcpadapt と Anthropic native provider の
        #       JSON Schema 非互換により一時無効化中。
        #       スキーマ変換ラッパー実装後に tools=self._get_stitch_tools() を復活させる。
        return Agent(
            config=self.agents_config['ui_designer'],
            llm=self._get_llm("MODEL_LARGE"),  # 創造的なUI設計
            max_rpm=10,
            verbose=True,
        )

    @agent
    def developer(self) -> Agent:
        return Agent(
            config=self.agents_config['developer'],
            llm=self._get_llm("MODEL_SMALL"),   # 指示に従ったコード生成
            max_rpm=10,
            verbose=True,
        )

    @agent
    def qa_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['qa_specialist'],
            llm=self._get_llm("MODEL_SMALL"),   # テストケース列挙
            max_rpm=10,
            verbose=True,
        )

    @agent
    def infra_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['infra_specialist'],
            llm=self._get_llm("MODEL_LARGE"),  # ゼロベースの技術選定
            max_rpm=10,
            verbose=True,
        )

    # ── Tasks ───────────────────────────────────────────────

    @task
    def requirements_task(self) -> Task:
        return Task(
            config=self.tasks_config['requirements_task'],
        )

    @task
    def architecture_task(self) -> Task:
        return Task(
            config=self.tasks_config['architecture_task'],
            context=[self.requirements_task()],
        )

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task'],
            context=[self.requirements_task(), self.architecture_task()],
        )

    @task
    def development_task(self) -> Task:
        return Task(
            config=self.tasks_config['development_task'],
            context=[self.architecture_task(), self.design_task()],
        )

    @task
    def qa_task(self) -> Task:
        return Task(
            config=self.tasks_config['qa_task'],
            context=[self.requirements_task(), self.development_task()],
        )

    @task
    def infra_task(self) -> Task:
        return Task(
            config=self.tasks_config['infra_task'],
            context=[self.architecture_task(), self.development_task()],
        )

    # ── Crew ────────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        """SDLC 自動化クルーを生成する（Sequential process）"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=5,
        )
