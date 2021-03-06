#!/usr/bin/env python
"""
This is the base class seisflows.system.Base
This class provides the core utilities interaction with HPC systems which must
be overloaded by subclasses
"""
import os
import sys
from glob import glob
from seisflows.config import save, saveobj
from seisflows.tools import unix
from seisflows.tools.err import ParameterError


PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class Base:
    """
    Abstract base class
    """
    def check(self):
        """
        Checks parameters and paths
        """
        # Name of job
        if "TITLE" not in PAR:
            setattr(PAR, "TITLE", os.path.basename(os.path.abspath(".")))

        # Time allocated for workflow in minutes
        if "WALLTIME" not in PAR:
            setattr(PAR, "WALLTIME", 30.)

        # Time allocated for each individual task in minutes
        if "TASKTIME" not in PAR:
            setattr(PAR, "TASKTIME", 15.)

        # Number of tasks
        if "NTASK" not in PAR:
            raise ParameterError(PAR, "NTASK")

        # Number of cores per task
        if "NPROC" not in PAR:
            raise ParameterError(PAR, "NPROC")

        # Level of detail in output messages
        if "VERBOSE" not in PAR:
            setattr(PAR, "VERBOSE", 1)

        # Location where job was submitted
        if "WORKDIR" not in PATH:
            setattr(PATH, "WORKDIR", os.path.abspath("."))

        # Location where output files are written
        if "OUTPUT" not in PATH:
            setattr(PATH, "OUTPUT", os.path.join(PATH.WORKDIR, "output"))

        # Location where temporary files are written
        if "SCRATCH" not in PATH:
            setattr(PATH, "SCRATCH", os.path.join(PATH.WORKDIR, "scratch"))

        # Where system files are written
        if "SYSTEM" not in PATH:
            setattr(PATH, "SYSTEM", os.path.join(PATH.SCRATCH, "system"))

        # Optional local scratch path
        if "LOCAL" not in PATH:
            setattr(PATH, "LOCAL", None)

    def setup(self):
        """
        Create the SeisFlows directory structure in preparation for a
        SeisFlows workflow. Ensure that if any config information is left over
        from a previous workflow, that these files are not overwritten by
        the new workflow. Should be called by submit()
        """
        # Create scratch directories
        unix.mkdir(PATH.SCRATCH)
        unix.mkdir(PATH.SYSTEM)

        # Create output directories
        unix.mkdir(PATH.OUTPUT)
        unix.mkdir(os.path.join(PATH.WORKDIR, "output.logs"))
        unix.mkdir(os.path.join(PATH.WORKDIR, "logs.old"))

        # If a scratch directory is made outside the working directory, make
        # sure its accessible from within the working directory
        if not os.path.exists("./scratch"):
            unix.ln(PATH.SCRATCH, os.path.join(PATH.WORKDIR, "scratch"))

        output_log = os.path.join(PATH.WORKDIR, "output")
        error_log = os.path.join(PATH.WORKDIR, "error")

        # If resuming, move old log files to keep them out of the way
        for log in [output_log, error_log]:
            unix.mv(src=glob(os.path.join(f"{log}*.log")),
                    dst=os.path.join(PATH.WORKDIR, "logs.old")
                    )

        # Copy the parameter.yaml file into the log directoroy
        par_copy = f"parameters_{PAR.BEGIN}-{PAR.END}.yaml"
        unix.cp(src="parameters.yaml",
                dst=os.path.join(PATH.WORKDIR, "logs.old", par_copy)
                )

        return output_log, error_log

    def submit(self):
        """
        Submits workflow
        """
        raise NotImplementedError('Must be implemented by subclass.')

    def run(self, classname, method, *args, **kwargs):
        """
        Runs task multiple times
        """
        raise NotImplementedError('Must be implemented by subclass.')

    def run_single(self, classname, method, *args, **kwargs):
        """
        Runs task a single time
        """
        raise NotImplementedError('Must be implemented by subclass.')

    def taskid(self):
        """
        Provides a unique identifier for each running task
        """
        raise NotImplementedError('Must be implemented by subclass.')

    def checkpoint(self, path, classname, method, args, kwargs):
        """
        Writes information to disk so tasks can be executed remotely

        :type path: str
        :param path: path the kwargs
        :type classname: str
        :param classname: name of the class to save
        :type method: str
        :param method: the specific function to be checkpointed
        :type kwargs: dict
        :param kwargs: dictionary to pass to object saving
        """
        argspath = os.path.join(path, "kwargs")
        argsfile = os.path.join(argspath, f"{classname}_{method}.p")
        unix.mkdir(argspath)
        saveobj(argsfile, kwargs)
        save()

