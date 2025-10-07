import subprocess
import time
import uuid
import json

import pytest

# Read src/models.json and dynamically generate test targets.
def load_models_from_config():
    with open("src/models.json") as f:
        config = json.load(f)
    # Returns a list of model names (e.g., "tinyllama:1.1b") from each entry in config["models"].
    return [model["name"] for model in config["models"].values()]


@pytest.mark.parametrize("model_full_name", load_models_from_config())
def test_docker_image_for_single_model(model_full_name, verify_inference):
    image_tag = f"test/ollama-ci:{model_full_name.replace(':', '-')}-v1-test"
    container_name = (
        f"test-container-{model_full_name.replace(':', '-')}-v1-{uuid.uuid4().hex[:4]}"
    )
    volume_name = f"{container_name}-cache"

    try:
        # Build image
        result = subprocess.run(
            [
                "docker",
                "build",
                "--build-arg",
                f"MODEL_NAME={model_full_name}",
                "-t",
                image_tag,
                "src",
            ],
            capture_output=False,
            text=True,
        )
        if result.returncode != 0:
            pytest.fail("Docker build failed")

        # Run container
        result = subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                container_name,
                "-v",
                f"{volume_name}:/root/.ollama",
                "-e",
                f"BUILT_IN_OLLAMA_MODEL={model_full_name}",
                image_tag,
            ],
            capture_output=False,
            text=True,
        )
        if result.returncode != 0:
            pytest.fail("Docker run failed")

        # Health check
        for attempt in range(90):
            time.sleep(10)
            result = subprocess.run(
                [
                    "docker",
                    "inspect",
                    "--format",
                    "{{.State.Health.Status}}",
                    container_name,
                ],
                capture_output=False,
                text=True,
            )
            if result.returncode == 0:
                break
            if attempt == 89:
                result = subprocess.run(
                    ["docker", "logs", container_name], capture_output=True, text=True
                )
                logs = result.stdout if result.returncode == 0 else "No logs"
                pytest.fail(
                    f"Container for model {model_full_name} did not become healthy in 900 seconds.\n"
                    f"Logs:\n{logs}"
                )

        # Check model list
        result = subprocess.run(
            [
                "docker",
                "exec",
                container_name,
                "curl",
                "-s",
                "http://localhost:11434/api/tags",
            ],
            capture_output=False,
            text=True,
        )
        if result.returncode != 0:
            pytest.fail("API call failed")

        verify_inference(container_name, model_full_name)

    finally:
        # Cleanup
        subprocess.run(["docker", "stop", container_name], capture_output=True)
        subprocess.run(["docker", "rm", "--force", container_name], capture_output=True)
        subprocess.run(["docker", "rmi", "--force", image_tag], capture_output=True)
        subprocess.run(
            ["docker", "volume", "rm", "-f", volume_name], capture_output=True
        )
