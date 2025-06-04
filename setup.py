from setuptools import setup, find_packages

setup(
    name="ghweekly",
    version="0.1.4",
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
    url="https://github.com/bhimrazy/gh-weekly-commits",
    project_urls={
        "Bug Tracker": "https://github.com/bhimrazy/gh-weekly-commits/issues",
        "Documentation": "https://github.com/bhimrazy/gh-weekly-commits#readme",
        "Source Code": "https://github.com/bhimrazy/gh-weekly-commits",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
)
