# Use the NVIDIA CUDA base image with cuDNN
FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04

# Install Miniconda
RUN apt-get update && apt-get install -y wget && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh

# Set environment variables
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PATH=/opt/conda/bin:$PATH

# Copy your environment.yml file
COPY environment.yml /app/environment.yml

# Create the Conda environment (base)
RUN conda env create -f /app/environment.yml

# Set the default environment to activate (base)
RUN echo "source activate base" > ~/.bashrc
ENV PATH /opt/conda/envs/base/bin:$PATH

# Copy your application code (modify the source path as needed)
COPY . /app
WORKDIR /app

# Command to run your application (modify as needed)
CMD ["python", "main.py"]
