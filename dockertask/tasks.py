from time import sleep
import paramiko as pk
import os, json
import getpass


def ssh_client(host,port,username):
    """ Create a paramiko connection object and return it """
    ssh = pk.SSHClient()
    ssh.set_missing_host_key_policy(pk.AutoAddPolicy())
    ssh.connect(host,port,username)
    return ssh

def docker_command_string(
        docker_name,
        docker_opts=None,
        docker_command=None,
        docker_run_args=None
    ):
    """ Put together a string for running docker """
    # Set up the docker command line for remote worker
    if docker_opts == None:
        if docker_run_args:
            docker_run = 'docker run %s %s' % (docker_run_args,docker_name)
        else:
            docker_run = 'docker run -d %s' % (docker_name)
    else:
        if docker_run_args:
            docker_run = 'docker run %s %s %s' % (docker_run_args,docker_opts, docker_name)
        else:
            docker_run = 'docker run -d %s %s' % (docker_opts, docker_name)
    # if the command to run is specified overide default for that Dockerfile
    if docker_command != None:
        docker_run = docker_run + " " + docker_command
    if os.environ.get('docker_env_cmd'): 
        docker_run = os.environ.get('docker_env_cmd') + ' && ' + docker_run
    return docker_run

def isrunning(state):
    """ Check if docker inspect object has a state of Running = True """
    if state['Running']:
        return True
    else:
        return False

def docker_task(
    docker_worker=None,
    docker_name=None,
    docker_opts=None,
    docker_command = None,
    id=None,
    docker_run_args = "-d"):
    """
    docker_worker => the remote host to run docker container upon
    docker_name => the docker hub name for the container to run
    docker_opts => options to docker such as -v --net='host' etc
    docker_command => the command to run inside the docker
    id => Some unique identifier of the calling task for managing output
    """

    try:
        username = os.environ['docker_username']
    except:
        username = getpass.getuser()


    if docker_worker == None:
        try:
            docker_worker = os.environ['docker_worker']
        except:
            print "Please set environtment variable docker_worker="

    ssh = ssh_client(docker_worker, 22, username)

    if docker_name == None:
        try:
            docker_name = os.environ['docker_name']
        except:
            print "Please set environment variable docker_name="

    cmd = docker_command_string(
            docker_name,
            docker_opts,
            docker_command,
            docker_run_args)

    stdin, stdout, stderr = ssh.exec_command(cmd)
    std_err = stderr.read()
    std_out = stdout.read()

    if std_err == '':

        docker_id = std_out.strip(' \n')

        while True:
            state = docker_state(docker_id,ssh)
            if isrunning(state):
                sleep(5)
            else:
                if state['ExitCode']==0:
                    return { "host": docker_worker, "task_id": id }
                else:
                    raise Exception(state['Error'])
    else:
        raise Exception(std_err)

def docker_state(docker_id,ssh):
    """ Using `docker inspect`, check state of a running docker """
    cmd = 'docker inspect %s' % (docker_id)
    if os.environ.get('docker_env_cmd'):
        cmd = os.environ.get('docker_env_cmd') + ' && ' + cmd
    stdin, stdout, stderr = ssh.exec_command(cmd)
    std_out = stdout.read()
    std_err = stderr.read()
    if std_err == '':
        data = json.loads(std_out)
        return data[0]['State']
    else:
        raise Exception(std_err)
