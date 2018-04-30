# Path to CUDA installation version 7.5.18 that works well
# Replace with your own installation of CUDA if needed
export CUDA_HOME=/usr/local/cuda-7.5.18

# CUDA general paths
export PATH=${CUDA_HOME}/bin:$PATH
export LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${CUDA_HOME}/extras/CUPTI/lib64:${LD_LIBRARY_PATH}
export MANPATH=${CUDA_HOME}/doc/man:${MANPATH}

# Path to the project
# Replace with wherever you cloned the project repo
export PYTHONPATH=${PYTHONPATH}:""
