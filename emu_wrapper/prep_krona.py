#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import pandas as pd

##### INPUT FILES #####
REL_ABUND_FILE = sys.argv[1]
OUTPUT_FILE = Path(REL_ABUND_FILE).with_name(Path(REL_ABUND_FILE).stem + "_krona.tsv")

# Restructure rel_abundance.tsv file to work with ktImportText
rel_abund_table = pd.read_csv(REL_ABUND_FILE, sep="\t", header=0, index_col=0)

rel_abund_table.at['unmapped', 'species'] = 'unmapped'
rel_abund_table.at['mapped_unclassified', 'species'] = 'mapped_unclassified'

rel_abund_table.reset_index(inplace=True)
rel_abund_table = rel_abund_table.drop(['tax_id','abundance'], axis=1)
try:
    rel_abund_table = rel_abund_table.drop(['SH'], axis=1) # KeyError
except KeyError:
    pass

estimated_counts = rel_abund_table.pop('estimated counts') 
rel_abund_table.insert(0, 'estimated counts', estimated_counts)

rel_abund_table.to_csv(OUTPUT_FILE, sep="\t", index=False)
