from setuptools import setup, find_packages

setup(
    name="ghweekly",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "pandas",
        "matplotlib",
    ],
    entry_points={
        "console_scripts": [
            "ghweekly=ghweekly.cli:main",
        ],
    },
    author="Bhimraj Yadav",
    description="Visualize weekly GitHub commit activity across repositories.",
    license="MIT",
)
