import subprocess
import json
import pytest


@pytest.fixture
def verify_inference():
    def _verify(container_name, model_name):
        print(f"Verifying model inference for {model_name}...")
        inference_result = subprocess.run(
            [
                "docker",
                "exec",
                container_name,
                "curl",
                "-s",
                "http://localhost:11434/api/generate",
                "-d",
                json.dumps({
                    "model": model_name,
                    "prompt": "Why is the sky blue?",
                    "stream": False
                })
            ],
            capture_output=True,
            text=True,
        )

        if inference_result.returncode != 0:
            pytest.fail(
                f"Inference API call failed for model {model_name}.\n"
                f"Stderr: {inference_result.stderr}"
            )

        # Verify that the response can be parsed as JSON and contains the 'response' key.
        try:
            response_json = json.loads(inference_result.stdout)
            assert "response" in response_json
            print(f"✅ Inference successful for model {model_name}")
        except (json.JSONDecodeError, AssertionError):
            pytest.fail(
                f"Inference response is invalid for model {model_name}.\n"
                f"Stdout: {inference_result.stdout}"
            )
    return _verify