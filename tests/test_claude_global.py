"""Checks for the global Claude Code kit in claude-global/.

These can't run the PowerShell installer, but they catch the mistakes that would
break it: invalid JSON, a skill without a name/description, or a missing file.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
KIT = ROOT / "claude-global"


def test_settings_is_valid_json_with_permission_lists():
    settings = json.loads((KIT / "settings.json").read_text(encoding="utf-8"))
    for name in ("allow", "ask", "deny"):
        rules = settings["permissions"][name]
        assert rules and all(isinstance(r, str) for r in rules)
        # Every rule looks like Tool(pattern), e.g. Bash(git status*) or Read(**/.env)
        assert all(re.fullmatch(r"(Bash|Read|Edit)\(.+\)", r) for r in rules), name
    # A rule must not be both allowed and denied.
    assert not set(settings["permissions"]["allow"]) & set(settings["permissions"]["deny"])
    # No Co-Authored-By trailer (matches the rule in CLAUDE.md).
    assert settings["attribution"] == {"commit": "", "pr": ""}


def test_secrets_and_force_push_are_denied():
    deny = json.loads((KIT / "settings.json").read_text(encoding="utf-8"))["permissions"]["deny"]
    assert "Read(**/.env)" in deny
    assert "Bash(git push --force*)" in deny


def test_every_skill_has_name_and_description():
    skills = [d for d in (KIT / "skills").iterdir() if d.is_dir()]
    assert len(skills) >= 4
    for skill in skills:
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        front = re.match(r"---\n(.*?)\n---\n", text, re.S)
        assert front, f"{skill.name}: SKILL.md needs a --- front matter block"
        fields = dict(line.split(":", 1) for line in front.group(1).splitlines())
        assert fields["name"].strip() == skill.name  # folder name and skill name must match
        assert len(fields["description"].strip()) > 50


def test_installer_finds_every_file_it_copies():
    # install.ps1 copies these from the repo's video/ folder into the stickman-video skill.
    for name in ("draw.js", "make_video.py", "stage.html", "requirements.txt", "scenes.js",
                 "assets/patrick-hand.woff2", "assets/patrick-hand-OFL.txt"):
        assert (ROOT / "video" / name).exists(), name
    assert (KIT / "CLAUDE.md").exists()
