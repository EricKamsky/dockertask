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
