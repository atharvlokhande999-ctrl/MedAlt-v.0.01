import requests
import os

# ---------------- CONFIG ----------------
MODE = os.getenv("MODE", "local")  # "local" or "github"
REPO = os.getenv("REPO", "Atharva-U12")

headers = {
    "Authorization": f"token {os.getenv('GITHUB_TOKEN')}"
}

# ---------------- LOCAL MODE ----------------
def get_local_leaderboard():
    leaderboard = {}
    folder = "submissions"

    if not os.path.exists(folder):
        return leaderboard

    for user_folder in os.listdir(folder):
        path = os.path.join(folder, user_folder, "results.txt")

        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    if "score" in line.lower():
                        score = float(line.split(":")[1].strip())
                        leaderboard[user_folder] = score

    return leaderboard


# ---------------- GITHUB MODE ----------------
def get_github_leaderboard():
    prs_url = f"https://api.github.com/repos/{REPO}/pulls?state=closed"
    response = requests.get(prs_url, headers=headers)

    if response.status_code != 200:
        print("Error fetching PRs:", response.text)
        return {}

    prs = response.json()
    leaderboard = {}

    for pr in prs:
        if pr.get("merged_at"):
            username = pr["user"]["login"]

            files_url = pr["url"] + "/files"
            files = requests.get(files_url, headers=headers).json()

            for file in files:
                if "results.txt" in file["filename"]:
                    raw_url = file["raw_url"]
                    content = requests.get(raw_url).text

                    for line in content.split("\n"):
                        if "score" in line.lower():
                            try:
                                score = float(line.split(":")[1].strip())

                                if username not in leaderboard or score > leaderboard[username]:
                                    leaderboard[username] = score
                            except:
                                pass

    return leaderboard


# ---------------- README UPDATE ----------------
def update_readme(leaderboard):
    sorted_lb = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

    leaderboard_md = "## 🏆 Leaderboard\n\n"
    leaderboard_md += "| Rank | User | Score |\n"
    leaderboard_md += "|------|------|-------|\n"

    for i, (user, score) in enumerate(sorted_lb, start=1):
        leaderboard_md += f"| {i} | {user} | {score} |\n"

    start = "<!-- LEADERBOARD_START -->"
    end = "<!-- LEADERBOARD_END -->"

    if not os.path.exists("README.md"):
        with open("README.md", "w") as f:
            f.write(start + "\n" + leaderboard_md + "\n" + end)
        return

    with open("README.md", "r") as f:
        content = f.read()

    if start in content and end in content:
        new_content = (
            content.split(start)[0]
            + start + "\n"
            + leaderboard_md + "\n"
            + end
            + content.split(end)[1]
        )
    else:
        new_content = content + "\n\n" + start + "\n" + leaderboard_md + "\n" + end

    with open("README.md", "w") as f:
        f.write(new_content)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    if MODE == "local":
        leaderboard = get_local_leaderboard()
        print("Running in LOCAL mode")

    else:
        leaderboard = get_github_leaderboard()
        print("Running in GITHUB mode")

    update_readme(leaderboard)