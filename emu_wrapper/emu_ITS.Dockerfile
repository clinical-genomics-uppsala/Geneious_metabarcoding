FROM --platform=linux/amd64 quay.io/biocontainers/emu:3.4.5--hdfd78af_0

LABEL description = "Emu image 3.4.5 with ITS database (UNITE eukaryotes)"
MAINTAINER "Ida Karlsson" ida.karlsson@scilifelab.uu.se

# Set workdir
WORKDIR /

# Python packages (osfclient)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Get database
RUN mkdir -p /emu_database && export EMU_DATABASE_DIR=/emu_database && cd ${EMU_DATABASE_DIR} \
    && export EMU_PREBUILT_DB='unite-all' \
    && osf -p 56uf7 fetch osfstorage/emu-prebuilt/${EMU_PREBUILT_DB}.tar && tar -xvf ${EMU_PREBUILT_DB}.tar

ENV EMU_DATABASE_DIR="/emu_database"