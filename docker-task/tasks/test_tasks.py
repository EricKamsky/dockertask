import tasks
import getpass

def getusername():
    return getpass.getuser()

def test_ssh():
    ssh = tasks.ssh_client('static.cybercommons.org',22,getusername())
    stdin, stdout, stderr = ssh.exec_command('hostname')
    out = stdout.read()
    print out
    assert out == 'static.cybercommons.org\n'

def test_docker_command_string_simple():
    output = tasks.docker_command_string("nginx")
    assert output == 'docker run -d nginx'

def test_docker_command_string_options():
    output = tasks.docker_command_string("nginx", "-v /data:/data")
    assert output == "docker run -d -v /data:/data nginx"

def test_docker_command_string_options_command():
    output = tasks.docker_command_string("nginx", "-v /data:/data", "/bin/bash")
    assert output == "docker run -d -v /data:/data nginx /bin/bash"

def test_isrunning():
    state = {u'Pid': 0, u'OOMKilled': True, u'Paused': False, u'Running': True,
        u'FinishedAt': u'2015-03-13T19:11:31.66940599Z', u'Restarting': False,
         u'Error': u'', u'StartedAt': u'2015-03-13T19:08:56.879774955Z', u'ExitCode': 0}
    running = tasks.isrunning(state)
    assert running == True

def test_isntrunning():
    state = {u'Pid': 0, u'OOMKilled': True, u'Paused': False, u'Running': False,
        u'FinishedAt': u'2015-03-13T19:11:31.66940599Z', u'Restarting': False,
         u'Error': u'', u'StartedAt': u'2015-03-13T19:08:56.879774955Z', u'ExitCode': 0}
    running = tasks.isrunning(state)
    assert running == False

def test_remote_task():
    tasks.remote_task('wind.rccc.ou.edu', 'ubuntu', docker_opts=None, docker_command='sleep 2')
