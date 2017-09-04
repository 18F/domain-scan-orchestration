from subprocess import call

call(["cf", "push", "-f", "manifest_celery_worker.yml"])
call(["cf", "push", "-f", "manifest_celery_beat.yml"])
call(["cf", "push", "-f", "manifest.yml"])
