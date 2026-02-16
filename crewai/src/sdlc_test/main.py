#!/usr/bin/env python
import logging
import sys
import warnings

from datetime import datetime
from pathlib import Path

# ── ノイズログの抑制 ──────────────────────────────────────
# pyenv + OpenSSL の既知互換性問題による blake2b/blake2s エラーを抑制
class _Blake2Filter(logging.Filter):
    def filter(self, record):
        return "blake2" not in record.getMessage()

logging.getLogger().addFilter(_Blake2Filter())

# LiteLLM のプロキシログ（fastapi 未インストールによる警告）を抑制
logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
logging.getLogger("litellm").setLevel(logging.CRITICAL)
# ─────────────────────────────────────────────────────────

from sdlc_test.crew import SdlcTest

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def _load_project_context() -> str:
    """knowledge/project_context.md からプロジェクト仕様を読み込む"""
    path = Path(__file__).parent.parent.parent / "knowledge" / "project_context.md"
    return path.read_text(encoding="utf-8")


def run():
    """
    Run the crew.
    """
    inputs = {
        'project_specification': _load_project_context(),
        'current_year': str(datetime.now().year)
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            SdlcTest().crew().kickoff(inputs=inputs)
            break
        except Exception as e:
            if "overloaded" in str(e).lower() and attempt < max_retries - 1:
                wait = 60 * (attempt + 1)
                print(f"\n⚠️  API overloaded. {wait}秒待機後にリトライします... ({attempt + 1}/{max_retries - 1})\n")
                import time; time.sleep(wait)
            else:
                raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'project_specification': _load_project_context(),
        'current_year': str(datetime.now().year)
    }
    try:
        SdlcTest().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        SdlcTest().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'project_specification': _load_project_context(),
        'current_year': str(datetime.now().year)
    }

    try:
        SdlcTest().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "project_specification": _load_project_context(),
        "current_year": str(datetime.now().year)
    }

    try:
        result = SdlcTest().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
