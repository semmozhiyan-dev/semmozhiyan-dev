"""
Tests for README.md — validates structure, sections, badges, links, and content.
"""

import re
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).parent.parent
README = REPO_ROOT / "README.md"


@pytest.fixture(scope="module")
def readme_text():
    return README.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# File-level checks
# ---------------------------------------------------------------------------

class TestReadmeExists:
    def test_readme_file_exists(self):
        assert README.exists(), "README.md must exist at the repository root"

    def test_readme_is_not_empty(self, readme_text):
        assert len(readme_text.strip()) > 0, "README.md must not be empty"

    def test_readme_is_utf8(self):
        # Reading with utf-8 encoding above would raise if invalid; this confirms it
        content = README.read_text(encoding="utf-8")
        assert isinstance(content, str)


# ---------------------------------------------------------------------------
# Section headings
# ---------------------------------------------------------------------------

EXPECTED_SECTIONS = [
    "About Me",
    "Tech Stack",
    "GitHub Stats",
    "GitHub Trophies",
    "Contribution Activity",
    "GitHub Performance Dashboard",
    "GitHub Analytics Dashboard",
    "Contribution Snake",
    "Featured Projects",
    "DevOps Practice",
    "Currently Learning",
    "Connect With Me",
]


class TestReadmeSections:
    @pytest.mark.parametrize("section", EXPECTED_SECTIONS)
    def test_section_present(self, readme_text, section):
        assert section in readme_text, f"README.md must contain section: '{section}'"

    def test_has_html_headings_or_md_headings(self, readme_text):
        has_md_heading = re.search(r"^#{1,3} ", readme_text, re.MULTILINE) is not None
        has_html_heading = re.search(r"<h[1-6]", readme_text, re.IGNORECASE) is not None
        assert has_md_heading or has_html_heading, "README.md must contain at least one heading"


# ---------------------------------------------------------------------------
# Personal information
# ---------------------------------------------------------------------------

class TestPersonalInfo:
    def test_name_present(self, readme_text):
        assert "Semmozhiyan" in readme_text, "Author name must appear in README.md"

    def test_role_devops(self, readme_text):
        assert "DevOps" in readme_text, "Role 'DevOps' must be mentioned"

    def test_role_backend(self, readme_text):
        assert "Backend" in readme_text, "Role 'Backend' must be mentioned"

    def test_location_india(self, readme_text):
        assert "India" in readme_text, "Location 'India' must be mentioned"

    def test_timezone_mentioned(self, readme_text):
        assert "Asia/Kolkata" in readme_text or "IST" in readme_text, \
            "Timezone must be mentioned"

    def test_education_mentioned(self, readme_text):
        assert "Computer Science" in readme_text or "B.E." in readme_text, \
            "Education must be mentioned"


# ---------------------------------------------------------------------------
# Tech stack badges
# ---------------------------------------------------------------------------

EXPECTED_TECH = [
    "Java",
    "Python",
    "Docker",
    "Kubernetes",
    "GitHub%20Actions",
    "Terraform",
    "Flask",
    "Django",
    "Node.js",
    "MySQL",
    "PostgreSQL",
    "Linux",
    "Nginx",
    "Prometheus",
    "Grafana",
]


class TestTechStack:
    @pytest.mark.parametrize("tech", EXPECTED_TECH)
    def test_tech_badge_present(self, readme_text, tech):
        assert tech in readme_text, f"Tech badge for '{tech}' must be present"

    def test_shields_io_badges_present(self, readme_text):
        assert "img.shields.io" in readme_text, \
            "shields.io badge URLs must be present"

    def test_for_the_badge_style_used(self, readme_text):
        assert "for-the-badge" in readme_text, \
            "Badges must use 'for-the-badge' style"


# ---------------------------------------------------------------------------
# GitHub stats integrations
# ---------------------------------------------------------------------------

class TestGitHubStats:
    def test_github_readme_stats_present(self, readme_text):
        assert "github-readme-stats.vercel.app" in readme_text, \
            "github-readme-stats widget must be embedded"

    def test_streak_stats_present(self, readme_text):
        assert "github-readme-streak-stats.herokuapp.com" in readme_text or \
               "streak-stats" in readme_text, \
            "GitHub streak stats widget must be embedded"

    def test_trophies_present(self, readme_text):
        assert "github-profile-trophy.vercel.app" in readme_text, \
            "GitHub trophies widget must be embedded"

    def test_activity_graph_present(self, readme_text):
        assert "github-readme-activity-graph.vercel.app" in readme_text, \
            "GitHub activity graph must be embedded"

    def test_profile_summary_cards_present(self, readme_text):
        assert "github-profile-summary-cards.vercel.app" in readme_text, \
            "GitHub profile summary cards must be embedded"

    def test_metrics_svg_referenced(self, readme_text):
        assert "github-metrics.svg" in readme_text, \
            "github-metrics.svg must be referenced in README.md"

    def test_username_in_stat_urls(self, readme_text):
        assert "semmozhiyan-dev" in readme_text, \
            "GitHub username must appear in stat widget URLs"


# ---------------------------------------------------------------------------
# Animated elements
# ---------------------------------------------------------------------------

class TestAnimations:
    def test_capsule_render_header(self, readme_text):
        assert "capsule-render.vercel.app" in readme_text, \
            "Animated banner via capsule-render must be present"

    def test_typing_animation_present(self, readme_text):
        assert "readme-typing-svg.demolab.com" in readme_text, \
            "Typing animation SVG must be present"

    def test_snake_animation_referenced(self, readme_text):
        assert "github-contribution-grid-snake" in readme_text, \
            "Contribution snake animation must be referenced"

    def test_snake_dark_mode_variant(self, readme_text):
        assert "github-contribution-grid-snake-dark.svg" in readme_text, \
            "Dark-mode snake SVG variant must be referenced"

    def test_picture_tag_for_snake(self, readme_text):
        assert "<picture>" in readme_text, \
            "Snake animation must use <picture> for dark/light mode switching"

    def test_profile_views_badge(self, readme_text):
        assert "komarev.com/ghpvc" in readme_text, \
            "Profile views counter badge must be present"

    def test_followers_badge_present(self, readme_text):
        assert "followers" in readme_text.lower(), \
            "Followers badge must be present"


# ---------------------------------------------------------------------------
# Contact / social links
# ---------------------------------------------------------------------------

EXPECTED_LINKS = [
    "mailto:semmozhiyan40@gmail.com",
    "linkedin.com/in/semmozhiyan",
    "instagram.com",
    "github.com/semmozhiyan-dev",
]


class TestContactInfo:
    @pytest.mark.parametrize("link", EXPECTED_LINKS)
    def test_contact_link_present(self, readme_text, link):
        assert link in readme_text, f"Contact link '{link}' must be present"

    def test_gmail_badge_present(self, readme_text):
        assert "Gmail" in readme_text, "Gmail badge must be present"

    def test_linkedin_badge_present(self, readme_text):
        assert "LinkedIn" in readme_text, "LinkedIn badge must be present"

    def test_instagram_badge_present(self, readme_text):
        assert "Instagram" in readme_text, "Instagram badge must be present"

    def test_github_badge_present(self, readme_text):
        assert "GitHub" in readme_text, "GitHub badge must be present in contact section"


# ---------------------------------------------------------------------------
# Featured projects
# ---------------------------------------------------------------------------

class TestFeaturedProjects:
    def test_wanderlite_project_present(self, readme_text):
        assert "wanderlite-travel-and-tourism" in readme_text, \
            "WanderLite project must be featured"

    def test_portfolio_project_present(self, readme_text):
        assert "semmozhi-portfolio" in readme_text, \
            "Portfolio project must be featured"

    def test_project_table_present(self, readme_text):
        assert "WanderLite" in readme_text and "Portfolio" in readme_text, \
            "Featured project comparison table must be present"

    def test_project_tech_labels(self, readme_text):
        assert "JavaScript" in readme_text, \
            "Project tech labels (JavaScript) must be present"

    def test_view_repo_buttons(self, readme_text):
        assert "View%20Repo" in readme_text or "View Repo" in readme_text, \
            "View Repo buttons must be present for featured projects"


# ---------------------------------------------------------------------------
# DevOps labs table
# ---------------------------------------------------------------------------

EXPECTED_DEVOPS_ENTRIES = [
    "CI/CD",
    "Docker",
    "Kubernetes",
    "Prometheus",
    "Terraform",
    "Linux",
]


class TestDevOpsLabs:
    @pytest.mark.parametrize("entry", EXPECTED_DEVOPS_ENTRIES)
    def test_devops_entry_present(self, readme_text, entry):
        assert entry in readme_text, \
            f"DevOps labs table must mention '{entry}'"


# ---------------------------------------------------------------------------
# Currently learning section
# ---------------------------------------------------------------------------

EXPECTED_LEARNING = [
    "Kubernetes",
    "Terraform",
    "Linux",
    "DevSecOps",
]


class TestCurrentlyLearning:
    @pytest.mark.parametrize("topic", EXPECTED_LEARNING)
    def test_learning_topic_present(self, readme_text, topic):
        assert topic in readme_text, \
            f"Currently learning section must mention '{topic}'"


# ---------------------------------------------------------------------------
# HTML structure / layout
# ---------------------------------------------------------------------------

class TestHtmlStructure:
    def test_center_alignment_used(self, readme_text):
        assert '<div align="center">' in readme_text, \
            "README must use centered div alignment for layout"

    def test_html_comments_present(self, readme_text):
        assert "<!--" in readme_text, \
            "Section separator HTML comments must be present"

    def test_footer_present(self, readme_text):
        assert "section=footer" in readme_text or "footer" in readme_text.lower(), \
            "Animated footer must be present"

    def test_powered_by_attribution(self, readme_text):
        assert "lowlighter/metrics" in readme_text, \
            "Attribution to lowlighter/metrics must be present"

    def test_snake_attribution(self, readme_text):
        assert "Platane/snk" in readme_text, \
            "Attribution to Platane/snk must be present"

    def test_auto_refresh_note(self, readme_text):
        assert "Auto-refreshed" in readme_text or "auto-refreshed" in readme_text, \
            "Auto-refresh note must be present in footer"

    def test_key_images_have_alt_text(self, readme_text):
        """Key semantic images (stats widgets, animated cards) must carry alt text.
        Decorative badge images are exempt as they are self-descriptive by URL."""
        key_patterns = [
            "GitHub Stats",
            "Top Languages",
            "GitHub Streak",
            "Trophies",
            "Activity Graph",
            "Profile Details",
            "Typing SVG",
            "Contribution Snake Animation",
        ]
        for label in key_patterns:
            assert f'alt="{label}"' in readme_text or f"alt='{label}'" in readme_text, \
                f"Key image with alt='{label}' must be present"
