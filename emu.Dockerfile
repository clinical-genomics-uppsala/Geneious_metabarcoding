FROM --platform=linux/amd64 continuumio/miniconda3:22.11.1

LABEL description = "emu image"

COPY environment.yaml /

# Set workdir
WORKDIR /

# Create emu environment and database
RUN conda env create -f /environment.yaml && \
    mkdir -p /emu_database && export EMU_DATABASE_DIR=/emu_database && \
    wget -qO- https://gitlab.com/treangenlab/emu/-/archive/v3.0.0/emu-v3.0.0.tar.gz | tar -C $EMU_DATABASE_DIR -xvz --strip-components=2 emu-v3.0.0/emu_database/

ENV EMU_DATABASE_DIR="/emu_database"

# Start with emu activated
SHELL ["conda", "run", "-n", "emu", "/bin/bash", "-c"]

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "emu"]