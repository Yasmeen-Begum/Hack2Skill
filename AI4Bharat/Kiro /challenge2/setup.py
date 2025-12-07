"""Setup configuration for Lazy Automation Tool."""

from setuptools import setup, find_packages

setup(
    name="lazy-automation-tool",
    version="0.1.0",
    description="A command-line utility to automate repetitive file system tasks",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "gradio>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "hypothesis>=6.82.0",
            "pytest-cov>=4.1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "lazy-auto=lazy_automation.cli.main:main",
            "lazy-auto-web=lazy_automation.web_interface:main",
        ]
    },
)
