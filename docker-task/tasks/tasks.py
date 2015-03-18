from celery.task import task
from time import sleep
import paramiko as pk
import os, json
import getpass

#Example task
@task()
def add(x, y):
    result = x + y
    return result

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
        docker_command_args=None
    ):
    """ Put together a string for running docker """
    # Set up the docker command line for remote worker
    if docker_opts == None:
        docker_run = 'docker run -d %s' % (docker_name)
    else:
        docker_run = 'docker run -d %s %s' % (docker_opts, docker_name)
    # if the command to run is specified overide default for that Dockerfile
    if docker_command != None:
        docker_run = docker_run + " " + docker_command
    return docker_run

def isrunning(state):
    if state['Running']:
        return True
    else:
        return False

@task
def remote_task(
    docker_worker=None,
    docker_name=None,
    docker_opts=None,
    docker_command = None
    ):
    """
    docker_worker => the remote host to run docker container upon
    docker_name => the docker hub name for the container to run
    docker_opts => options to docker such as -v --net='host' etc
    docker_command => the command to run inside the docker
    """
    task_id = str(remote_task.request.id)

    try:
        username = os.environ['docker_username']
    except:
        username = getpass.getuser()

    ssh = ssh_client(docker_worker, 22, username)

    if docker_worker == None:
        try:
            docker_worker = os.environ['docker_worker']
        except:
            print "Please set environtment variable docker_worker="

    if docker_name == None:
        try:
            docker_name = os.environ['docker_name']
        except:
            print "Please set environment variable docker_name="
    if

    cmd = docker_command_string(
            docker_name,
            docker_opts,
            docker_command)

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
                    return { "host": docker_worker, "task_id": str(task_id) }
                else:
                    raise Exception(state['Error'])
    else:
        raise Exception(std_err)


@task()
def qc_docker_workflow(forward_read_filename, reverse_read_filename, basedir="/data/static/",docker_worker=os.environ['docker_worker']):
    resultDir = os.path.join(basedir, 'mgmic_tasks/', str(qc_docker_workflow.request.id))
    os.makedirs(resultDir)
    ssh = pk.SSHClient()
    ssh.set_missing_host_key_policy(pk.AutoAddPolicy())
    #keys setup to login as pass environmental username to docker
    ssh.connect(docker_worker,22,os.environ['username'])
    cmd ='docker run -d -v /opt/local/scripts/:/scripts -v /data/static:/data/static bwawrik/bioinformatics /scripts/bin/Illumina_MySeq_Trim %s %s %s'
    cmd = cmd % (forward_read_filename,reverse_read_filename,resultDir)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    std_out = stdout.read()
    std_err = stderr.read()
    if std_err == '':
        dock_id = std_out.strip(' \n')
        #Example poll_docker return
        #{u'Pid': 0, u'OOMKilled': True, u'Paused': False, u'Running': False,
        # u'FinishedAt': u'2015-03-13T19:11:31.66940599Z', u'Restarting': False,
        # u'Error': u'', u'StartedAt': u'2015-03-13T19:08:56.879774955Z', u'ExitCode': 0}
        while True:
            poll = docker_state(dock_id,ssh)
            if poll['Running']:
                sleep(10)
            else:
                if poll['ExitCode']==0:
                    return "http://%s/mgmic_tasks/%s" % (docker_worker,str(qc_docker_workflow.request.id))
                else:
                    raise Exception(poll['Error'])
    else:
        raise Exception(std_err)

def docker_state(docker_id,ssh):
    cmd = 'docker inspect %s' % (docker_id)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    std_out = stdout.read()
    std_err = stderr.read()
    if std_err == '':
        data = json.loads(std_out)
        return data[0]['State']
    else:
        raise Exception(std_err)
