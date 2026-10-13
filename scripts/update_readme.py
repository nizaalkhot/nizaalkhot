#!/usr/bin/env python3
"""
Dynamic GitHub Profile README Updater
Fetches recent projects, repositories, and activity from GitHub API,
dynamically computes career years of experience starting from May 2022,
formats them into rich markdown cards and badges, and injects them into README.md.
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

USERNAME = "nizaalkhot"
PROFILE_REPO = "nizaalkhot"
CAREER_START_DATE = datetime(2022, 5, 1, tzinfo=timezone.utc)
MAX_PROJECTS = 6
MAX_ACTIVITIES = 5

TECH_BADGES = {
    "python": "https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white",
    "langgraph": "https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white",
    "langchain": "https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white",
    "crewai": "https://img.shields.io/badge/CrewAI-FF4F00?style=flat-square&logo=robot&logoColor=white",
    "dspy": "https://img.shields.io/badge/DSPy-8A2BE2?style=flat-square&logo=python&logoColor=white",
    "pytorch": "https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white",
    "tensorflow": "https://img.shields.io/badge/TensorFlow-FF6F00?style=flat-square&logo=tensorflow&logoColor=white",
    "fastapi": "https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white",
    "docker": "https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white",
    "kubernetes": "https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white",
    "aws": "https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazon-aws&logoColor=white",
    "azure": "https://img.shields.io/badge/Azure-0078D4?style=flat-square&logo=microsoft-azure&logoColor=white",
    "gcp": "https://img.shields.io/badge/GCP-4285F4?style=flat-square&logo=google-cloud&logoColor=white",
    "bedrock": "https://img.shields.io/badge/AWS%20Bedrock-232F3E?style=flat-square&logo=amazon-aws&logoColor=white",
    "sagemaker": "https://img.shields.io/badge/SageMaker-232F3E?style=flat-square&logo=amazon-aws&logoColor=white",
    "rag": "https://img.shields.io/badge/RAG-7928CA?style=flat-square&logo=databricks&logoColor=white",
    "llm": "https://img.shields.io/badge/LLM-8A2BE2?style=flat-square&logo=openai&logoColor=white",
    "genai": "https://img.shields.io/badge/GenAI-412991?style=flat-square&logo=google&logoColor=white",
    "agentic": "https://img.shields.io/badge/Agentic-00C49F?style=flat-square&logo=probot&logoColor=white",
    "javascript": "https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black",
    "typescript": "https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white",
    "neo4j": "https://img.shields.io/badge/Neo4j-008CC1?style=flat-square&logo=neo4j&logoColor=white",
    "postgresql": "https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white",
    "pinecone": "https://img.shields.io/badge/Pinecone-000000?style=flat-square&logo=pinecone&logoColor=white",
    "jenkins": "https://img.shields.io/badge/Jenkins-D24939?style=flat-square&logo=jenkins&logoColor=white",
    "gitlab": "https://img.shields.io/badge/GitLab-FC6D26?style=flat-square&logo=gitlab&logoColor=white",
}


def calculate_years_experience() -> str:
    """Calculate dynamic years of experience starting from May 2022."""
    now = datetime.now(timezone.utc)
    total_months = (now.year - CAREER_START_DATE.year) * 12 + (now.month - CAREER_START_DATE.month)
    years = total_months / 12.0
    return f"{int(years)}+"


def generate_experience_badge(years_str: str) -> str:
    """Generate a clean Shields.io badge with properly encoded text."""
    encoded_val = years_str.replace("+", "%2B")
    return f'<img src="https://img.shields.io/badge/Experience-{encoded_val}%20Years-0078D4?style=flat-square" alt="Years of Experience" />'


def make_request(url: str):
    """Execute an HTTP request to the GitHub API with optional auth token."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {
        "User-Agent": "nizaalkhot-profile-updater",
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code} for URL {url}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None


def fetch_repositories():
    """Fetch public repositories and sort by featured topic and recent activity."""
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=pushed&direction=desc"
    repos = make_request(url)
    if not repos:
        return []

    valid_repos = []
    priority_topics = {"featured", "portfolio", "showcase", "genai", "agent", "agents", "langgraph", "rag"}

    for r in repos:
        if r.get("fork") or r.get("archived") or r.get("name") == PROFILE_REPO:
            continue

        topics = set(r.get("topics", []))
        is_priority = bool(topics & priority_topics)

        score = (100 if is_priority else 0) + (r.get("stargazers_count", 0) * 10)
        valid_repos.append((score, r))

    valid_repos.sort(
        key=lambda item: (item[0], item[1].get("pushed_at", "")),
        reverse=True
    )

    return [item[1] for item in valid_repos[:MAX_PROJECTS]]


def get_badges_for_repo(repo):
    """Generate markdown badges based on language and topics."""
    badges = []
    language = repo.get("language")
    if language:
        lang_key = language.lower()
        if lang_key in TECH_BADGES:
            badges.append(f"![]({TECH_BADGES[lang_key]})")
        else:
            badges.append(f"![{language}](https://img.shields.io/badge/-{language}-333333?style=flat-square)")

    topics = repo.get("topics", [])
    for t in topics:
        t_key = t.lower()
        if t_key in TECH_BADGES and t_key != (language.lower() if language else ""):
            badges.append(f"![]({TECH_BADGES[t_key]})")
        elif t_key in {"crewai", "langchain", "dspy", "ragas", "weaviate", "pinecone", "neo4j", "graphiti"}:
            badges.append(f"![{t}](https://img.shields.io/badge/-{t}-412991?style=flat-square)")

    if not badges:
        badges.append("![AI Project](https://img.shields.io/badge/Domain-AI%2FML-107C41?style=flat-square)")

    return " ".join(badges[:3])


def format_date(iso_str):
    """Format an ISO 8601 date string to readable YYYY-MM-DD."""
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return iso_str[:10]


def generate_projects_markdown(repos):
    """Build a clean responsive markdown table for projects."""
    if not repos:
        return "_No public repositories found to display._\n"

    lines = [
        "| Project | Description | Tech Stack | Stats | Updated |",
        "| :--- | :--- | :--- | :---: | :---: |",
    ]

    for r in repos:
        name = r.get("name", "Unknown")
        repo_url = r.get("html_url", "#")
        homepage = r.get("homepage")
        description = r.get("description") or "Autonomous AI & Generative AI project."
        if len(description) > 90:
            description = description[:87] + "..."

        title_col = f"**[{name}]({repo_url})**"
        if homepage:
            title_col += f"<br>🌐 [Live Demo]({homepage})"

        badges_col = get_badges_for_repo(r)
        stars = r.get("stargazers_count", 0)
        forks = r.get("forks_count", 0)
        stats_col = f"⭐ `{stars}` &nbsp; 🍴 `{forks}`"
        updated_col = f"`{format_date(r.get('pushed_at'))}`"

        clean_desc = description.replace("|", "\\|")
        lines.append(f"| {title_col} | {clean_desc} | {badges_col} | {stats_col} | {updated_col} |")

    return "\n".join(lines) + "\n"


def fetch_recent_activity():
    """Fetch recent public events for the user."""
    url = f"https://api.github.com/users/{USERNAME}/events/public?per_page=30"
    events = make_request(url)
    if not events:
        return []

    activity_items = []
    seen_repos = set()

    for event in events:
        event_type = event.get("type")
        repo_name = event.get("repo", {}).get("name", "")
        repo_short = repo_name.split("/")[-1] if "/" in repo_name else repo_name
        repo_url = f"https://github.com/{repo_name}"
        created_at = format_date(event.get("created_at"))

        if repo_short == PROFILE_REPO:
            continue

        item_str = None
        if event_type == "PushEvent":
            commits = event.get("payload", {}).get("commits", [])
            msg = commits[0].get("message", "Recent changes").split("\n")[0] if commits else "Pushed new updates"
            if len(msg) > 60:
                msg = msg[:57] + "..."
            item_str = f"- 🔨 Pushed to **[{repo_short}]({repo_url})**: `{msg}` — *{created_at}*"
        elif event_type == "CreateEvent":
            ref_type = event.get("payload", {}).get("ref_type", "branch")
            if ref_type == "repository":
                item_str = f"- 🚀 Created new repository **[{repo_short}]({repo_url})** — *{created_at}*"
            elif ref_type == "tag":
                ref = event.get("payload", {}).get("ref", "new release")
                item_str = f"- 🏷️ Created tag `{ref}` in **[{repo_short}]({repo_url})** — *{created_at}*"
        elif event_type == "ReleaseEvent":
            rel_name = event.get("payload", {}).get("release", {}).get("name") or "New Release"
            item_str = f"- 📦 Published release `{rel_name}` in **[{repo_short}]({repo_url})** — *{created_at}*"
        elif event_type == "PullRequestEvent":
            action = event.get("payload", {}).get("action", "opened")
            pr_title = event.get("payload", {}).get("pull_request", {}).get("title", "")
            item_str = f"- 🔀 {action.capitalize()} PR in **[{repo_short}]({repo_url})**: `{pr_title}` — *{created_at}*"

        if item_str and repo_short not in seen_repos:
            seen_repos.add(repo_short)
            activity_items.append(item_str)
            if len(activity_items) >= MAX_ACTIVITIES:
                break

    return activity_items


def generate_activity_markdown(activities):
    """Build markdown list for recent activities."""
    if not activities:
        return "_No recent public activity recorded._\n"
    return "\n".join(activities) + "\n"


def replace_section(content: str, marker_name: str, replacement: str) -> str:
    """Replace content between HTML comment markers."""
    start_tag = f"<!-- {marker_name}:START -->"
    end_tag = f"<!-- {marker_name}:END -->"
    pattern = rf"({re.escape(start_tag)})(.*?)({re.escape(end_tag)})"
    
    if not re.search(pattern, content, flags=re.DOTALL):
        print(f"Warning: Marker '{marker_name}' not found in content.", file=sys.stderr)
        return content

    return re.sub(
        pattern,
        lambda m: f"{m.group(1)}\n{replacement.strip()}\n{m.group(3)}",
        content,
        flags=re.DOTALL
    )


def replace_all_occurrences(content: str, marker_name: str, replacement: str) -> str:
    """Replace all instances of an inline comment marker pair with replacement."""
    start_tag = f"<!-- {marker_name}:START -->"
    end_tag = f"<!-- {marker_name}:END -->"
    pattern = rf"({re.escape(start_tag)})(.*?)({re.escape(end_tag)})"

    return re.sub(
        pattern,
        lambda m: f"{m.group(1)}{replacement.strip()}{m.group(3)}",
        content,
        flags=re.DOTALL
    )


def update_readme():
    """Main execution entry point."""
    readme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")
    if not os.path.exists(readme_path):
        print(f"Error: README.md not found at {readme_path}", file=sys.stderr)
        sys.exit(1)

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    print("Computing dynamic years of experience...")
    years_exp = calculate_years_experience()
    print(f"Computed Experience: {years_exp} years (since May 2022)")

    exp_badge_md = generate_experience_badge(years_exp)

    print("Fetching repositories...")
    repos = fetch_repositories()
    projects_md = generate_projects_markdown(repos)

    print("Fetching recent activities...")
    activities = fetch_recent_activity()
    activity_md = generate_activity_markdown(activities)

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    last_updated_md = f"⚡ *Automated with GitHub Actions • Last synced: `{now_utc}`*"

    # Inject dynamic content
    updated_content = replace_section(content, "EXPERIENCE_BADGE", exp_badge_md)
    updated_content = replace_all_occurrences(updated_content, "YEARS_OF_EXPERIENCE", years_exp)
    updated_content = replace_section(updated_content, "RECENT_PROJECTS", projects_md)
    updated_content = replace_section(updated_content, "RECENT_ACTIVITY", activity_md)
    updated_content = replace_section(updated_content, "LAST_UPDATED", last_updated_md)

    if updated_content != content:
        with open(readme_path, "r+", encoding="utf-8") as f:
            f.seek(0)
            f.write(updated_content)
            f.truncate()
        print("Successfully updated README.md with fresh dynamic content!")
    else:
        print("README.md is already up-to-date.")


if __name__ == "__main__":
    update_readme()
