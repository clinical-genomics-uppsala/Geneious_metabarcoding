:: Path to current directory to bundled optional files
set plugin_path=%~dp0

:: Output to Geneious
set outfile=%2

:: Options from Geneious
set path_to_geneious_data=%4
set config_file=%6
set path_to_data=%8


python "%plugin_path%emu.py" -o %outfile% -g %path_to_geneious_data% -p %config_file% -f %path_to_data%

:: Wrapper Plugin Creator command line: -o emu_output.tsv -g [inputFolderName] [otherOptions]
