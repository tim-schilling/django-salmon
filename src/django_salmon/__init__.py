from __future__ import annotations

import os

from .registry import registry

__all__ = ["registry"]
# Support suffixing the version with a dev segment.
# This allows for building dev distributions to test
# the release process.
# See .github/workflows/test_release.yml
__version__ = VERSION = "0.1.0" + os.environ.get("DJSALMON_VERSION_DEV", "")
