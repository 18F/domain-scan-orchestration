from subprocess import call

call(["cf","push","manifest_celery_worker.yml"])
call(["cf","push","manifest_celery_beat.yml"])
call(["cf","push","manifest.yml"])
