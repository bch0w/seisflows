#!/usr/bin/env python
"""
This is the custom class for an steepest descent optimization schema.
It supercedes the `seisflows.optimize.base` class
"""
import sys

from seisflows.config import custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class SteepestDescent(custom_import("optimize", "base")):
    """
    Steepest descent method
    """
    def __init__(self):
        self.restarted = False

    def check(self):
        """
        Checks parameters, paths, and dependencies
        """
        if "LINESEARCH" not in PAR:
            setattr(PAR, "LINESEARCH", "Bracket")

        super().check()

    def setup(self):
        """
        Set up the steepest descent optimization schema
        """
        super().setup()

    def compute_direction(self):
        """
        Overwrite the Base compute direction class
        """
        super().compute_direction()

    def restart(self):
        """
        Steepest descent never requires restarts
        """
        pass

