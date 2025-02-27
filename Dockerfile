# Multi-stage build
FROM ubuntu:20.04 as builder

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libboost-all-dev \
    libopencv-dev \
    libeigen3-dev \
    libgrpc++-dev \
    libsqlite3-dev \
    libpaho-mqtt-dev \
    python3.9 \
    python3.9-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Create build directory
RUN mkdir build

# Build C++ components
RUN cd build && \
    cmake .. && \
    make -j$(nproc)

# Install Python dependencies
RUN python3.9 -m pip install --upgrade pip && \
    python3.9 -m pip install -r scripts/python/requirements.txt

# Final stage
FROM ubuntu:20.04

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libboost-all-dev \
    libopencv-dev \
    libeigen3-dev \
    libgrpc++-dev \
    libsqlite3-dev \
    libpaho-mqtt-dev \
    python3.9 \
    python3.9-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy built artifacts from builder
COPY --from=builder /app/build /app/build
COPY --from=builder /app/scripts /app/scripts
COPY --from=builder /app/config /app/config

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV LD_LIBRARY_PATH=/app/build/lib

# Expose ports
EXPOSE 8080
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start application
CMD ["./build/bin/eco_vehicle"]
