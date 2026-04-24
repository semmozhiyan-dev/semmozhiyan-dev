"""
Tests for .github/workflows/*.yml — validates YAML syntax, required fields,
triggers, permissions, and job configurations for both workflows.
"""

import pathlib

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
MAIN_WORKFLOW = WORKFLOWS_DIR / "main.yml"
SNAKE_WORKFLOW = WORKFLOWS_DIR / "snake.yml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_yaml(path: pathlib.Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# ---------------------------------------------------------------------------
# Directory & file existence
# ---------------------------------------------------------------------------

class TestWorkflowFilesExist:
    def test_workflows_directory_exists(self):
        assert WORKFLOWS_DIR.exists() and WORKFLOWS_DIR.is_dir(), \
            ".github/workflows directory must exist"

    def test_main_workflow_exists(self):
        assert MAIN_WORKFLOW.exists(), "main.yml workflow must exist"

    def test_snake_workflow_exists(self):
        assert SNAKE_WORKFLOW.exists(), "snake.yml workflow must exist"

    def test_no_extra_unexpected_files(self):
        yml_files = list(WORKFLOWS_DIR.glob("*.yml")) + list(WORKFLOWS_DIR.glob("*.yaml"))
        names = {f.name for f in yml_files}
        expected = {"main.yml", "snake.yml"}
        unexpected = names - expected
        assert not unexpected, f"Unexpected workflow files found: {unexpected}"


# ---------------------------------------------------------------------------
# YAML validity
# ---------------------------------------------------------------------------

class TestYamlValidity:
    def test_main_workflow_is_valid_yaml(self):
        data = load_yaml(MAIN_WORKFLOW)
        assert isinstance(data, dict), "main.yml must parse to a YAML mapping"

    def test_snake_workflow_is_valid_yaml(self):
        data = load_yaml(SNAKE_WORKFLOW)
        assert isinstance(data, dict), "snake.yml must parse to a YAML mapping"

    def test_main_workflow_not_empty(self):
        data = load_yaml(MAIN_WORKFLOW)
        assert data, "main.yml must not be empty"

    def test_snake_workflow_not_empty(self):
        data = load_yaml(SNAKE_WORKFLOW)
        assert data, "snake.yml must not be empty"


# ---------------------------------------------------------------------------
# Top-level required keys
# ---------------------------------------------------------------------------

REQUIRED_TOP_LEVEL_KEYS = [
    pytest.param("name", id="name"),
    pytest.param(True, id="on"),   # PyYAML parses `on:` as boolean True
    pytest.param("jobs", id="jobs"),
]


class TestRequiredTopLevelKeys:
    @pytest.mark.parametrize("key", REQUIRED_TOP_LEVEL_KEYS)
    def test_main_workflow_has_key(self, key):
        data = load_yaml(MAIN_WORKFLOW)
        assert key in data, f"main.yml must have top-level key '{key}'"

    @pytest.mark.parametrize("key", REQUIRED_TOP_LEVEL_KEYS)
    def test_snake_workflow_has_key(self, key):
        data = load_yaml(SNAKE_WORKFLOW)
        assert key in data, f"snake.yml must have top-level key '{key}'"


# ---------------------------------------------------------------------------
# Workflow names
# ---------------------------------------------------------------------------

class TestWorkflowNames:
    def test_main_workflow_name(self):
        data = load_yaml(MAIN_WORKFLOW)
        assert data["name"] == "GitHub Metrics", \
            "main.yml name must be 'GitHub Metrics'"

    def test_snake_workflow_name(self):
        data = load_yaml(SNAKE_WORKFLOW)
        assert data["name"] == "Contribution Snake", \
            "snake.yml name must be 'Contribution Snake'"


# ---------------------------------------------------------------------------
# Triggers (on:)
# ---------------------------------------------------------------------------

class TestWorkflowTriggers:
    def test_main_has_schedule_trigger(self):
        data = load_yaml(MAIN_WORKFLOW)
        assert "schedule" in data[True], \
            "main.yml must have a schedule trigger"

    def test_main_has_workflow_dispatch(self):
        data = load_yaml(MAIN_WORKFLOW)
        assert "workflow_dispatch" in data[True], \
            "main.yml must support manual dispatch"

    def test_main_has_push_trigger(self):
        data = load_yaml(MAIN_WORKFLOW)
        assert "push" in data[True], \
            "main.yml must trigger on push"

    def test_main_push_targets_main_branch(self):
        data = load_yaml(MAIN_WORKFLOW)
        branches = data[True]["push"].get("branches", [])
        assert "main" in branches, \
            "main.yml push trigger must target the 'main' branch"

    def test_main_schedule_cron_format(self):
        data = load_yaml(MAIN_WORKFLOW)
        crons = [item["cron"] for item in data[True]["schedule"]]
        cron_pattern = r'^\S+ \S+ \S+ \S+ \S+$'
        import re
        for cron in crons:
            assert re.match(cron_pattern, cron), \
                f"Cron expression '{cron}' must have 5 fields"

    def test_main_schedule_runs_hourly(self):
        data = load_yaml(MAIN_WORKFLOW)
        crons = [item["cron"] for item in data[True]["schedule"]]
        assert any("0 * * * *" in c for c in crons), \
            "main.yml must schedule an hourly run (0 * * * *)"

    def test_snake_has_schedule_trigger(self):
        data = load_yaml(SNAKE_WORKFLOW)
        assert "schedule" in data[True], \
            "snake.yml must have a schedule trigger"

    def test_snake_has_workflow_dispatch(self):
        data = load_yaml(SNAKE_WORKFLOW)
        assert "workflow_dispatch" in data[True], \
            "snake.yml must support manual dispatch"

    def test_snake_has_push_trigger(self):
        data = load_yaml(SNAKE_WORKFLOW)
        assert "push" in data[True], \
            "snake.yml must trigger on push"

    def test_snake_push_targets_main_branch(self):
        data = load_yaml(SNAKE_WORKFLOW)
        branches = data[True]["push"].get("branches", [])
        assert "main" in branches, \
            "snake.yml push trigger must target the 'main' branch"

    def test_snake_schedule_runs_every_6_hours(self):
        data = load_yaml(SNAKE_WORKFLOW)
        crons = [item["cron"] for item in data[True]["schedule"]]
        assert any("0 */6 * * *" in c for c in crons), \
            "snake.yml must schedule a run every 6 hours (0 */6 * * *)"


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

class TestWorkflowJobs:
    def test_main_has_github_metrics_job(self):
        data = load_yaml(MAIN_WORKFLOW)
        assert "github-metrics" in data["jobs"], \
            "main.yml must define a 'github-metrics' job"

    def test_snake_has_generate_snake_job(self):
        data = load_yaml(SNAKE_WORKFLOW)
        assert "generate-snake" in data["jobs"], \
            "snake.yml must define a 'generate-snake' job"

    def test_main_job_runs_on_ubuntu(self):
        data = load_yaml(MAIN_WORKFLOW)
        runner = data["jobs"]["github-metrics"]["runs-on"]
        assert "ubuntu" in runner, \
            "github-metrics job must run on ubuntu"

    def test_snake_job_runs_on_ubuntu(self):
        data = load_yaml(SNAKE_WORKFLOW)
        runner = data["jobs"]["generate-snake"]["runs-on"]
        assert "ubuntu" in runner, \
            "generate-snake job must run on ubuntu"


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------

class TestWorkflowPermissions:
    def test_main_job_has_contents_write(self):
        data = load_yaml(MAIN_WORKFLOW)
        perms = data["jobs"]["github-metrics"].get("permissions", {})
        assert perms.get("contents") == "write", \
            "github-metrics job must have contents: write permission"

    def test_snake_job_has_contents_write(self):
        data = load_yaml(SNAKE_WORKFLOW)
        perms = data["jobs"]["generate-snake"].get("permissions", {})
        assert perms.get("contents") == "write", \
            "generate-snake job must have contents: write permission"


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

class TestWorkflowSteps:
    def test_main_job_has_steps(self):
        data = load_yaml(MAIN_WORKFLOW)
        steps = data["jobs"]["github-metrics"].get("steps", [])
        assert len(steps) >= 1, "github-metrics job must have at least one step"

    def test_snake_job_has_steps(self):
        data = load_yaml(SNAKE_WORKFLOW)
        steps = data["jobs"]["generate-snake"].get("steps", [])
        assert len(steps) >= 2, "generate-snake job must have at least two steps"

    def test_main_uses_lowlighter_metrics_action(self):
        data = load_yaml(MAIN_WORKFLOW)
        steps = data["jobs"]["github-metrics"]["steps"]
        uses_values = [s.get("uses", "") for s in steps]
        assert any("lowlighter/metrics" in u for u in uses_values), \
            "github-metrics job must use lowlighter/metrics action"

    def test_snake_uses_platane_snk_action(self):
        data = load_yaml(SNAKE_WORKFLOW)
        steps = data["jobs"]["generate-snake"]["steps"]
        uses_values = [s.get("uses", "") for s in steps]
        assert any("Platane/snk" in u for u in uses_values), \
            "generate-snake job must use Platane/snk action"

    def test_snake_uses_ghaction_github_pages(self):
        data = load_yaml(SNAKE_WORKFLOW)
        steps = data["jobs"]["generate-snake"]["steps"]
        uses_values = [s.get("uses", "") for s in steps]
        assert any("ghaction-github-pages" in u for u in uses_values), \
            "generate-snake job must use ghaction-github-pages to push output"

    def test_all_main_steps_have_name(self):
        data = load_yaml(MAIN_WORKFLOW)
        steps = data["jobs"]["github-metrics"]["steps"]
        for i, step in enumerate(steps):
            assert "name" in step, f"Step {i} in github-metrics job must have a 'name'"

    def test_all_snake_steps_have_name(self):
        data = load_yaml(SNAKE_WORKFLOW)
        steps = data["jobs"]["generate-snake"]["steps"]
        for i, step in enumerate(steps):
            assert "name" in step, f"Step {i} in generate-snake job must have a 'name'"


# ---------------------------------------------------------------------------
# Metrics action inputs (main.yml)
# ---------------------------------------------------------------------------

class TestMetricsActionInputs:
    @pytest.fixture(scope="class")
    def metrics_step(self):
        data = load_yaml(MAIN_WORKFLOW)
        steps = data["jobs"]["github-metrics"]["steps"]
        for step in steps:
            if "lowlighter/metrics" in step.get("uses", ""):
                return step
        pytest.fail("lowlighter/metrics step not found")

    def test_token_uses_secret(self, metrics_step):
        token = metrics_step["with"].get("token", "")
        assert "secrets.GITHUB_TOKEN" in token, \
            "Metrics action must use ${{ secrets.GITHUB_TOKEN }}"

    def test_user_is_correct(self, metrics_step):
        user = metrics_step["with"].get("user", "")
        assert user == "semmozhiyan-dev", \
            "Metrics action must target user 'semmozhiyan-dev'"

    def test_output_filename_is_svg(self, metrics_step):
        filename = metrics_step["with"].get("filename", "")
        assert filename.endswith(".svg"), \
            "Metrics output filename must end with .svg"

    def test_output_filename_matches_readme(self, metrics_step):
        filename = metrics_step["with"].get("filename", "")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        assert filename in readme, \
            f"Metrics output filename '{filename}' must be referenced in README.md"

    def test_committer_message_has_skip_ci(self, metrics_step):
        msg = metrics_step["with"].get("committer_message", "")
        assert "[skip ci]" in msg, \
            "Committer message must contain [skip ci] to avoid recursive runs"

    def test_timezone_is_india(self, metrics_step):
        tz = metrics_step["with"].get("config_timezone", "")
        assert tz == "Asia/Kolkata", \
            "Metrics timezone must be set to Asia/Kolkata"

    def test_plugin_isocalendar_enabled(self, metrics_step):
        assert metrics_step["with"].get("plugin_isocalendar") in (True, "yes"), \
            "Isocalendar plugin must be enabled"

    def test_plugin_languages_enabled(self, metrics_step):
        assert metrics_step["with"].get("plugin_languages") in (True, "yes"), \
            "Languages plugin must be enabled"

    def test_plugin_activity_enabled(self, metrics_step):
        assert metrics_step["with"].get("plugin_activity") in (True, "yes"), \
            "Activity plugin must be enabled"

    def test_plugin_lines_enabled(self, metrics_step):
        assert metrics_step["with"].get("plugin_lines") in (True, "yes"), \
            "Lines plugin must be enabled"

    def test_plugin_habits_enabled(self, metrics_step):
        assert metrics_step["with"].get("plugin_habits") in (True, "yes"), \
            "Habits plugin must be enabled"

    def test_plugin_achievements_enabled(self, metrics_step):
        assert metrics_step["with"].get("plugin_achievements") in (True, "yes"), \
            "Achievements plugin must be enabled"

    def test_plugin_people_enabled(self, metrics_step):
        assert metrics_step["with"].get("plugin_people") in (True, "yes"), \
            "People plugin must be enabled"

    def test_plugin_stars_enabled(self, metrics_step):
        assert metrics_step["with"].get("plugin_stars") in (True, "yes"), \
            "Stars plugin must be enabled"

    def test_plugin_repositories_features_correct_repos(self, metrics_step):
        repos = metrics_step["with"].get("plugin_repositories_featured", "")
        assert "wanderlite-travel-and-tourism" in repos, \
            "plugin_repositories_featured must include wanderlite-travel-and-tourism"
        assert "semmozhi-portfolio" in repos, \
            "plugin_repositories_featured must include semmozhi-portfolio"


# ---------------------------------------------------------------------------
# Snake action inputs (snake.yml)
# ---------------------------------------------------------------------------

class TestSnakeActionInputs:
    @pytest.fixture(scope="class")
    def snake_step(self):
        data = load_yaml(SNAKE_WORKFLOW)
        steps = data["jobs"]["generate-snake"]["steps"]
        for step in steps:
            if "Platane/snk" in step.get("uses", ""):
                return step
        pytest.fail("Platane/snk step not found")

    @pytest.fixture(scope="class")
    def push_step(self):
        data = load_yaml(SNAKE_WORKFLOW)
        steps = data["jobs"]["generate-snake"]["steps"]
        for step in steps:
            if "ghaction-github-pages" in step.get("uses", ""):
                return step
        pytest.fail("ghaction-github-pages step not found")

    def test_snake_github_user_is_correct(self, snake_step):
        user = snake_step["with"].get("github_user_name", "")
        assert user == "semmozhiyan-dev", \
            "Snake action github_user_name must be 'semmozhiyan-dev'"

    def test_snake_outputs_regular_svg(self, snake_step):
        outputs = snake_step["with"].get("outputs", "")
        assert "github-contribution-grid-snake.svg" in outputs, \
            "Snake action must output regular SVG"

    def test_snake_outputs_dark_svg(self, snake_step):
        outputs = snake_step["with"].get("outputs", "")
        assert "github-contribution-grid-snake-dark.svg" in outputs, \
            "Snake action must output dark-mode SVG"

    def test_snake_dark_uses_github_dark_palette(self, snake_step):
        outputs = snake_step["with"].get("outputs", "")
        assert "palette=github-dark" in outputs, \
            "Dark snake SVG must use palette=github-dark"

    def test_push_targets_output_branch(self, push_step):
        branch = push_step["with"].get("target_branch", "")
        assert branch == "output", \
            "Pages push step must target branch 'output'"

    def test_push_uses_github_token(self, push_step):
        env = push_step.get("env", {})
        token = env.get("GITHUB_TOKEN", "")
        assert "secrets.GITHUB_TOKEN" in token, \
            "Pages push step must use ${{ secrets.GITHUB_TOKEN }}"
