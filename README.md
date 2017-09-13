# Domain Scan Orchestration

## Set up

The steps that follow are needed to set up the mechanism to schedule jobs.

### First - clone the repo:

`git clone https://github.com/18F/domain-scan-orchestration`

### Second - Providing credentials:

*   
	`options.creds` - this is a json file that was serialized with python's built in json library and the following code:

```
	import json
	dicter = { 
		"censys_id": "", 
		"censys_key": "", 
		"query": "parsed.subject.common_name:/gov/ or parsed.extensions.subject_alt_name.dns_names:/gov/", 
		"export": true
	}
	json.dump(open("options.creds"))
```

You'll need to fill in censys_id and censys_key with your credentials from [censys](https://censys.io/).

* 

	`github_token.creds` - this is a json file that was serialized with python's built in json library and the following code:

```
	import json
	github_token = ""
	json.dump(github_token, open("github_token.creds","w"))
```

You'll need to get a github token by following the directions found [here](https://github.com/blog/1509-personal-api-tokens)

Make sure both of these commands are run from the top level directory.  

### Third - login to cloud.gov:

[logging in](https://cloud.gov/docs/getting-started/setup/#set-up-the-command-line)

### Fourth - create a database and name it celery-test

To create the database, follow the steps outlined here: https://cloud.gov/docs/services/relational-database/

I'm not sure if you need to run this step, it might be possible to just have the manifest files run this, but I created the database manually and it worked.  I didn't have time to test with having the database get automatically get created from the manifest file.


### Fifth - run the deployer script:

`python deployer.py` 

Run the above command to deploy the three seperate manifests found in:

* manifest.yml

* manifest_celery_worker.yml

* manifest_celery_beat.yml

The next thing you'll need to do is very, very hacky -

Head over to [https://scheduler.app.cloud.gov/initialize_database](https://scheduler.app.cloud.gov/initialize_database).

You'll need to do this to initialize the database to Flask-SQLAlchemy.  This is probably possible to do more easily, but I couldn't figure it out.

Then you'll need to upload a csv with a single column called Domain that has a list of all the domains you'll want to scan.  Head to [https://scheduler.app.cloud.gov](https://scheduler.app.cloud.gov) and upload the file to the upload button that should be on the page.

If you want to make sure that the scheduler is running you can head over to:

[https://scheduler.app.cloud.gov/gather](https://scheduler.app.cloud.gov/gather)

This will kick off the process manually.  If you don't see a change, you can reset the csv by hitting:

[https://scheduler.app.cloud.gov/reset](https://scheduler.app.cloud.gov/reset) and then hitting [https://scheduler.app.cloud.gov/gather](https://scheduler.app.cloud.gov/gather) again.

The csv should return to it's original state which can be found here:

[domain-list.csv](https://github.com/18F/domain-scan-orchestration/blob/master/data/domain-list.csv)

Once you are confident the scheduler works, you can just let it run!  The schedule is set in app.py here:

```
schedule = {
    "gatherer": {
        "task": "app.gatherer",
        "schedule": crontab(0, 0, day_of_week=2),
    },
}
```

If you want to add other tasks, simply add them there.  