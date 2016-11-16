from fabric.api import run, local, lcd

def update_python_requirements():
    local('pipreqs --force .')

def get_uci_dataset():
    with lcd("src/tools/download_uci_ml/"):
        local("scrapy crawl uci")
