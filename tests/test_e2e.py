import contextlib
import subprocess
import time

import pytest


class TestE2E:
    @classmethod
    @contextlib.contextmanager
    def e2e_setup(cls, compose_file, build=False):
        container_name = {
            "docker-compose.test.yml": "ollama-test-container",
            "docker-compose.pull-test.yml": "ollama-pull-test-container",
        }.get(compose_file, "unknown-container")

        try:
            # Clean up any existing containers
            subprocess.run(
                ["docker", "compose", "-f", compose_file, "down", "-v"],
                capture_output=False,
            )

            # Build and start container
            up_command = ["docker", "compose", "-f", compose_file, "up", "-d"]
            if build:
                up_command.append("--build")
            result = subprocess.run(
                up_command,
                capture_output=False,
                text=True,
            )
            if result.returncode != 0:
                pytest.fail(f"Docker compose up failed: {result.stderr}")

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

            yield container_name

        finally:
            # Cleanup
            subprocess.run(
                ["docker", "compose", "-f", compose_file, "down", "-v"],
                capture_output=True,
            )

    def test_docker_compose_build(self, verify_inference):
        """E2E test using docker-compose with build"""
        compose_file = "docker-compose.test.yml"

        with self.e2e_setup(compose_file, build=True) as container_name:
            verify_inference(container_name, "tinyllama:1.1b")

            print("✅ E2E build test passed successfully")

    def test_docker_compose_pull(self, verify_inference):
        """E2E test using docker-compose with pulled image from GitHub registry"""
        compose_file = "docker-compose.pull-test.yml"

        with self.e2e_setup(compose_file, build=False) as container_name:
            verify_inference(container_name, "qwen3:0.6b")

            print("✅ E2E pull test passed successfully")
