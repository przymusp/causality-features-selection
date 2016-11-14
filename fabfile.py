from fabric.api import run, local

def update_python_requirements():
    local('pipreqs --force .')
