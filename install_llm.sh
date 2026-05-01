#!/bin/bash

# install_llm.sh - Install llama-cpp-python with CPU or GPU support

GPU_MODE=false
VENV_PATH=".venv"

# Ensure we are in the project root and .venv exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Local virtual environment ($VENV_PATH) not found."
    echo "Please run 'uv sync' first to create the environment."
    exit 1
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --gpu) GPU_MODE=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [ "$GPU_MODE" = true ]; then
    echo "Installing llama-cpp-python with CUDA (GPU) support into $VENV_PATH..."
    # Set CMAKE_ARGS for CUDA support
    # GGML_CUDA=on is for modern llama-cpp-python (0.2.27+)
    # FORCE_CMAKE=1 ensures it doesn't use a cached CPU build
    export CMAKE_ARGS="-DGGML_CUDA=on"
    export FORCE_CMAKE=1
    
    # Target the local .venv explicitly to avoid cross-contamination
    uv pip install llama-cpp-python --no-cache-dir --force-reinstall --python "$VENV_PATH"
else
    echo "Installing llama-cpp-python for CPU only (using pre-built wheels) into $VENV_PATH..."
    # Ensure no old CMAKE_ARGS are lingering
    unset CMAKE_ARGS
    unset FORCE_CMAKE
    
    uv pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --no-cache-dir --force-reinstall --python "$VENV_PATH"
fi

echo "Installation complete."
