## For Version 1.2.0

#### Structural change considerations:
- [ ] Mandate that even if functions are supered from parent classes, that the source code explicitely names the function and the super call, would be redundant and add to length of code, but would reduce the headache of spaghetti-like code as the user atleast knows which functions are meant to be present in the current class.
- [ ] Can we do away with the custom_import() function and simply include direct import statements? This would reduce clutter and make code easier to read, current system obscures where import statements point. If the argument is that custom_import() includes custom error messages, incorrect import statements would also raise informative ImportErrors that will point the User to the correct location. 
- [ ] Why is the core functionality of Optimize split into optimize and plugins.optimize, can these two be reconciled? It makes the code harder to follow when you have to jump between these two directories to understand a single module.  
- [ ] Why is line_search a plugin when it is called directly in the initilaization of optimize.Base, it seems it is no longer a plugin but core functionality of the package and should be relabelled so. Perhaps the line_search directory can be dropped into the optimize directory  
- [ ] Following up on the above two points, it feels like the entire 'plugins' directory is just a 'miscellaneous' directory. Most of the functionality located I feel could be relocated to more fitting locations that would make more sense than a catch-all plugin directory  
- [ ] Can we have a single run_checks() function within the sfsubmit function that checks all parameter requirements from individual modules. At the moment the master job needs to be submitted and running, and even multiple jobs might need to be submitted before a parameter check happens for a given module, which if set incorrectly can crash a run. 
- [ ] The disk storage requirements for a large scale run can be excessive with the need for N_events database directories. Thats almost 1Tb of disk storage for 250 events using a 10s mesh. I think its vital that we start using Specfem's simultaneous run ability to drastically reduce the temporary storage costs as well as prepare Seisflows for scalability.
- [ ] ~~Rename the Base classes to be more specific, e.g. SolverBase, can be confusing if all Base classes are named the same thing.~~  
This would be nice, but it also obscures the module calls in the parameter file, requiring, e.g. SOLVER: SolverBase, which is not as clean as SOLVER: Base. This is still confusing though if you are editing multiple base classes together. 
- [ ] Allow command line runs of each "workflow" function to remove the requirement of a master job. Or even a whole command line exploration capability of the source code, such as progress of inversion etc. 

#### Bugs
- [ ] ~~setattr after parameters have been set doesnt work~~  
This is a feature I suppose, not a bug
- [ ] unix.rename will rename the entire file path, which can get dicey if e.g. 'smooth' is in the path and postprocess tries to rename the kernels from _smooth to ''

#### General
- [X] A giant list of acceptable parameters rather than having to search the source code  
Parameters are now set with a hard definition by SeisFlowsPathsParameters clsas
- [ ] replace subprocess.check_ouput(X) with subprocess.run(X, capture_output=True, text=True).stdout
- [ ] consider using a logger rather than print statement updates
- [ ] write unit tests
- [ ] update docs to reflect the major changes made, include changelog
- [X] try to reconcile a `base` parameters.yaml file with `custom` attributes, e.g. make a custom_parameters.yaml file to store all the non-standard parameters  
Now with SeisFlowsPathsParameters, only parameters that are mandated by the chosen modules will make it into the parameters file. With their types and docstrings  
- [ ] create a simple pet 2D example (specfem2D acoustic checkerboard from Ryan)
      that can be run serial and can be used for testing of the base classes
- [ ] Bring in all classes from Seisflows and update to Py3 w/ docstrings
- [ ] Sanity checks before submitting workflow, not inside the workflow
- [ ] incorporate Specfems mass event simulator to avoid N instances of database files, this would really help cut down on the total scratch file size
- [ ] Split up output.slurm by iteration
- [ ] line_search.Writer should not have its own iter, it should take iteration number from optimize

#### Preprocess
- [ ] Finish updating to Py3 and writing full docstrings, better integration with ObsPy for Base class
- [X] Include the machinery of Pyatoa as a Preprocess class rather than completely separate as Pyaflowa  
Pyatoa now defines all its own machinery which is simply called in the preprocess class. Like a plugin


#### Plugins
- [ ] Clean up the random plugins and maybe organize them better

#### Postprocess
- [ ] Finish writing combine_vol_data_vtk wrapper to generate vtk models

#### Solver
- [ ] Re-introduce Specfem2D and Specfem3D Globe solver classes

#### Workflow
- [ ] Incorporate mesh generation into `setup` for one-time mesh generation using Meshfem3D?
- [X] Add resume_from capability into Inversion base class
- [ ] ~~Finish updating migration and migration pyatoa, clean up forward~~
- [ ] Thrifty Inversion, allow workflow to start from simulation after a resume call, using a user-defined parameter,
      if the User hasn't changed anything in the parameter files. At the moment hitting the end of one set of tasks, 
      e.g. iterations 2-5 and resuming from 6, forces forward simulations to be run again, even if nothing has changed
      after iteration 5, which is a bit wasteful if you could jump straight into an adjoint simulation
- [ ] STOP_AT parameter for inversion, removes the need for a 'forward' workflow?
- [ ] ~~add workflow for minimum_resolvable_period which takes bin and DATA directories for NGLL5 and NGLL7 specfem and computes synthetics and compares them using pyatoa?~~

#### Scripts
- [X] add more descriptive help statements, maybe a step by step way to set up a
      run folder that asks the User to choose the parameters they want and fills
      in the parameter.yaml file and maybe also points them to the directories
      that require custom classes  
This is incorporated in the seisflows entry point script
- [x] include print statement for submit detailing important parameters such
      as ntasks, walltime, begin, end
- [X] include print statement for resume detailing parameters such as ntasks,
      walltime, begin, end, resume_from, allow for full print statement of all variables in a digestable way
- [ ] create a status function to check on the status of jobs, maybe by 
      querying the output files. Try not to make it system dependent so that it
      can still be generally applicable to Seisflows
- [ ] Move convert_model() function into the util section of Seisflows
- [ ] Sanity check that PAR.NTASKS <= number of sources in DATA, also list which events are being used or give the option to choose
- [X] Copy parameters.yaml into output/ on submit or resume so that if parameters change during an inversion, the user knows what the
      input parameters were? Or can you save this to a dictionary somewhere?

