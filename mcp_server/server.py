from mcp.server import MCPServer
import subprocess
import os

mcp = MCPServer("selenium-pytest")

# Your project root
PROJECT_ROOT = r"C:\Users\viswa\OneDrive\Metafusion_SentryPlatform-selenium_pytest"


@mcp.tool()
def hello() -> str:
    """Test MCP connection."""
    return "MCP is working!"


@mcp.tool()
def run_pytest(test_path: str = "") -> str:
    """
    Run pytest tests.

    Examples:
      run_pytest()
      run_pytest("tests/test_login.py")
      run_pytest("tests/test_login.py::test_valid_login")
    """

    command = ["python", "-m", "pytest", "-v"]

    if test_path:
        command.append(test_path)

    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300
        )

        return (
            f"Pytest exit code: {result.returncode}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    except subprocess.TimeoutExpired:
        return "Pytest timed out after 5 minutes."

    except Exception as e:
        return f"Error running pytest: {e}"


if __name__ == "__main__":
    mcp.run()
