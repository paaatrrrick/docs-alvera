import os, re, subprocess, sys

BANNED = ["simply", "just", "easy", "obviously"]
MARKER = "{/* reviewed-by: docs-rules */}"
base = os.environ["BASE_REF"]
changed = subprocess.run(
    ["git", "diff", "--name-only", "--diff-filter=AM", f"origin/{base}...HEAD", "--", "misc/autopilot-e2e/"],
    capture_output=True, text=True, check=True,
).stdout.split()
errors = 0

def fail(path, line, message):
    global errors
    errors += 1
    print(f"::error file={path},line={line},title=docs-rules::{message}")
    print(f"{path}:{line}: {message}")

for path in changed:
    if not path.endswith(".mdx"):
        continue
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    front = match.group(1) if match else ""
    desc = re.search(r"^description:\s*[\"']?(.*?)[\"']?\s*$", front, re.M)
    if not desc:
        fail(path, 1, "Frontmatter must have a description (20 to 160 characters).")
    elif not 20 <= len(desc.group(1)) <= 160:
        fail(path, 1, f"Description is {len(desc.group(1))} characters; it must be 20 to 160.")
    for number, line in enumerate(lines, 1):
        for word in BANNED:
            if re.search(rf"\b{word}\b", line, re.I):
                fail(path, number, f'Banned word "{word}": the style guide forbids minimizing words.')
    if MARKER not in text:
        fail(path, len(lines), f"Every page under misc/autopilot-e2e/ must end with the line {MARKER}")

print(f"docs-rules: {len(changed)} file(s) checked, {errors} error(s)")
sys.exit(1 if errors else 0)
