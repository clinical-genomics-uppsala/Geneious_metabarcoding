FROM --platform=linux/amd64 r-base:4.4.2

LABEL description="R with vegan package"
LABEL version="4.4.2"
LABEL maintainer="ida.karlsson@scilifelab.uu.se"

# Set workdir
WORKDIR /usr/local/src/data

# Install pandoc
RUN wget https://github.com/jgm/pandoc/releases/download/3.5/pandoc-3.5-linux-amd64.tar.gz \
    && tar xvzf pandoc-3.5-linux-amd64.tar.gz --strip-components 1 -C /usr/local/

# Install R packages
RUN R -e "install.packages('vegan',repos = 'http://cran.us.r-project.org')" \
    && R -e "install.packages('rmarkdown',repos = 'http://cran.us.r-project.org')" 

# Markdown + ordiellipse_custom_scale function
COPY rscripts /usr/local/src/rscripts