#!/usr/bin/env python3
"""
Test script to verify semantic-release configuration.

This script demonstrates how different commit types will affect version bumping.
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str] | str, capture: bool = True) -> str:
    """Run a shell command and return output."""
    if isinstance(cmd, str):
        # Split simple commands into list
        cmd_list = cmd.split()
    else:
        cmd_list = cmd
    
    result = subprocess.run(
        cmd_list,
        capture_output=capture,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    if capture:
        return result.stdout.strip()
    return ""


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    import re
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if match:
        return match.group(1)
    return "unknown"


def test_semantic_release_config():
    """Test semantic-release configuration."""
    print("🔍 Testing Semantic Release Configuration\n")
    print("=" * 70)

    # Check if semantic-release is installed
    try:
        version = run_command(["semantic-release", "--version"])
        print(f"✅ Python Semantic Release installed: {version}")
    except Exception as e:
        print(f"❌ Error: semantic-release not installed: {e}")
        print("Install with: pip install python-semantic-release==9.17.0")
        sys.exit(1)

    # Get current version
    current_version = get_current_version()
    print(f"📦 Current version: {current_version}")
    print()

    # Test configuration validity
    print("📋 Testing configuration validity...")
    result = subprocess.run(
        ["semantic-release", "version", "--print"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    
    if result.returncode == 0:
        print("✅ Configuration is valid")
    else:
        print(f"❌ Configuration error:\n{result.stderr}")
        sys.exit(1)

    print()
    print("=" * 70)
    print("\n📚 Version Bump Examples:\n")

    examples = [
        ("fix: correct off-by-one error", "Patch: 3.3.0 → 3.3.1"),
        ("feat: add new export format option", "Minor: 3.3.0 → 3.4.0"),
        ("feat!: redesign API\n\nBREAKING CHANGE: API changed", "Major: 3.3.0 → 4.0.0"),
        ("docs: update README", "No release"),
        ("chore: update dependencies", "No release"),
        ("perf: optimize pattern matching", "Patch: 3.3.0 → 3.3.1"),
    ]

    for commit_msg, bump_type in examples:
        commit_type = commit_msg.split(":")[0].split("!")[0]
        icon = {
            "fix": "🐛",
            "feat": "✨",
            "docs": "📝",
            "chore": "🔧",
            "perf": "⚡",
        }.get(commit_type, "📌")
        
        # Get the first line of the commit message
        first_line = commit_msg.split("\n")[0]
        print(f"{icon} {first_line}")
        print(f"   → {bump_type}\n")

    print("=" * 70)
    print("\n🎯 How to trigger a release:\n")
    print("1. Commit changes using conventional commit format")
    print("2. Push to main branch")
    print("3. GitHub Actions workflow automatically:")
    print("   - Analyzes commits since last release")
    print("   - Bumps version in pyproject.toml")
    print("   - Updates CHANGELOG.md")
    print("   - Creates Git tag")
    print("   - Publishes GitHub Release")
    print()
    print("📖 See docs/RELEASE_MANAGEMENT.md for full details")
    print()


if __name__ == "__main__":
    test_semantic_release_config()
