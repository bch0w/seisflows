"""
Pre-defined Warning and Error messages so that Seisflows has a uniform look
"""


WarningOverwrite = """

WARNING: Data from previous workflow found in working directory.

To delete data and start a new workflow type:
  seisflows restart

To resume existing workflow type:
  sesiflows resume
"""

FileError = """

FILE NOT FOUND

    {file}

"""

SolverError = """

SOLVER FAILED

    Nonzero exit status returned by:  {exc}

    Subsequent tasks may fail because expected solver output is not in place.
    Users running on clusters without fault tolerance should consider stopping 
    any remaining workflow tasks to avoid further loss of resources. 

    To troubleshoot solver errors, navigate to ./scratch/solver to browse solver
    output or try running solver manually in the directories set up in
    ./scratch/solver. 

"""

SystemWarning = """

Please double check SYSTEM parameter

    Expected hostname: {}
    Actual hostname: {}

"""

ReceiverError_SPECFEM = """

ERROR READING RECEIVERS

    Error reading receivers.

"""

SourceError_SPECFEM = """

ERROR READING SOURCES

    In DIRECTORY, there must be one or more files matching WILDCARD.

    DIRECTORY:  "{}"
    WILDCARD:  "{}"

"""

ParameterWarning_SPECFEM = """

PARAMETER WARNING

    There is a conflict between parameters.

    SPECFEM Parameter:  "{}"
    Old Value:  {}
    Overwriting with:  {}

"""

DataFormatWarning = """

DATA FORMAT WARNING

    reader format: {}
    writer format: {}

    Incompatible file formats may result in job failure or other problems.

"""

ReaderError = """

READER ERROR

   Seismic data reader not found.

   PAR.READER must correspond to an entry in seisflows.plugins.readers

"""

WriterError = """

WRITER ERROR

   Seismic data writer not found.

   PAR.WRITER must correspond to an entry in seisflows.plugins.writers

"""

TaskTimeout = """

TASK TIMED OUT

    Stopping workflow because task time limit exceeded. (To adjust limit,
    add or modify TASKTIME in parameter file.)

        Task name:  {classname}.{method}
        Task id:    {job_id}
        Time limit (minutes): {tasktime}

"""

TaskError_LSF = """

TASK ERROR

    Task failed:  {}.{}

    For more information, see output.lsf/{}

    Stopping workflow...

"""


TaskError_PBS = """

TASK ERROR

    Task failed:  {}.{}

    For more information, see output.pbs/{}

    Stopping workflow...

"""

TaskError_SLURM = """

TASK ERROR

    Task failed:  {classname}.{method}

    For more information, see output.logs/{job_id}

    Stopping workflow...

"""

obspyImportError = """

DEPENDENCY ERROR

    The current data processing workflow requires OBSPY.  Please install it and
    try again.

"""

mpiError1 = """

SYSTEM CONFIGURATION ERROR

    The following system configuration can be used only with single-core
    solvers:

        system.{}

    If your solver requires only a single core, then set NPROC equal to 1.

    If your solver requires multiple cores, then consider using lsf_lg, pbs_lg,
    or slurm_lg system configurations instead.

"""

mpiError2 = """

DEPENDENCY ERROR

    The following system configuration requires MPI4PY:

        system.{}

    Please install MPI4PY and try again, or consider choosing a different system
    configuration.

"""

mpiError3 = """

SYSTEM CONFIGURATION WARNING

    The following system configuration requires 'mpiexec':

        system.{}

    Please make sure than 'mpiexec' is accessible through your shell's PATH
    environment variable. If your executable goes by a different name such as
    'mpirun', consider creating an alias in your shell's configuration file, and
    remember to source the modified configuration file. If MPI is not available
    on your system, consider using the 'multithreaded' system interface instead.

"""

MissingParameter_Workflow = """

Please specify a workflow by adding a line to the parameter file, e.g.

    WORKFLOW='inversion';

for a list of available workflows, see seisflows/workflow in the source code

"""

MissingParameter_System = """

Please specify a system interface by adding a line to the parameter file, e.g.

    SYSTEM='serial';

for a list of available interfaces, see seisflows/system in the source code

"""

ImportError1 = """

SEISFLOWS IMPORT ERROR

    Please check that "custom_import" utility is being used as follows:

        custom_import(name1, name2)

    The resulting full dotted name "seisflows.name1.name2" must correspond to a
    module in the SeisFlows package.

"""

ImportError2 = """

SEISFLOWS IMPORT ERROR

    custom_import(system, classname, method)

    Please check that "name1" is one of the following

        workflow
        solver
        optimize
        preprocess
        postprocess
        system

"""

ImportError3 = """

SEISFLOWS IMPORT ERROR

    The following module was not found in the SeisFlows package:

        seisflows.{name}.{module}

    Please check user-supplied {module_upper} parameter.

"""

ImportError4 = """

SEISFLOWS IMPORT ERROR

    By convention, SeisFlows module 

        seisflows.{name}.{module}

    must contain a class named

        {classname}

"""

CompatibilityError1 = """

Parameter settings have changed.

In your parameter file, please remove
    OPTIMIZE='base'

and add one of the following instead
    OPTIMIZE='LBFGS'
    OPTIMIZE'=NLCG'
    OPTIMIZE='SteepestDescent'

"""

Warning_pbs_sm = """

WARNING:  PBS_SM hasn't been tested for a long while because we don't own a PBS
cluster.  If you have access to one cluster and are willing to help debug, 
please let us know.

"""

Warning_pbs_lg = """

WARNING:  PBS_LG hasn't been tested for a long while because we don't own a PBS
cluster.  If you have access to one cluster and are willing to help debug, 
please let us know.

"""

PoissonsRatioError = """
                
ERROR CHECKING MODEL PARAMETERS

    The Poisson's ratio of '{tag}' is out of bounds with respect 
    to the range defined by Specfem3D (-1, 0.5). This will cause 
    an error in the process xgenerate_databases. The model 
    bounds were found to be:

    {pmin:.2f} < PR < {pmax:.2f}

"""
