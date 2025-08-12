"""Plotting utilities for GitHub activity visualization."""

import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional


def create_weekly_commits_plot(
    df: pd.DataFrame,
    username: str,
    title: Optional[str] = None,
    figsize: tuple = (14, 6),
    colormap: str = "tab20",
    output_file: Optional[str] = None,
    show_plot: bool = True,
) -> None:
    """Create a stacked bar plot of weekly commits.

    Args:
        df: DataFrame with weekly commit data
        username: GitHub username for the plot title
        title: Custom title for the plot
        figsize: Figure size as (width, height)
        colormap: Matplotlib colormap name
        output_file: File path to save the plot (optional)
        show_plot: Whether to display the plot
    """
    if df.empty:
        plt.figure(figsize=figsize)
        plt.text(
            0.5,
            0.5,
            "No data to display",
            ha="center",
            va="center",
            transform=plt.gca().transAxes,
            fontsize=16,
        )
        plt.title(title or f"Weekly GitHub Contributions ({username})")
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
        if show_plot:
            plt.show()
        return

    plt.figure(figsize=figsize)
    ax = df.plot(
        kind="bar",
        stacked=True,
        width=0.8,
        colormap=colormap,
        edgecolor="none",
        ax=plt.gca(),
    )

    # Add value labels on bars
    for patch in ax.patches:
        height = patch.get_height()
        if height > 0:
            x = patch.get_x() + patch.get_width() / 2
            y = patch.get_y() + height / 2
            ax.text(
                x,
                y,
                int(height),
                ha="center",
                va="center",
                fontsize=8,
                color="white",
                weight="bold",
            )

    # Format x-axis labels
    ax.set_xticklabels(
        [d.strftime("%Y-%m-%d") for d in df.index], rotation=45, ha="right"
    )

    # Set labels and title
    plot_title = title or f"Weekly GitHub Contributions by Repo ({username})"
    plt.title(plot_title, fontsize=16, pad=20)
    plt.xlabel("Start of the week (Monday)")
    plt.ylabel("Merged Commits")

    # Improve layout
    plt.tight_layout()

    # Save plot if requested
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches="tight")

    # Show plot if requested
    if show_plot:
        plt.show()
