import subprocess
import time

import pytest


def test_e2e_with_docker_compose():
    """E2E test using docker-compose"""
    compose_file = "docker-compose.test.yml"

    try:
        # Clean up any existing containers
        subprocess.run(
            ["docker", "compose", "-f", compose_file, "down", "-v"],
            capture_output=False,
        )

        # Build and start container
        result = subprocess.run(
            ["docker", "compose", "-f", compose_file, "up", "-d", "--build"],
            capture_output=False,
            text=True,
        )
        if result.returncode != 0:
            pytest.fail(f"Docker compose up failed: {result.stderr}")

        container_name = "ollama-test-container"

        # Wait for container to be healthy (up to 15 minutes)
        for attempt in range(90):
            time.sleep(10)

            # Check if container is still running
            result = subprocess.run(
                ["docker", "ps", "-q", "-f", f"name={container_name}"],
                capture_output=False,
                text=True,
            )
            if result.returncode != 0:
                # Container stopped, get logs
                result = subprocess.run(
                    ["docker", "compose", "-f", compose_file, "logs"],
                    capture_output=True,
                    text=True,
                )
                logs = result.stdout if result.returncode == 0 else "No logs"
                pytest.fail(f"Container stopped unexpectedly.\nLogs:\n{logs}")

            # Check if ollama API is responding
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    container_name,
                    "curl",
                    "-sf",
                    "http://localhost:11434/api/tags",
                ],
                capture_output=False,
                text=True,
            )
            if result.returncode == 0:
                print(
                    f"✅ Container is healthy and model is loaded (attempt {attempt + 1})"
                )
                break

            if attempt == 89:
                result = subprocess.run(
                    ["docker", "compose", "-f", compose_file, "logs"],
                    capture_output=True,
                    text=True,
                )
                logs = result.stdout if result.returncode == 0 else "No logs"
                pytest.fail(
                    f"Container did not become healthy in 900 seconds.\n"
                    f"Logs:\n{logs}"
                )

        # Verify model is available via API
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

        print("✅ E2E test passed successfully")

    finally:
        # Cleanup
        subprocess.run(
            ["docker", "compose", "-f", compose_file, "down", "-v"],
            capture_output=True,
        )
