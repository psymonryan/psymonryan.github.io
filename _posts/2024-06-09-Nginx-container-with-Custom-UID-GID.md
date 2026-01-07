---
title: Running an Nginx container with a Custom UID and GID
date: 2024-06-09 14:00:00 +1000
description: Learn how to run an Nginx container with custom UID and GID, solving permission issues with host filesystems and implementing user namespace remapping for enhanced security.
categories: [docker]
tags: [container]
---

## Introduction

If this sounds like you, then keep reading:
- Are you sick of the hard coded uid of 101 and gid of 101 ?
- Do you want to run as a non-root user, but need to customise the UID and GID used by the container process?
- Do you want to keep it simple and not create your own Dockerfile so you can readily keep your nginx container updated without any extra hassle?
- Have you already scoured the internet looking for solutions?

It turns out that what we need is [User Namespace Remapping](https://docs.docker.com/engine/security/userns-remap/) - User namespace remapping in Docker allows containers to have a different set of UID/GID mappings compared to the host system, enhancing security by isolating container processes from the host's user and group IDs. It is also particularly useful when aligning with the uid/gid of volumes mounted from the host filesystem. 

How many of us use the official nginx container? Ok lots of people, a quick glance on dockerhub and we see that it has chalked up more than a Billion downloads. :sweat_smile:


![NGINX](<../assets/pimg/nginx downloads on docker hub.png>)

However, the official image (and even the [Official Docker NGINX unprivileged image⁠](https://hub.docker.com/r/nginxinc/nginx-unprivileged)) don't offer us any immediate solution.

My searches trying to figure out how to do this only found github issues complaining about it eg: [Update UID and GID to 10001 (>10000)](https://github.com/nginxinc/docker-nginx-unprivileged/issues/149)

## Things I already tried (that didn't work)
- Setting environment variables (in Kubernetes manifests or Nomad job files)
  - Normally nomad job files let me do this by setting the PGID and PGID environment variables, but for some reason its not working for me in this case. (I think most of the containers I am using honour this standard, but nginx just ignores it)
  
- Attempting to force the issue (as a command line test) with the official nginx image:
  ```bash
  $ docker run -it --rm --name="nginx-experiment" --user "1000:1000" nginx
...
/docker-entrypoint.sh: Configuration complete; ready for start up
2024/06/09 05:32:39 [warn] 1#1: the "user" directive makes sense only if the master process runs with super-user privileges, ignored in /etc/nginx/nginx.conf:2
nginx: [warn] the "user" directive makes sense only if the master process runs with super-user privileges, ignored in /etc/nginx/nginx.conf:2
2024/06/09 05:32:39 [emerg] 1#1: mkdir() "/var/cache/nginx/client_temp" failed (13: Permission denied)
nginx: [emerg] mkdir() "/var/cache/nginx/client_temp" failed (13: Permission denied)
```
    This doesn't work because the tmp directories inside the container are not writable for my custom UID.

 - Customising Nginx Config files by trying to add ```user 1000;``` directive
 ```bash
 $ docker run -it --rm --name="nginx-experiment" -v /Users/simon/src/docker/nginx.conf:/etc/nginx/nginx.conf:ro nginx
 ...
 /docker-entrypoint.sh: Configuration complete; ready for start up
2024/06/09 07:55:02 [emerg] 1#1: getpwnam("1000") failed in /etc/nginx/nginx.conf:2
nginx: [emerg] getpwnam("1000") failed in /etc/nginx/nginx.conf:2
 ```
    This one doesn't work because it seems that you can only add a valid username (ie: once that has to be present inside /etc/passwd)

 - I considered creating a custom Dockerfile

   This could work (there are a few example solutions out there for this), but this would add some extra complexity to my image update pipeline with an extra build step required every time the image was updated. There must be an easier way! 

## Custom UID and GID [SOLVED]

I'm going to use the unprivileged image as a starting point (```nginxinc/nginx-unprivileged```)
The reason for this is that it does a few critical things that allow us to get away with asking our containerisation framework to do user namespace remapping.

1. It removes the 'user' directive from the default config file (so we can ignore the 'nginx' entry in the passwd file)
2. It moves the nginx.pid file out of the /var/run privileged directory to "anyone can write here" temp directory /tmp
3. It also changes the *_temp_path variables to /tmp/ - which is writable by any UID/GID

With all this in place if we can then force the orchestration framework to load the image as a different uid/gid, and theoretically we wont see any complaint from the image.

Before we move on, lets give this a try from the command line:

```bash
$ docker run -it --rm --name="nginx-experiment" --user "1000:1000" nginxinc/nginx-unprivileged
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
10-listen-on-ipv6-by-default.sh: info: can not modify /etc/nginx/conf.d/default.conf (read-only file system?)
/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
/docker-entrypoint.sh: Configuration complete; ready for start up
2024/06/09 05:34:29 [notice] 1#1: using the "epoll" event method
2024/06/09 05:34:29 [notice] 1#1: nginx/1.27.0
2024/06/09 05:34:29 [notice] 1#1: built by gcc 12.2.0 (Debian 12.2.0-14)
2024/06/09 05:34:29 [notice] 1#1: OS: Linux 5.15.49-linuxkit
2024/06/09 05:34:29 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
2024/06/09 05:34:29 [notice] 1#1: start worker processes
2024/06/09 05:34:29 [notice] 1#1: start worker process 21
2024/06/09 05:34:29 [notice] 1#1: start worker process 22
```

Ok this looks happy as it is no longer complaining about permissions. So now I need this to run in my Nomad cluster.

In order to get Nomad to run a job as the non-default user this needs to be specified as a [task parameter](https://developer.hashicorp.com/nomad/docs/job-specification/task#user). Unfortunately the format of this is not very well documented, however, similar to command line docker, it turns out that Nomad is also happy to use the "UID:GID" format, allowing us to also modify the GID.

```hcl
    task "nginx" {
        driver = "docker"
        user = "1000:1000"

        config {
            image = "nginxinc/nginx-unprivileged"
            ports = ["http"]
            ...
        }
```

If you are using Kubernetes, things are a little easier and you have a couple of options. First you can just do the equivalent of the above, with something like:

```yml
  securityContext:
    runAsUser: 1000
    runAsGroup: 1000
```

Or, you might like to leave the internal UID/GID mapping 'as-is' and just do a filesystem group mapping. ie:

```
  securityContext:
    runAsUser: 101
    runAsGroup: 101
    fsGroup: 1000
```


## Validation for Nomad

Now when we exec[^1] into the container and look at the UID and GID of process 1[^2] we can see:
```bash
simon@mymac: > nomad alloc exec -i -t -job nginx /bin/sh
$ grep [GU]id: /proc/1/status
Uid:    1000    1000    1000    1000
Gid:    1000    1000    1000    1000
```

Ok, fantastic, I'm happy, now I can get on with things knowing that nginx will cooperate nicely with my filesystem :grinning:

----

[^1]: Since the nginx container is super lean, there is no *ps* command, however we can find the UID/GID by peering into the /proc entry for process 1 using this method.

[^2]: I'm using *nomad alloc exec* here, but you could also use *docker exec* or *kubectl exec*

