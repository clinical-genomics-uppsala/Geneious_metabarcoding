FROM --platform=linux/amd64 quay.io/biocontainers/emu:3.4.5--hdfd78af_0

LABEL description="Emu image with UNITE 19.02.2025 database"
LABEL version="3.4.5"
LABEL maintainer="ida.karlsson@scilifelab.uu.se"

# Set workdir
WORKDIR /

# Python packages (osfclient)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Get database
RUN mkdir -p /emu_database

COPY unite-eukaryotes-19.02.2025-dev/species_taxid.fasta /emu_database
COPY unite-eukaryotes-19.02.2025-dev/taxonomy.tsv /emu_database

ENV EMU_DATABASE_DIR="/emu_database"