import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Fetch weekly GitHub commits for a user across multiple repos."
    )
    parser.add_argument("--username", required=True, help="GitHub username")
    parser.add_argument(
        "--repos",
        nargs="+",
        required=True,
        help="List of GitHub repositories (org/repo)",
    )
    from datetime import datetime
    current_year_start = f"{datetime.now().year}-01-01"
    parser.add_argument(
        "--start",
        required=False,
        default=current_year_start,
        help=f"Start date (YYYY-MM-DD), default: {current_year_start}"
    )
    parser.add_argument(
        "--end",
        default=None,
        help="End date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--token", help="GitHub token (optional, for higher rate limits)"
    )
    parser.add_argument("--plot", action="store_true", help="Show plot")
    parser.add_argument(
        "--include-committer", 
        action="store_true", 
        help="Include commits where user is the committer (e.g., PR merge commits). Default: only authored commits"
    )

    args = parser.parse_args()

    # Only import heavy modules after parsing args for fast help/parse
    from datetime import datetime

    from ghweekly.main import fetch_weekly_commits

    # Only import matplotlib if plotting is requested
    if args.plot:
        import matplotlib.pyplot as plt

    end_date = args.end or datetime.now().strftime("%Y-%m-%d")
    headers = {"Authorization": f"token {args.token}"} if args.token else {}
    df = fetch_weekly_commits(
        username=args.username,
        repos=args.repos,
        start=datetime.fromisoformat(args.start),
        end=datetime.fromisoformat(end_date),
        headers=headers,
        include_committer=args.include_committer,
    )

    print(df)

    # generate plots
    if args.plot:
        ax = df.plot(
            kind="bar", stacked=True, figsize=(14, 6), colormap="tab20", width=0.8
        )
        for patch in ax.patches:
            h = patch.get_height()
            if h > 0:
                x = patch.get_x() + patch.get_width() / 2
                y = patch.get_y() + h / 2
                ax.text(
                    x, y, int(h), ha="center", va="center", fontsize=8, color="white"
                )
        ax.set_xticklabels(
            [d.strftime("%Y-%m-%d") for d in df.index], rotation=45, ha="right"
        )
        plt.title(f"Weekly GitHub Contributions by Repo ({args.username})")
        plt.xlabel("Start of the week (Monday)")
        plt.ylabel("Merged Commits")
        plt.tight_layout()
        plt.savefig("weekly_commits.png", dpi=300)
        plt.show()


if __name__ == "__main__":
    main()
