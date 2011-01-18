import os, subprocess
import sys
import shutil

def mercurial_clone():
    pass

def die(msg):
    print msg
    sys.exit()

def get_env():
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    return env

def clone(url, path):
    cmd = subprocess.Popen(
        ['hg', 'clone', '--quiet', '--noninteractive', url, path],
        env=get_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    if cmd.returncode != 0:
        die("hg clone failed.")

def pull(path):
    cmd = subprocess.Popen(
        ['hg', 'pull', '--quiet', '--noninteractive',
         '--repository', path],
        env=get_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    if cmd.returncode != 0:
        die("hg update failed.")

def update_to_release(path, release):
    cmd = subprocess.Popen(
        ['hg', 'update', '--quiet', '--noninteractive',
         '--repository', path, release],
        env=get_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    if cmd.returncode != 0:
        die("hg update failed.")

def do(path, command, *options):
    original_path = os.getcwd()
    l = [command] + list(options)
    try:
        os.chdir(path)
        cmd = subprocess.Popen(
            l, env=get_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = cmd.communicate()
        if cmd.returncode != 0:
            die('%s failed.' % command)
    finally:
        os.chdir(original_path)

def bootstrap(path):
    do(path, 'python2.6', 'bootstrap.py', '-d')
    
def buildout(path):
    do(path, 'bin/buildout', '-N')

def sphinxbuild(path):
    do(path, '/bin/bash', 'bin/sphinxbuilder')

def create_page(releases):
    pass

class Outputter(object):
    def __init__(self, verbose):
        self.verbose = verbose

    def __call__(self, msg):
        if self.verbose:
            print msg
        
def build_release_docs(hg_url, repository_path, releases, destination_path,
                       verbose=False):
    output = Outputter(verbose)
    if os.path.exists(repository_path):
        output("Repository exists, pulling updates")
        pull(repository_path)
    else:
        output("Cloning repository", verbose)
        os.mkdir(repository_path)
        clone(hg_url, repository_path)
    if os.path.exists(destination_path):
        output("Destination directory exists, clearing destination directory")
        shutil.rmtree(destination_path)
    output("Creating destination directory")
    os.mkdir(destination_path)
    for release in releases:
        output("Release: %s" % release)
        output("Cloning for release")
        release_path = os.path.join(destination_path, release)
        os.mkdir(release_path)
        clone(repository_path, release_path)
        output("Updating to release")
        update_to_release(release_path, release)
        output("Running bootstrap.py")
        bootstrap(release_path)
        output("Running bin/buildout")
        buildout(release_path)
        output("Running bin/sphinxbuilder")
        sphinxbuild(release_path)

def main():
    build_release_docs('https://bitbucket.org/fanstatic/fanstatic',
                       'repos', ['0.9b', 'default'], 'out', verbose=True)
    
if __name__ == '__main__':
    main()
    
