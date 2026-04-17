"""Built-in skills."""

from .omc import build_skill as build_omc_skill
from .omx import build_skill as build_omx_skill

__all__ = ["build_omc_skill", "build_omx_skill"]
