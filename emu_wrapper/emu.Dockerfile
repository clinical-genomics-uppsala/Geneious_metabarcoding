FROM --platform=linux/amd64 quay.io/biocontainers/emu:3.4.5--hdfd78af_0

LABEL description = "Emu image with standard database"
LABEL version="3.4.5"
MAINTAINER "Ida Karlsson" ida.karlsson@scilifelab.uu.se

# Set workdir
WORKDIR /

# Python packages (osfclient & excel report dependencies)
COPY requirements.txt .
COPY emu_report.py .

RUN pip install --no-cache-dir -r requirements.txt

# Get database
RUN mkdir -p /emu_database && export EMU_DATABASE_DIR=/emu_database && cd ${EMU_DATABASE_DIR} \
    && osf -p 56uf7 fetch osfstorage/emu-prebuilt/emu.tar && tar -xvf emu.tar

ENV EMU_DATABASE_DIR="/emu_database"