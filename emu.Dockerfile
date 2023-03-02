FROM --platform=linux/amd64 quay.io/biocontainers/emu:3.4.4--hdfd78af_1

LABEL description = "Emu image with standard database"
MAINTAINER "Ida Karlsson" ida.karlsson@scilifelab.uu.se

# Set workdir
WORKDIR /

# Get database
RUN mkdir -p /emu_database && export EMU_DATABASE_DIR=/emu_database \
    && wget -qO- https://gitlab.com/treangenlab/emu/-/archive/v3.0.0/emu-v3.0.0.tar.gz | tar -C $EMU_DATABASE_DIR -xvz --strip-components=2 emu-v3.0.0/emu_database/

ENV EMU_DATABASE_DIR="/emu_database"