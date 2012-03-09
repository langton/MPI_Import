# Just a basic sanity check on MPI_Import. We'll import numpy and a
# trivial user-defined module.
from MPI_Import import mpi_import
with mpi_import():
    import numpy
    import trivialmod

if trivialmod.data != 42:
    raise SystemExit("trivialmod was not imported correctly!")
