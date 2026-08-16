"""Public profile facts. Keep private vault details out of this file."""

from datetime import date

USERNAME = "AnmolKamboj"
FULL_NAME = "Anmol Kamboj"
HANDLE = "anmol@ops"
TITLE = "Software Engineer"
FOCUS = "Agentic AI · Cloud Security"
LOCATION = "Boca Raton, Florida"
EMAIL = "anmolkamboj@gmail.com"
PORTFOLIO = "https://portfolio-nine-lovat-52.vercel.app/"
LINKEDIN = "https://www.linkedin.com/in/anm0lkamb0j"
GITHUB = f"https://github.com/{USERNAME}"

BIRTHDAY = date(2000, 8, 28)

EDUCATION = [
    {
        "school": "Florida Atlantic University",
        "credential": "M.S. Computer Science",
        "when": "2024 — May 2026",
        "note": "GPA 3.90 / 4.0",
    },
    {
        "school": "Chandigarh University",
        "credential": "B.E. Computer Science · Gaming & Graphics",
        "when": "— June 2023",
        "note": "GPA 3.04 / 4.0",
    },
]

WORK = [
    {
        "org": "Penti.AI",
        "role": "Agentic AI & Full Stack Developer",
        "when": "Jun 2025 — Present",
        "where": "Boca Raton, FL",
        "summary": "Building an agentic penetration-testing platform: recon, contextual scanning, validation, and reports people can actually use.",
    },
    {
        "org": "FourKites",
        "role": "Software Engineer",
        "when": "Aug 2022 — May 2023",
        "where": "Chennai, India",
        "summary": "Appointment Manager for carrier pickup and drop-off tracking. Go, Python, HTML. Cut performance time ~15% and automated 50 existing flows.",
    },
]

PROJECTS = [
    {
        "name": "Jarvis",
        "status": "building",
        "summary": "A Telegram-native personal agent with persistent context, so I stop re-briefing a new chat every hour.",
    },
    {
        "name": "Penti.AI",
        "status": "production",
        "summary": "Multi-step agent workflows for automated reconnaissance, vulnerability scanning, exploitation logic, and reporting.",
    },
]

STACK = {
    "Interface": ["React", "Next.js", "TypeScript", "Tailwind"],
    "Systems": ["Python", "Go", "SQL", "Flask", "REST"],
    "Cloud": ["AWS", "Docker", "CI/CD", "IAM", "GCP"],
    "Agents": ["LLM tooling", "orchestration", "tool calling"],
}

# Midnight brass — not the usual purple GitHub-stats look.
PALETTE = {
    "bg": (6, 9, 16),
    "panel": (11, 16, 27),
    "grid": (18, 24, 34),
    "line": (36, 48, 66),
    "text": (226, 232, 240),
    "muted": (148, 163, 184),
    "dim": (94, 108, 128),
    "brass": (232, 197, 106),
    "brass_dim": (168, 132, 58),
    "cyan": (94, 234, 212),
    "cyan_dim": (45, 122, 122),
    "rose": (251, 113, 133),
    "ink": (8, 11, 18),
    "square_dark": (16, 22, 34),
    "square_light": (30, 41, 59),
    "piece_light": (240, 220, 160),
    "piece_dark": (125, 147, 181),
}
