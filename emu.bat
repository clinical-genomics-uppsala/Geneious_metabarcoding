:: Output to Geneious
set outFile=%2

:: Options from Geneious
set pathToGeneiousData=%4
set pathToDocker=%6
set pathToData=%8

:: Path to current directory to bundled optional files
set pluginPath=%~dp0
::set pluginPath=%10

python "%pluginPath%emu.py" -o %outFile% -g %pathToGeneiousData% -d %pathToDocker% -f %pathToData%

:: -o emu_output.tsv -g [inputFolderName] [otherOptions] -p [pluginPath]
