
FROM python:3.13-slim

# Install C++ compilation tools and CMake.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install requirements in the container's Python environment.
RUN python -m pip install --no-cache-dir --upgrade pip 
COPY requirements.txt /workspace/
RUN python -m pip install --no-cache-dir -r requirements.txt

# Start in a shell for interactive development.
CMD ["bash"]
