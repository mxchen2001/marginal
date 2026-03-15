"""Entrypoint — runs the marginal agentic loop."""

from __future__ import annotations

import asyncio
import logging
import sys

from marginal.funnel.scheduler import run_loop, run_once


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    if "--loop" in sys.argv:
        run_loop()
    else:
        asyncio.run(run_once())


if __name__ == "__main__":
    main()
