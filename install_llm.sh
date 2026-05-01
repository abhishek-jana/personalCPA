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
    export CMAKE_ARGS="-DGGML_CUDA=on"
    # Use uv pip install for direct control over compilation
    uv pip install llama-cpp-python --no-cache-dir --force-reinstall
else
    echo "Installing llama-cpp-python for CPU only (using pre-built wheels)..."
    uv pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --no-cache-dir --force-reinstall
fi

echo "Installation complete."
