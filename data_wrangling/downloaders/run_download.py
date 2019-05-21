from subprocess import run

sel = ''
while True:
    if sel == 's' or sel == 'm':
        break
    sel = input('single or multiprocess download?[s/m]')
    
if sel == 's':
    run('cmd /c cd ./single_proc/ & run.bat')
elif sel == 'm':
    run('cmd /c cd ./multi_proc/ & run.bat')