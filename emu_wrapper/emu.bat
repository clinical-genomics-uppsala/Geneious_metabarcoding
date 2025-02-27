:: Path to current directory to bundled optional files
set pluginPath=%~dp0

:: Output to Geneious
set outFile=%2

:: Options from Geneious
set pathToGeneiousData=%4
set configFile=%6
set pathToData=%8


python "%pluginPath%emu.py" -o %outFile% -g %pathToGeneiousData% -p %configFile% -f %pathToData%

:: Wrapper Plugin Creator command line: -o emu_output.tsv -g [inputFolderName] [otherOptions]
