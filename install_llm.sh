#!/bin/bash

# install_llm.sh - Install llama-cpp-python with CPU or GPU support

GPU_MODE=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --gpu) GPU_MODE=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [ "$GPU_MODE" = true ]; then
    echo "Installing llama-cpp-python with CUDA (GPU) support..."
    # Set CMAKE_ARGS for CUDA support
    # GGML_CUDA=on is for modern llama-cpp-python (0.2.27+)
    # FORCE_CMAKE=1 ensures it doesn't use a cached CPU build
    export CMAKE_ARGS="-DGGML_CUDA=on"
    export FORCE_CMAKE=1
    
    # Use uv pip install for direct control over compilation
    uv pip install llama-cpp-python --no-cache-dir --force-reinstall
else
    echo "Installing llama-cpp-python for CPU only (using pre-built wheels)..."
    # Ensure no old CMAKE_ARGS are lingering
    unset CMAKE_ARGS
    unset FORCE_CMAKE
    
    uv pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --no-cache-dir --force-reinstall
fi

echo "Installation complete."
