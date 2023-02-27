FROM --platform=linux/amd64 continuumio/miniconda3:22.11.1

LABEL description = "emu image from gitlab to include: Combine-outputs empty col error fix"

# Set workdir
WORKDIR /

# Create emu environment and database
RUN git clone https://gitlab.com/treangenlab/emu.git && cd emu && git checkout 07e2eacfe457e6618ae22fd5d9b2e31d350c2b68 && \
    conda env create -f environment.yml

ENV PATH="${PATH}:/emu"
ENV EMU_DATABASE_DIR="/emu/emu_database"

# Start with emu activated
SHELL ["conda", "run", "-n", "emu", "/bin/bash", "-c"]

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "custom-emu"]