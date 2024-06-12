:: Path to current directory to bundled optional files
set pluginPath=%~dp0

:: Output to Geneious
set outFile=%2

:: Options from Geneious
set pathToGeneiousData=%4
set pathToDocker=%6
set pathToData=%8
shift
shift
shift
shift
shift
shift
set kronaImage=%4
set emuImage=%6
set noThreads=%8

python "%pluginPath%emu.py" -o %outFile% -g %pathToGeneiousData% -d %pathToDocker% -f %pathToData% -k %kronaImage% -i %emuImage% -t %noThreads%

:: -o emu_output.tsv -g [inputFolderName] [otherOptions]
