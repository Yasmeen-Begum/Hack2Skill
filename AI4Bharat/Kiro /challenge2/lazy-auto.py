#!/usr/bin/env python3
"""
Executable script for Lazy Automation Tool.

This script provides a direct entry point for running the tool
without installation. For installed usage, use the 'lazy-auto' command.
"""

import sys
from lazy_automation.cli.main import main

if __name__ == '__main__':
    main()
