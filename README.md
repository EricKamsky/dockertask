docker-task
===========

Low level functions to build tasks that run on docker containers over SSH.


## Environment Variables

Setting the following variables can make calls to dockertask.docker_task() simpler but is not required.

```
export docker_worker="some.hostname.com"
export docker_name="mgmic/qiime"
export docker_username="celeryworker"
```

## Using with Celery

```
from celery.task import task
import dockertask

@task
def mytask(args):
    return dockertask.docker_task(docker_worker="some.host.com",
            docker_name="hubuser/dockername:tag",
            docker_opts="-v /data:/data",
            docker_command="somescript %s" % args, id=str(mytask.request.id))

```
