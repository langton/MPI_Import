# A trivial module. One piece of data, plus a check
# that we're using MPI_Import

import __builtin__
if not hasattr(__builtin__.__import__,"mpi_import"):
    raise SystemExit("trivialmod imported without MPI_Import")

data = 42
