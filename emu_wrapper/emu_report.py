#!/usr/bin/env python3

import sys
import os
import numpy as np
import pandas as pd
import pandas.io.formats.excel

# import xlsxwriter

pandas.io.formats.excel.ExcelFormatter.header_style = None


##### INPUT FILES #####
if len(sys.argv) >= 5:
    COUNT_FILE = sys.argv[1]
    RA_FILE = sys.argv[2]
    OUTPUT_EXCEL = sys.argv[3]
    CSV_FILE = sys.argv[4]
    VERSION_FILE = sys.argv[5]
else:
    COUNT_FILE = "emu-combined-species-counts.tsv"
    RA_FILE = "emu-combined-species.tsv"
    OUTPUT_EXCEL = "emu.xlsx"
    CSV_FILE = "fasta.csv"
    VERSION_FILE = "versions.csv"

EMUFOLDER = os.getcwd()

##### READING #####


# Sort data frame by sample columns and most abundant taxa.
# Sample names should start with barcode no: 01, 02, 03..... or with barcode49, barcode27 etc.
def sort_samples(df, sortabund):
    header = df.columns.values.tolist()
    taxonomy = [
        name for name in header if not name[0].isdigit() if "barcode" not in name
    ]

    # sort sample columns by name, not taxonomy
    samples = np.sort(df.columns.difference(taxonomy)).tolist()
    # remove columns with threshold - duplicates
    samples = [sample for sample in samples if "threshold" not in sample]

    df = df.loc[:, taxonomy + samples].set_index(taxonomy)  # taxonomy as index columns

    if sortabund == "yes":
        # Remove and save unassigned row
        unassigned = df.iloc[-1, :]
        df = df.iloc[:-1, :]
        # Add temporary row sum column for sorting
        df = (
            df.assign(sum=df.sum(axis=1))
            .sort_values(by="sum", ascending=False)
            .drop(["sum"], axis=1)
        )

        # For qc sheet - number of assigned/unassigned reads per samples
        qc = df.sum(axis=0, numeric_only=True)
        qc = pd.DataFrame(qc, columns=["#assigned"])
        qc["#unassigned"] = unassigned

        df = pd.concat([df,
            unassigned.to_frame().T]
        )

        return (df, qc)

    else:
        return df


# LONG FORMAT
# Dict of sample and relative abundance file
sample_dict = {}
for file in os.listdir(EMUFOLDER):
    if file.endswith(("_rel-abundance.tsv")):
        sample_dict[file.split("_rel-abundance.tsv")[0].rsplit(".", 1)[0].strip()] = (
            os.path.join(EMUFOLDER, file)
        )
sample_dict = dict(sorted(sample_dict.items()))  # sort by sample name

# Append csv data to a list
long_list = []
for sample, file in sample_dict.items():
    #print(sample, file)
    emu_tab = pd.read_csv(file, sep="\t", header=0)
    emu_tab = emu_tab.sort_values(by=["estimated counts"], ascending=False)

    total = emu_tab["estimated counts"].sum()
    emu_tab.loc[-1] = pd.Series(
        total, index=["estimated counts"]
    )  # add total reads per sample row
    emu_tab.at[-1, "species"] = "total"
    emu_tab["abundance total"] = (
        emu_tab["estimated counts"].div(total).values
    )  # calculate relative abundance including unassigned reads

    emu_tab["% total"] = emu_tab["abundance total"] * 100

    emu_tab["Sample"] = sample  # .rsplit(".", 1)[0].strip() remove .fasta/.fastq
    long_list.append(emu_tab)


# Convert to dataframe
long_df = pd.concat(long_list, axis=0, ignore_index=True)
long_df = long_df.set_index("Sample")
long_df = long_df.drop(
    [
        "genus",
        "family",
        "order",
        "class",
        "phylum",
        "clade",
        "superkingdom",
        "subspecies",
        "species subgroup",
        "species group",
    ],
    axis=1,
)
long_df = long_df[
    ["species", "tax_id", "abundance", "estimated counts", "abundance total", "% total"]
]
matches = long_df["tax_id"] == "unassigned"
long_df.loc[matches, "species"] = long_df.loc[matches, "tax_id"]
long_df = long_df.drop(["tax_id"], axis=1)


# COUNTS EMU - tsv
count_data = pd.read_csv(COUNT_FILE, sep="\t", header=0)
count_data, qc = sort_samples(count_data, "yes")
count_data.columns = (
    count_data.columns.str.rsplit(".", n=1).str[0].str.strip()
)  # remove .fasta/.fastq

# RELATIVE ABUNDANCE EMU - tsv
ra_data = pd.read_csv(RA_FILE, sep="\t", header=0)
ra_data = sort_samples(ra_data, "no")
ra_data.columns = ra_data.columns.str.rsplit(".", n=1).str[0].str.strip()
ra_data = ra_data.reindex(count_data.index)  # same sorting as count sheet (abundance)

# QC SHEET
# CSV file with information from fasta files
qc_csv = pd.read_csv(CSV_FILE, sep=",", index_col=0, names=["#filtered"])
# Assigned/unassigned from count sheet
qc_csv = pd.concat([qc_csv, qc], axis=1).sort_index()
qc_csv["prop_assigned"] = qc_csv["#assigned"] / qc_csv["#filtered"]
qc_csv.index = qc_csv.index.str.rsplit(".", n=1).str[0].str.strip()

# SOFTWARE SHEET
versions_csv = pd.read_csv(VERSION_FILE, sep=",", header=None)
versions_csv.loc[-1] = ["report_date", pd.Timestamp.today()]  # add date as first row
versions_csv.index = versions_csv.index + 1 
versions_csv.sort_index(inplace=True)



##### WRITING TO EXCEL FILE #####
def get_rows(df,content):
    rows = df[
        df.applymap(
                    lambda x: True if isinstance(x, str) and content in x else False
                ).any(axis=1)
        ].index.tolist()
    return rows

def format_rows(worksheet, row, report_format):
    worksheet.set_row(  #row, height, cell_format, options
        row + 1, None, report_format
    )

# From config
report_params = dict(versions_csv.to_numpy())
#print(report_params)

with pd.ExcelWriter(OUTPUT_EXCEL, engine='xlsxwriter') as writer:

    versions_csv.to_excel(writer, sheet_name="software", index=False, header=False)
    qc_csv.to_excel(writer, sheet_name="qc", index=True, float_format="%.2f")
    long_df.to_excel(writer, sheet_name="emu_long", index=True, float_format="%.2f")
    count_data.to_excel(writer, sheet_name="emu_counts", index=True, float_format="%.2f")
    ra_data.to_excel(writer, sheet_name="emu_proportions", index=True, float_format="%.2f")

    workbook = writer.book

    ##### FORMATTING ####
    # Left-adjust cells
    align_cells = workbook.add_format()
    align_cells.set_align("left")

    # Formats
    bold_format = workbook.add_format({"bold": "True"})  # header and index
    border_format = workbook.add_format({"bottom": 1, "bold": "True"})
    spike_format = workbook.add_format({"color": "orange"})
    pass_cutoff_format = workbook.add_format({"color": "blue"})
    fail_cutoff_format = workbook.add_format({"color": "red"})
    fail_reads_format = workbook.add_format({"color": "red","bottom": 1})

    for worksheet in workbook.worksheets():
        worksheet.set_column("A:A", 25, bold_format)  # width of cell
        worksheet.set_row(0, 15, bold_format)  # default row height
        worksheet.freeze_panes(1, 1)

        for taxon in report_params['spike_taxa'].split(','):
            worksheet.conditional_format(1, 1, len(long_df), len(count_data.columns), # (first_row, first_col, last_row, last_col)
                {'type':     'text',
                'criteria': 'containing',
                'value':    taxon.strip().strip('"'),
                'format':   spike_format})

        if worksheet.get_name() == "software":
            worksheet.set_column("B:B", 30)

        if worksheet.get_name() == "emu_long":
            worksheet.set_column("B:B", 25)

            # Conditional formatting
            long_df.reset_index(inplace=True)
            for sample, path in sample_dict.items():
                continue_sample = False
                sample_rows = get_rows(long_df,sample)
                #print(f"Processing sample: {sample} with {sample_rows} rows")

                total_row = None
                unassigned_row = None

                for row in sample_rows:
                    if long_df["species"][row] == "total":
                        total_row = row
                        #print(f"Total row: {total_row}")
                        if int(long_df["estimated counts"][total_row]) < int(report_params['min_reads']):
                            #print(f"Estimated counts {long_df['estimated counts'][total_row]} is less than {report_params['min_reads']}")
                            format_rows(worksheet, total_row, fail_reads_format)
                            continue_sample = True
                        else:
                            format_rows(worksheet, total_row, border_format) # mark last row
                    elif long_df["species"][row] == "unassigned":
                        unassigned_row = row
                        #print(f"Unassigned row: {unassigned_row}")
                    
                for row in sample_rows:
                    if not continue_sample and row == unassigned_row:

                        if float(long_df["abundance total"][unassigned_row]) >= float(report_params['max_unassigned_prop']):
                            #print(f"Abundance total {long_df['abundance total'][unassigned_row]} is greater than {report_params['max_unassigned_prop']}")
                            format_rows(worksheet, unassigned_row, fail_cutoff_format)
                            continue_sample = True

                for row in sample_rows:
                    if not continue_sample and (row != unassigned_row and row != total_row): 
                        if (float(long_df["abundance total"][row]) >= float(report_params['min_abund_tot'])) and (float(long_df["estimated counts"][row])) >= int(report_params['min_counts_taxa']):
                            #print(f"Abundance total {long_df['abundance total'][row]} is greater than {report_params['min_abund_tot']}")
                            format_rows(worksheet, row, pass_cutoff_format)
                
                if continue_sample:
                    #print(f"Continuing to next sample due to conditions met in sample: {sample}")
                    continue


