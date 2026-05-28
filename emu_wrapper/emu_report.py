#!/usr/bin/env python3

import sys
import os
import numpy as np
import pandas as pd
import pandas.io.formats.excel


pandas.io.formats.excel.ExcelFormatter.header_style = None


##### INPUT FILES #####
if len(sys.argv) >= 5:
    COUNT_FILE = sys.argv[1]
    RA_FILE = sys.argv[2]
    OUTPUT_EXCEL = sys.argv[3]
    CSV_FILE = sys.argv[4]
    VERSION_FILE = sys.argv[5]
    EMUFOLDER = os.getcwd()

# Test data - execute report script in Geneious_metabarcoding folder: python emu_wrapper/emu_report.py
else:
    COUNT_FILE = "data/test_report/emu-combined-species-counts.tsv"
    RA_FILE = "data/test_report/emu-combined-species.tsv"
    OUTPUT_EXCEL = "data/test_report/emu.xlsx"
    CSV_FILE = "data/test_report/fasta.csv"
    VERSION_FILE = "data/test_report/versions.csv"
    EMUFOLDER = "data/test_report/"

##########
LONG_DF_HEADER = ["species", "tax_id", "abundance", "estimated counts", "abundance total", "% total"]


##### READING EMU OUTPUT FILES #####


def sort_samples(df, sortabund):
    """Sort data frame columns by sample names and most abundant taxa.
    Sample names should start with barcode no: 01, 02, 03; or with barcode49, barcode27 etc.
    If count table is input df set sortabund=True and df is used to sort taxa by abundance.
    """
    header = df.columns.values.tolist()
    taxonomy = [
        name for name in header if not name[0].isdigit() if "barcode" not in name
    ]

    # sort sample columns by name, not taxonomy
    samples = np.sort(df.columns.difference(taxonomy)).tolist()

    # remove columns with threshold - duplicates
    samples = [sample for sample in samples if "threshold" not in sample]
    df = df.loc[:, taxonomy + samples].set_index(taxonomy)  # taxonomy as index columns
    df.index.names = taxonomy

    if sortabund == "yes":
        # Remove and save unmapped/unclassified/unassigned row
        unassigned = df.iloc[-1, :]
        df = df.iloc[:-1, :]
        # Add temporary row sum column for sorting
        df = (
            df.assign(sum=df.sum(axis=1))
            .sort_values(by="sum", ascending=False)
            .drop(["sum"], axis=1)
        )
        df = pd.concat([df, unassigned.to_frame().T])
        df.index.names = taxonomy
        return df
    else:
        return df


def create_sample_file_dict(result_folder):
    """ Create dict of sample name and rel-abundance output file """
    sample_dict = {}
    for file in os.listdir(result_folder):
        if file.endswith(("_rel-abundance.tsv")):
            sample_dict[file.split("_rel-abundance.tsv")[0].rsplit(".", 1)[0].strip()] = (
                os.path.join(result_folder, file)
            )
    sample_dict = dict(sorted(sample_dict.items()))  # sort by sample name
    return sample_dict


def sample_tsv_to_list(sample_dict):
    """ Append all data from rel-abundance.tsv files to a list """
    long_list = []
    for sample, file in sample_dict.items():
        # print(sample, file)
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
    return long_list


def create_long_df(long_list, df_header):
    """ Convert list of rel-abundance data to one dataframe for all samples """
    long_df = pd.concat(long_list, axis=0, ignore_index=True)
    long_df = long_df.set_index("Sample")
    long_df = long_df[long_df.columns.intersection(df_header)]
    long_df = long_df[df_header]
    unmapped = long_df["tax_id"] == "unmapped"
    unclassified = long_df["tax_id"] == "mapped_unclassified"
    long_df.loc[unmapped, "species"] = long_df.loc[unmapped, "tax_id"]
    long_df.loc[unclassified, "species"] = long_df.loc[unclassified, "tax_id"]
    long_df = long_df.drop(["tax_id"], axis=1)
    return long_df


def create_qc_df(fasta_csv, long_df):
    """Create qc data frame including no of reads in fasta files and unmapped/unclassified from long dataframe"""
    qc_csv = pd.read_csv(fasta_csv, sep=",", index_col=0, names=["#filtered"])

    long_df = long_df.drop(["abundance","abundance total", "% total"], axis=1)
    unmapped_df = long_df.loc[long_df["species"] == "unmapped"].rename(columns={"estimated counts": "#unmapped"})
    unclassified_df = long_df.loc[long_df["species"] == "mapped_unclassified"].rename(columns={"estimated counts": "#mapped_unclassified"})

    qc_csv = pd.concat([qc_csv, unmapped_df, unclassified_df], axis=1).sort_index()
    qc_csv = qc_csv.drop(["species"], axis=1)
    qc_csv["%assigned"] = 100 - ((qc_csv["#unmapped"] + qc_csv["#mapped_unclassified"]) / qc_csv["#filtered"]*100)
    qc_csv.index = qc_csv.index.str.rsplit(".", n=1).str[0].str.strip()

    return qc_csv


# LONG FORMAT - rel-abundance.tsv
all_samples = create_sample_file_dict(EMUFOLDER)
all_samples_list = sample_tsv_to_list(all_samples)
long_format_df = create_long_df(all_samples_list, LONG_DF_HEADER)

# COUNTS EMU - tsv
count_data = pd.read_csv(COUNT_FILE, sep="\t", header=0)
count_data = sort_samples(count_data, "yes")
count_data.columns = count_data.columns.str.rsplit(".", n=1).str[0].str.strip() # remove .fasta/.fastq

# RELATIVE ABUNDANCE EMU - tsv
ra_data = pd.read_csv(RA_FILE, sep="\t", header=0)
ra_data = sort_samples(ra_data, "no")
ra_data.columns = ra_data.columns.str.rsplit(".", n=1).str[0].str.strip()
ra_data = ra_data.reindex(count_data.index)  # same sorting as count sheet (abundance)

# QC SHEET
qc_df = create_qc_df(CSV_FILE, long_format_df)

# SOFTWARE SHEET
versions_csv = pd.read_csv(VERSION_FILE, sep=",", header=None)
versions_csv.loc[-1] = ["report_date", pd.Timestamp.today()]  # add date as first row
versions_csv.index = versions_csv.index + 1
versions_csv.sort_index(inplace=True)


##### WRITING TO EXCEL FILE #####
def get_rows(df, content):
    """Get list of rows indices in dataframe if row has content (for example rows from the same sample)"""
    rows = df[
        df.map(
            lambda x: True if isinstance(x, str) and content in x else False
        ).any(axis=1)
    ].index.tolist()
    return rows


def format_rows(worksheet, row, report_format):
    """Format rows in excel file, arguments: row, height, cell_format, options"""
    worksheet.set_row(row + 1, None, report_format)


# From config
report_params = dict(versions_csv.to_numpy())

with pd.ExcelWriter(OUTPUT_EXCEL, engine="xlsxwriter") as writer:

    versions_csv.to_excel(writer, sheet_name="software", index=False, header=False)
    qc_df.to_excel(writer, sheet_name="qc", index=True, float_format="%.2f")
    long_format_df.to_excel(writer, sheet_name="emu_long", index=True, float_format="%.2f")
    count_data.to_excel(
        writer, sheet_name="emu_counts", index=True, float_format="%.2f"
    )
    ra_data.to_excel(
        writer, sheet_name="emu_proportions", index=True, float_format="%.2f"
    )

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
    fail_reads_format = workbook.add_format({"color": "red", "bottom": 1})

    for worksheet in workbook.worksheets():
        worksheet.set_column("A:A", 25, bold_format)  # width of cell
        worksheet.set_row(0, 15, bold_format)  # default row height
        worksheet.freeze_panes(1, 1)

        for taxon in report_params["spike_taxa"].split(","):
            worksheet.conditional_format(
                1,
                1,
                len(long_format_df),
                len(count_data.columns),  # (first_row, first_col, last_row, last_col)
                {
                    "type": "text",
                    "criteria": "containing",
                    "value": taxon.strip().strip('"'),
                    "format": spike_format,
                },
            )

        if worksheet.get_name() == "software":
            worksheet.set_column("B:B", 30)

        if worksheet.get_name() == "emu_long":
            worksheet.set_column("B:B", 25)

            # Conditional formatting
            long_format_df.reset_index(inplace=True)
            for sample, path in all_samples.items():
                continue_sample = False
                sample_rows = get_rows(long_format_df, sample)
                #print(f"Processing sample: {sample} with rows {sample_rows}")

                total_row = None
                unmapped_row = None
                unclasssified_row = None

                # Get "non-species" rows for the sample, handle total row
                for row in sample_rows:
                    if long_format_df["species"][row] == "total":
                        total_row = row
                        #print(f"Total row: {total_row}")
                        if int(long_format_df["estimated counts"][total_row]) < int(
                            report_params["min_reads"]
                        ):
                            #print(f"Estimated counts {long_format_df['estimated counts'][total_row]} is less than {report_params['min_reads']}")
                            format_rows(worksheet, total_row, fail_reads_format)
                        #    continue_sample = True
                        else:
                            format_rows(
                                worksheet, total_row, border_format
                            )  # mark last row
                    elif long_format_df["species"][row] == "unmapped":
                        unmapped_row = row
                        #print(f"Unmapped row: {unmapped_row}")
                    elif long_format_df["species"][row] == "mapped_unclassified":
                        unclassified_row = row
                        #print(f"Mapped unclassified row: {unclassified_row}")

                # Check max_unassigned criteria
                unassigned_prop = float(long_format_df["abundance total"][unmapped_row]) + float(long_format_df["abundance total"][unclassified_row])
                if float(unassigned_prop) >= float(report_params["max_unassigned_prop"]):
                    #print(f"Abundance total {long_format_df['abundance total'][unmapped_row]} and {long_format_df['abundance total'][unclassified_row]} is greater than {report_params['max_unassigned_prop']}")
                    for row in sample_rows:
                        if not continue_sample and row == unmapped_row:
                                format_rows(worksheet, unmapped_row, fail_cutoff_format)
                        elif not continue_sample and row == unclassified_row:
                                format_rows(worksheet, unclassified_row, fail_cutoff_format)
                                continue_sample = True

                # Highlight taxa passing cutoff
                for row in sample_rows:
                    if not continue_sample and (
                        row != unmapped_row and row != unclassified_row and row != total_row
                    ):
                        if (
                            float(long_format_df["abundance total"][row])
                            >= float(report_params["min_abund_tot"])
                        ) and (float(long_format_df["estimated counts"][row])) >= int(
                            report_params["min_counts_taxa"]
                        ):
                            #print(f"Abundance total {long_format_df['abundance total'][row]} for {long_format_df['species'][row]} is greater than {report_params['min_abund_tot']}")
                            format_rows(worksheet, row, pass_cutoff_format)

                if continue_sample:
                    #print(f"Continuing to next sample due to conditions met in sample: {sample}")
                    continue
