#!/usr/bin/env python
"""
This is the subclass seisflows.solver.specfem2d

This class provides utilities for the Seisflows solver interactions with
Specfem2D. It inherits all attributes from seisflows.solver.Base,
"""
import os
import sys
from glob import glob

from seisflows.plugins.solver.specfem2d import smooth_legacy
from seisflows.tools.seismic import getpar, setpar
from seisflows.tools import unix
from seisflows.tools.tools import exists
from seisflows.config import custom_import
from seisflows.tools.seismic import call_solver
from seisflows.tools.err import ParameterError


PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

system = sys.modules['seisflows_system']
preprocess = sys.modules['seisflows_preprocess']


class Specfem2D(custom_import("solver", "base")):
    """
    Python interface to Specfem2D. This subclass inherits functions from
    seisflows.solver.Base

    !!! See base class for method descriptions !!!
    """
    def check(self):
        """
        Checks parameters and paths
        """
        super().check()

        # Set an internal parameter list
        if PAR.MATERIALS.upper() == "ELASTIC":
            self.parameters += ["vp", "vs"]
        elif PAR.MATERIALS.upper() == "ACOUSTIC":
            self.parameters += ["vp"]

        required_parameters = ["NT", "DT", "F0", "FORMAT"]
        for req in required_parameters:
            if req not in PAR:
                raise ParameterError(self, req)

        acceptable_formats = ["SU"]
        if PAR.FORMAT.upper() not in acceptable_formats:
            raise Exception(f"'FORMAT' must be {acceptable_formats}")

    def check_solver_parameter_files(self):
        """
        Checks solver parameters
        """
        def getpar_tryexcept(trial_list, cast, tag=""):
            """
            Re-used function to wrap getpar() in a try-except
            To allow for different SPECFEM2D Par_file version
            :type trial_list: list
            :param trial_list: list of strings to check in par file
            :type cast: str
            :param cast: cast the output results as this type
            :type tag: str
            :param tag: tag used incase error raised, for more useful message
            :rtype tuple: (str, cast)
            :return: the correct check from the trial list and corresponding val
            """
            for check in trial_list:
                try:
                    return check, getpar(check, cast=cast)
                except KeyError as e:
                    pass
            else:
                raise KeyError(f"Parameter '{tag}' not found when looking for "
                               f"{trial_list}") from e

        # Check the number of steps in the SPECFEM2D Par_file
        nt_str, nt = getpar_tryexcept(trial_list=["NSTEP", "nt"],
                                      cast=int, tag="nt")
        if nt != PAR.NT:
            if self.taskid == 0:
                print(f"WARNING: nt={nt} not equal PAR.NT={PAR.NT},"
                      f"setting PAR FILE nt={PAR.NT}")
            setpar(nt_str, PAR.NT)

        # Check the dt step discretization in the SPECFEM2D Par_file
        dt_str, dt = getpar_tryexcept(trial_list=["DT", "deltat"],
                                      cast=float, tag="dt")
        if dt != PAR.DT:
            if self.taskid == 0:
                print(f"WARNING: dt={dt} not equal PAR.DT={PAR.DT},"
                      f"setting PAR FILE dt={PAR.DT}")
            setpar(dt_str, PAR.DT)

        # Check the central frequency in the SPECFEM2D SOURCE file
        f0 = getpar("f0", file="DATA/SOURCE", cast=float)
        if f0 != PAR.F0:
            if self.taskid == 0:
                print(f"WARNING: f0={f0} not equal PAR.F0={PAR.F0},"
                      f"setting SOURCE f0={PAR.F0}")
            setpar("f0", PAR.F0, filename="DATA/SOURCE")

        # Ensure that NPROC matches the MESH values
        if self.mesh_properties.nproc != PAR.NPROC:
            if self.taskid == 0:
                print(f"Warning: "
                      f"mesh_properties.nproc={self.mesh_properties.nproc} "
                      f"not equal  PAR.NPROC={PAR.NPROC}"
                      )

        if "MULTIPLES" in PAR:
            if PAR.MULTIPLES:
                setpar("absorbtop", ".false.")
            else:
                setpar("absorbtop", ".true.")

    def generate_data(self, **model_kwargs):
        """
        Generates data using the True model, exports traces to `traces/obs`

        :param model_kwargs: keyword arguments to pass to `generate_mesh`
        """
        self.generate_mesh(**model_kwargs)

        unix.cd(self.cwd)
        setpar("SIMULATION_TYPE", "1")
        setpar("SAVE_FORWARD", ".true.")

        call_solver(system.mpiexec(), "bin/xmeshfem2D", output="mesher.log")
        call_solver(system.mpiexec(), "bin/xspecfem2D", output="solver.log")

        if PAR.FORMAT in ['SU', 'su']:
            src = glob('OUTPUT_FILES/*.su')
            # work around SPECFEM2D's different file names (depending on the
            # version used :
            unix.rename('single_p.su', 'single.su', src)
            src = glob('OUTPUT_FILES/*.su')
            dst = 'traces/obs'
            unix.mv(src, dst)

        if PAR.SAVETRACES:
            self.export_traces(PATH.OUTPUT+'/'+'traces/obs')

    def initialize_adjoint_traces(self):
        """
        Setup utility: Creates the "adjoint traces" expected by SPECFEM.
        This is only done for the 'base' the Preprocess class.

        Note:
            Adjoint traces are initialized by writing zeros for all channels.
            Channels actually in use during an inversion or migration will be
            overwritten with nonzero values later on.
        """
        super().initialize_adjoint_traces()

        # work around SPECFEM2D's use of different name conventions for
        # regular traces and 'adjoint' traces
        if PAR.FORMAT.upper() == "SU":
            files = glob(os.path.join(self.cwd, "traces", "adj", "*SU"))
            unix.rename(old='_SU', new='_SU.adj', names=files)

        # work around SPECFEM2D's requirement that all components exist,
        # even ones not in use
        if PAR.FORMAT.upper() == "SU":
            unix.cd(os.path.join(self.cwd, "traces", "adj"))

            for channel in ['x', 'y', 'z', 'p']:
                src = f"U{PAR.CHANNELS[0]}_file_single.su.adj"
                dst = f"{channel}s_file_single.su.adj"
                if not exists(dst):
                    unix.cp(src, dst)

    def generate_mesh(self, model_path, model_name, model_type='gll'):
        """
        Performs meshing with internal mesher Meshfem2D and database generation

        :type model_path: str
        :param model_path: path to the model to be used for mesh generation
        :type model_name: str
        :param model_name: name of the model to be used as identification
        :type model_type: str
        :param model_type: available model types to be passed to the Specfem3D
            Par_file. See Specfem3D Par_file for available options.
        """
        assert(exists(model_path)), f"model {model_path} does not exist"

        available_model_types = ["gll"]
        assert(model_type in available_model_types), \
            f"{model_type} not in available types {available_model_types}"

        self.initialize_solver_directories()
        unix.cd(self.cwd)

        # Run mesh generation
        if model_type == "gll":
            self.check_mesh_properties(model_path)

            # Copy the model files (ex: proc000023_vp.bin ...) into DATA
            src = glob(os.path.join(model_path, "*"))
            dst = self.model_databases
            unix.cp(src, dst)

        # Export the model into output folder
        if self.taskid == 0:
            self.export_model(os.path.join(PATH.OUTPUT, model_name))

    def forward(self, path='traces/syn'):
        """
        Calls SPECFEM2D forward solver, exports solver outputs to traces dir

        :type path: str
        :param path: path to export traces to after completion of simulation
        """
        setpar("SIMULATION_TYPE", "1")
        setpar("SAVE_FORWARD", ".true.")

        call_solver(system.mpiexec(), "bin/xmeshfem2D")
        call_solver(system.mpiexec(), "bin/xspecfem2D")

        if PAR.FORMAT.upper() == "SU":
            filenames = glob(os.path.join("OUTPUT_FILES", "*.su"))

            # Work around SPECFEM2D's different file names (version dependent)
            unix.rename("single_p.su", "single.su", filenames)

            unix.mv(filenames, path)

    def adjoint(self):
        """
        Calls SPECFEM2D adjoint solver, creates the `SEM` folder with adjoint
        traces which is required by the adjoint solver
        """
        setpar("SIMULATION_TYPE", "3")
        setpar("SAVE_FORWARD", ".false.")

        unix.rm("SEM")
        unix.ln("traces/adj", "SEM")

        # Deal with different SPECFEM2D name conventions for regular traces and
        # "adjoint" traces
        if PAR.FORMAT.upper == "SU":
            files = glob(os.path.join("traces", "adj", "*.su"))
            unix.rename(".su", ".su.adj", files)

        call_solver(system.mpiexec(), "bin/xmeshfem2D")
        call_solver(system.mpiexec(), "bin/xspecfem2D")

    def import_model(self, path):
        """
        File transfer utility to move a SPEFEM2D model into the correct location
        for a workflow.

        :type path: str
        :param path: path to the SPECFEM2D model
        :return:
        """
        unix.cp(src=glob(os.path.join(path, "model", "*")),
                dst=os.path.join(self.cwd, "DATA")
                )

    def export_model(self, path):
        """
        File transfer utility to move a SPEFEM2D model from the DATA directory
        to an external path location

        :type path: str
        :param path: path to export the SPECFEM2D model
        :return:
        """
        unix.mkdir(path)
        unix.cp(src=glob(os.path.join(self.cwd, "DATA", "*.bin")),
                dst=path)

    @property
    def data_filenames(self):
        """
        Returns the filenames of all data, either by the requested components
        or by all available files in the directory.

        :rtype: list
        :return: list of data filenames
        """
        if PAR.CHANNELS:
            if PAR.FORMAT in ['SU', 'su']:
                filenames = []
                for channel in PAR.CHANNELS:
                    filenames += [f"U{channel}_file_single.su"]
                return filenames
        else:
            unix.cd(self.cwd)
            unix.cd('traces/obs')

            if PAR.FORMAT in ['SU', 'su']:
                return glob('U?_file_single.su')

    @property
    def model_databases(self):
        """
        The location of databases for kernel outputs
        """
        return os.path.join(self.cwd, "DATA")

    @property
    def kernel_databases(self):
        """
        The location of databases for model outputs
        """
        return os.path.join(self.cwd, "OUTPUT_FILES")

    @property
    def source_prefix(self):
        """
        Specfem2D's preferred source prefix

        :rtype: str
        :return: source prefix
        """
        return PAR.SOURCE_PREFIX.upper()

