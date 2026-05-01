"""Test settings — uses local PostgreSQL via .env.test."""

import environ
import pathlib
environ.Env.read_env(pathlib.Path(__file__).resolve().parents[2] / ".env.test")

from .base import *  # noqa: F401, F403
