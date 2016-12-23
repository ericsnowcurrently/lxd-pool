*********
lXD-pool
*********

A library (and tool) for managing a pool of LXD containers.

.. TODO: more intro here


.. contents:: Table of Contents
   :depth: 2


How to Use
==============

TBD


Development
==============

TBD


Abount LXD
==============

https://linuxcontainers.org/lxd/
https://github.com/lxc/lxd

TBD

(pre-defined) images
------------------------

"ubuntu:14.04"

* list

  * lxc image list
  * lxc image list <remote>:

* create

  * lxc image copy <image>
  * lxc image copy <image>  --alias <image>
  * lxc image copy <remote>:<image>
  * lxc image copy <image> --auto-update
  * lxc publish <container>
  * lxc publish <container> <prop-key>=<value>

* destroy

  * lxc image delete <image>

* update

  *

* archive

  * lxc image export <image>

* restore

  * lxc image import <tarball> --alias <image>

container management
------------------------

* list

  * lxc list

* create

  * lxc launch <image> <container>
  * lxc launch <remote>:<image> <container>
  * lxc launch <image> <container> --ephemeral
  * lxc launch <image> --profile <profile> --config <key>=<value> <container>

* destroy

  * lxc delete <container>

* start

  * lxc start <container>

* stop

  * lxc stop <container>

* other

  * lxc info <container>
  * lxc move <old name> <new name>
  * lxc copy <container> <container>

snapshots
---------

* list

  *

* create

  * lxc snapshot <container> <snapshot>

* destroy

  * lxc delete <snapshot>

* restore

  * lxc restore <container> <snapshot>

running commands
-------------------

* exec

  * lxc exec <container> <command>
  * lxc exec <container> --env <var>=<value> <command>

files/artifacts
-------------------

* pull

  * lxc file pull <container>/<filename> <local>

* push

  * lxc file push <local> <container>/<filename>

other
---------

defaults::

  * ubuntu: (for stable Ubuntu images)
  * ubuntu-daily: (for daily Ubuntu images)
  * images: (for a bunch of other distros)

* remotes

  * lxc remote add <remote> <address>

* config

  * lxc config ...

* profiles

  * lxc profile ...

* migrating containers

  * lxc move <container> <remote>:<container>

TBD

.. TODO: migrating containers?


Snaps
=========

TBD


Juju
=========

TBD


Alternatives
==============

TBD

.. TODO: mention docker?
