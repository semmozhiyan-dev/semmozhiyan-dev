"""
Tests for static assets — validates the presence and integrity of
generated/committed files such as github-metrics.svg.
"""

import pathlib
import xml.etree.ElementTree as ET

import pytest

REPO_ROOT = pathlib.Path(__file__).parent.parent
METRICS_SVG = REPO_ROOT / "github-metrics.svg"


# ---------------------------------------------------------------------------
# SVG file existence
# ---------------------------------------------------------------------------

class TestSvgFileExists:
    def test_metrics_svg_exists(self):
        assert METRICS_SVG.exists(), \
            "github-metrics.svg must exist in the repository root"

    def test_metrics_svg_is_file(self):
        assert METRICS_SVG.is_file(), \
            "github-metrics.svg must be a regular file, not a directory"

    def test_metrics_svg_is_not_empty(self):
        assert METRICS_SVG.stat().st_size > 0, \
            "github-metrics.svg must not be an empty file"


# ---------------------------------------------------------------------------
# SVG file content
# ---------------------------------------------------------------------------

class TestSvgFileContent:
    @pytest.fixture(scope="class")
    def svg_text(self):
        return METRICS_SVG.read_text(encoding="utf-8")

    def test_metrics_svg_is_utf8_readable(self):
        content = METRICS_SVG.read_text(encoding="utf-8")
        assert isinstance(content, str)

    def test_metrics_svg_starts_with_svg_tag(self, svg_text):
        stripped = svg_text.lstrip()
        assert stripped.startswith("<svg") or stripped.startswith("<?xml"), \
            "github-metrics.svg must start with <svg or <?xml declaration"

    def test_metrics_svg_contains_svg_element(self, svg_text):
        assert "<svg" in svg_text, \
            "github-metrics.svg must contain an <svg> element"

    def test_metrics_svg_closes_svg_element(self, svg_text):
        assert "</svg>" in svg_text, \
            "github-metrics.svg must have a closing </svg> tag"

    def test_metrics_svg_is_valid_xml(self, svg_text):
        try:
            ET.fromstring(svg_text)
        except ET.ParseError as exc:
            pytest.fail(f"github-metrics.svg is not valid XML: {exc}")

    def test_metrics_svg_root_tag_is_svg(self, svg_text):
        root = ET.fromstring(svg_text)
        local_name = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        assert local_name == "svg", \
            f"Root XML element must be 'svg', got '{local_name}'"

    def test_metrics_svg_has_width_or_viewbox(self, svg_text):
        root = ET.fromstring(svg_text)
        has_width = root.get("width") is not None
        has_viewbox = root.get("viewBox") is not None
        assert has_width or has_viewbox, \
            "SVG root element must have a 'width' or 'viewBox' attribute"

    def test_metrics_svg_has_content_elements(self, svg_text):
        root = ET.fromstring(svg_text)
        # An SVG with real content should have child elements
        assert len(list(root)) > 0, \
            "github-metrics.svg must contain child elements (not be a bare <svg/>)"


# ---------------------------------------------------------------------------
# Repository root — expected committed files
# ---------------------------------------------------------------------------

class TestRepositoryRootFiles:
    def test_readme_md_present(self):
        assert (REPO_ROOT / "README.md").exists(), \
            "README.md must exist at repository root"

    def test_metrics_svg_present(self):
        assert (REPO_ROOT / "github-metrics.svg").exists(), \
            "github-metrics.svg must exist at repository root"

    def test_github_dir_present(self):
        assert (REPO_ROOT / ".github").is_dir(), \
            ".github directory must exist"

    def test_workflows_dir_present(self):
        assert (REPO_ROOT / ".github" / "workflows").is_dir(), \
            ".github/workflows directory must exist"

    def test_no_sensitive_files_committed(self):
        sensitive_patterns = [
            ".env", "*.pem", "*.key", "*.p12", "*.pfx",
            "id_rsa", "id_dsa", "*.gpg",
            "secrets.yml", "secrets.yaml",
            ".npmrc", "oauth_token",
        ]
        for pattern in sensitive_patterns:
            matches = list(REPO_ROOT.rglob(pattern))
            # Exclude .git directory
            matches = [m for m in matches if ".git" not in m.parts]
            assert not matches, \
                f"Sensitive file pattern '{pattern}' must not be committed: {matches}"


# ---------------------------------------------------------------------------
# Cross-file consistency checks
# ---------------------------------------------------------------------------

class TestCrossFileConsistency:
    def test_metrics_svg_filename_matches_workflow_config(self):
        """The filename in main.yml's metrics action must match the committed SVG."""
        import yaml
        workflow_path = REPO_ROOT / ".github" / "workflows" / "main.yml"
        data = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        steps = data["jobs"]["github-metrics"]["steps"]
        configured_filename = None
        for step in steps:
            if "lowlighter/metrics" in step.get("uses", ""):
                configured_filename = step["with"].get("filename")
                break
        assert configured_filename is not None, \
            "Could not find filename in metrics workflow step"
        assert (REPO_ROOT / configured_filename).exists(), \
            f"Committed SVG '{configured_filename}' must match the workflow-configured filename"

    def test_snake_output_branch_referenced_in_readme(self):
        """The 'output' branch used by snake.yml should be referenced in README."""
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        assert "output" in readme, \
            "README.md must reference the 'output' branch for snake SVGs"

    def test_metrics_svg_referenced_in_readme(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        assert "github-metrics.svg" in readme, \
            "github-metrics.svg must be referenced in README.md"

    def test_username_consistent_across_files(self):
        """The GitHub username 'semmozhiyan-dev' must be consistent in all files."""
        import yaml
        username = "semmozhiyan-dev"
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        assert username in readme, "Username must appear in README.md"

        main_wf = yaml.safe_load(
            (REPO_ROOT / ".github" / "workflows" / "main.yml").read_text(encoding="utf-8")
        )
        main_steps = main_wf["jobs"]["github-metrics"]["steps"]
        for step in main_steps:
            if "lowlighter/metrics" in step.get("uses", ""):
                assert step["with"].get("user") == username, \
                    f"main.yml metrics step must use username '{username}'"

        snake_wf = yaml.safe_load(
            (REPO_ROOT / ".github" / "workflows" / "snake.yml").read_text(encoding="utf-8")
        )
        snake_steps = snake_wf["jobs"]["generate-snake"]["steps"]
        for step in snake_steps:
            if "Platane/snk" in step.get("uses", ""):
                assert step["with"].get("github_user_name") == username, \
                    f"snake.yml step must use github_user_name '{username}'"
