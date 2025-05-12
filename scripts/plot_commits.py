from ghweekly.main import fetch_weekly_commits
import matplotlib.pyplot as plt
from datetime import datetime
import os

USERNAME = "bhimrazy"
REPOS = [
    "Lightning-AI/litdata",
    "Lightning-AI/LitServe",
    "Lightning-AI/litgpt",
    "Lightning-AI/LitModels",
    "Lightning-AI/pytorch-lightning",
]

GH_TOKEN = os.getenv("GH_TOKEN")
HEADERS = {'Authorization': f'token {GH_TOKEN}'} if GH_TOKEN else {}

START = datetime(2025, 1, 1)
END = datetime.now()

df = fetch_weekly_commits(USERNAME, REPOS, START, END, HEADERS)

plt.figure(figsize=(14,6))
ax = df.plot(
    kind='bar',
    stacked=True,
    width=0.8,
    colormap='tab20',
    edgecolor='none',
    ax=plt.gca()
)

for patch in ax.patches:
    h = patch.get_height()
    if h > 0:
        x = patch.get_x() + patch.get_width()/2
        y = patch.get_y() + h/2
        ax.text(x, y, int(h), ha='center', va='center', fontsize=8, color='white')

ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in df.index], rotation=45, ha='right')
plt.title(f'Weekly GitHub Contributions by Repo ({USERNAME})', fontsize=16, pad=20)
plt.xlabel('Start of the week (Monday)')
plt.ylabel('Merged Commits')
plt.tight_layout()
plt.savefig('weekly_commits.png', dpi=300)
plt.show()
