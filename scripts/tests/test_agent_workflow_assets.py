"""Unit tests for agent instructions, skills, adapters, and repo file layout."""

import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_instruction_hierarchy_exists_and_bounded():
    instruction_files = [
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "backend" / "AGENTS.md",
        REPO_ROOT / "frontend" / "AGENTS.md",
        REPO_ROOT / "juries" / "AGENTS.md",
    ]
    for path in instruction_files:
        assert path.exists(), f"Expected instruction file {path} to exist"
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) <= 160, f"Instruction file {path.name} exceeds concise limit ({len(lines)} > 160 lines)"

    root_content = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "docs/changes/" in root_content
    assert "Change-Record:" in root_content
    assert "docs/EXPLANATION.md" in root_content
    assert "UPL Compliance" in root_content


@pytest.mark.unit
def test_canonical_skills_exist_and_conform():
    canonical_skills = [
        "justify-change-record",
        "justify-feature-planning",
        "justify-debugging",
        "justify-verification-handoff",
        "justify-rag-eval",
    ]
    skills_dir = REPO_ROOT / ".agents" / "skills"

    for skill_name in canonical_skills:
        skill_file = skills_dir / skill_name / "SKILL.md"
        assert skill_file.exists(), f"Skill file {skill_file} not found"

        content = skill_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        assert len(lines) <= 160, f"Skill {skill_name} exceeds concise limit ({len(lines)} > 160 lines)"

        # Check YAML frontmatter
        assert lines[0].strip() == "---", f"Skill {skill_name} missing frontmatter start"
        fm_end = False
        fm_dict: dict[str, str] = {}
        for line in lines[1:]:
            if line.strip() == "---":
                fm_end = True
                break
            if ":" in line:
                k, v = line.split(":", 1)
                fm_dict[k.strip()] = v.strip().strip("'\"")

        assert fm_end, f"Skill {skill_name} missing frontmatter closing delimiter"
        assert fm_dict.get("name") == skill_name, f"Skill {skill_name} has invalid name {fm_dict.get('name')}"
        assert "description" in fm_dict and len(fm_dict["description"]) > 10, (
            f"Skill {skill_name} missing valid description"
        )

    # Specific check for justify-rag-eval metric floors
    rag_eval_content = (skills_dir / "justify-rag-eval" / "SKILL.md").read_text(encoding="utf-8")
    assert "evals.run_eval" in rag_eval_content
    assert "faithfulness" in rag_eval_content
    assert "0.90" in rag_eval_content


@pytest.mark.unit
def test_tool_adapters_exist_and_conform():
    # 1. opencode.json
    opencode_json = REPO_ROOT / "opencode.json"
    assert opencode_json.exists(), "opencode.json does not exist"
    import json

    data = json.loads(opencode_json.read_text(encoding="utf-8"))
    assert data.get("$schema") == "https://opencode.ai/config.json"
    assert "instructions" in data
    assert "AGENTS.md" in data["instructions"]
    assert "docs/changes/README.md" in data["instructions"]

    # 2. opencode commands
    commands_dir = REPO_ROOT / ".opencode" / "commands"
    for cmd in ["start-change", "verify-change", "handoff-change"]:
        cmd_path = commands_dir / f"{cmd}.md"
        assert cmd_path.exists(), f"Command {cmd_path} does not exist"
        cmd_content = cmd_path.read_text(encoding="utf-8")
        assert cmd_content.startswith("---"), f"Command {cmd} missing frontmatter"
        assert "description:" in cmd_content, f"Command {cmd} missing description in frontmatter"

    # 3. Claude Code adapters
    claude_files = [
        REPO_ROOT / "CLAUDE.md",
        REPO_ROOT / "backend" / "CLAUDE.md",
        REPO_ROOT / "frontend" / "CLAUDE.md",
        REPO_ROOT / "juries" / "CLAUDE.md",
    ]
    for cfile in claude_files:
        assert cfile.exists(), f"Claude instruction file {cfile} does not exist"
        content = cfile.read_text(encoding="utf-8")
        assert "@AGENTS.md" in content, f"{cfile.name} missing @AGENTS.md import"

    # 4. .claude/skills symlink
    claude_skills = REPO_ROOT / ".claude" / "skills"
    assert claude_skills.exists(), ".claude/skills does not exist"
    assert claude_skills.is_symlink(), ".claude/skills is not a symlink"
    assert (claude_skills / "justify-change-record" / "SKILL.md").exists()


@pytest.mark.unit
def test_opencode_plugin_structure():
    import json

    opencode_json = REPO_ROOT / "opencode.json"
    data = json.loads(opencode_json.read_text(encoding="utf-8"))
    assert "plugins" in data, "opencode.json missing 'plugins' array"
    assert "./.opencode/plugins/justify-workflow" in data["plugins"]

    plugin_dir = REPO_ROOT / ".opencode" / "plugins" / "justify-workflow"
    assert plugin_dir.is_dir(), f"{plugin_dir} is not a directory"

    pkg_json_file = plugin_dir / "package.json"
    assert pkg_json_file.exists(), f"{pkg_json_file} does not exist"
    pkg = json.loads(pkg_json_file.read_text(encoding="utf-8"))
    assert pkg.get("name") == "justify-workflow"
    assert pkg.get("type") == "module"

    index_js = plugin_dir / "index.js"
    assert index_js.exists(), f"{index_js} does not exist"
    content = index_js.read_text(encoding="utf-8")
    assert 'id: "justify.workflow"' in content
    assert "setup(ctx)" in content or "setup(" in content


@pytest.mark.unit
def test_public_learning_documentation_replaces_private_history():
    constitution = REPO_ROOT / "docs" / "CONSTITUTION.md"
    assert constitution.exists(), "docs/CONSTITUTION.md must exist"
    assert not (REPO_ROOT / ".specify").exists(), ".specify directory must be fully retired"

    assert (REPO_ROOT / "docs" / "superpowers" / "specs" / "2026-10-20-osj-learning-release-design.md").exists()
    assert (REPO_ROOT / "docs" / "superpowers" / "plans" / "2026-10-20-osj-learning-release.md").exists()
    assert not (REPO_ROOT / "specs").exists(), "Top-level specs directory must be removed"
    assert not (REPO_ROOT / "justify_srs.md").exists(), "Root justify_srs.md must be relocated"

    # Publication includes educational docs rather than original business collateral.
    assert not (REPO_ROOT / "docs" / "showcase").exists()
    assert not (REPO_ROOT / "docs" / "presentation").exists()
    assert not (REPO_ROOT / "docs" / "MEET_THE_BUILDERS_BLOG.md").exists()

    # 3. Cleaned review and evaluation files
    assert not (REPO_ROOT / "docs" / "chat-timeout-review.md").exists()
    assert (REPO_ROOT / "docs" / "changes" / "2026-10-20-osj-learning-release.md").exists()
    assert not (REPO_ROOT / "docs" / "research").exists()
    assert not (REPO_ROOT / "backend" / "evals" / "PLAN.md").exists()

    # 4. Retired Spec Kit machinery
    assert not (REPO_ROOT / ".specify" / "extensions.yml").exists(), "extensions.yml should be retired"
    speckit_skills = list((REPO_ROOT / ".agents" / "skills").glob("speckit-*"))
    assert len(speckit_skills) == 0, f"Found unretired speckit skills: {speckit_skills}"

    # 5. Marker stripped from root AGENTS.md
    root_agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "<!-- SPECKIT START -->" not in root_agents


@pytest.mark.unit
def test_agent_workflow_documentation_and_path_cleanliness():
    # 1. Flagship documentation guide exists and contains essential sections
    guide = REPO_ROOT / "docs" / "AGENT_WORKFLOW.md"
    assert guide.exists(), "docs/AGENT_WORKFLOW.md must exist"
    guide_content = guide.read_text(encoding="utf-8")
    assert "Proportional Planning" in guide_content
    assert "justify-change-record" in guide_content
    assert "validate_change_records.py" in guide_content
    assert "install-git-hooks.sh" in guide_content
    assert "OpenCode" in guide_content

    # 2. No stale docs/presentation paths in commands or skills
    skills_dir = REPO_ROOT / ".agents" / "skills"
    for skill_file in skills_dir.glob("**/SKILL.md"):
        content = skill_file.read_text(encoding="utf-8")
        assert "docs/presentation" not in content, (
            f"Stale docs/presentation path found in {skill_file.relative_to(REPO_ROOT)}"
        )

    commands_dir = REPO_ROOT / ".opencode" / "commands"
    for cmd_file in commands_dir.glob("*.md"):
        content = cmd_file.read_text(encoding="utf-8")
        assert "docs/presentation" not in content, (
            f"Stale docs/presentation path found in {cmd_file.relative_to(REPO_ROOT)}"
        )

    # 3. juries/AGENTS.md accurately reflects Dart and Jaspr
    juries_agents = (REPO_ROOT / "juries" / "AGENTS.md").read_text(encoding="utf-8")
    assert "Jaspr" in juries_agents
    assert "dart" in juries_agents


@pytest.mark.unit
def test_dedicated_repo_scripts_layout():
    # Validator lives under scripts/ and is executable
    validator_path = REPO_ROOT / "scripts" / "validate_change_records.py"
    assert validator_path.exists(), "scripts/validate_change_records.py must exist"
    assert os.access(validator_path, os.X_OK), "scripts/validate_change_records.py must be executable"

    # Validator no longer exists inside backend/scripts
    assert not (REPO_ROOT / "backend" / "scripts" / "validate_change_records.py").exists(), (
        "backend/scripts/validate_change_records.py must be removed"
    )

    # Old unit test locations in backend/tests/unit must not exist
    assert not (REPO_ROOT / "backend" / "tests" / "unit" / "test_validate_change_records.py").exists()
    assert not (REPO_ROOT / "backend" / "tests" / "unit" / "test_agent_workflow_assets.py").exists()
