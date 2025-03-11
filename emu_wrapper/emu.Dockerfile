FROM --platform=linux/amd64 quay.io/biocontainers/emu:3.4.5--hdfd78af_0

LABEL description="Emu image with standard 16S database"
LABEL version="3.4.5"
LABEL maintainer="ida.karlsson@scilifelab.uu.se"

# Set workdir
WORKDIR /

# Python packages (osfclient & excel report dependencies)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Get 16S database
RUN mkdir -p /emu_database/16S && export EMU_DATABASE_16S=/emu_database/16S && cd ${EMU_DATABASE_16S} \
    && osf -p 56uf7 fetch osfstorage/emu-prebuilt/emu.tar && tar -xvf emu.tar

# Excel report
COPY emu_report.py .