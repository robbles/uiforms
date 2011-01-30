from fabric.api import *

env.hosts = ['robbles@testing.doteight.com']

def deploy():
    # Update from GitHub repo master branch
    with cd('webapps/uiforms/uiforms/'):
        run('git pull origin master')

    # Show the last commit as a sanity check
    run('git log -n1')

    # Restart Apache
    with cd('webapps/uiforms/apache2/bin'):
        run('restart')


