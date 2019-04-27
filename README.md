# Is Reddit the Asshole?

## What?

I, like many, am tired of the obvious bait posts on my reddit feed consisting of ridiculous situations in which, yes, 
OP is in fact an asshole.

To that end, I built this application to track the statistics of petitioners to /r/AITA.

## How?

Todo

## Let me at it!

First, install [docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/).

Next, clone the repo:

```sh
$ git clone git@github.com:tristanmkernan/aita.git
```

Grab your reddit client id and secret [here](https://www.reddit.com/prefs/apps):

1. Click 'Create another app'
2. Enter application name, select 'script' option, enter 'localhost' for redirect uri
3. Click 'Create app'
4. Grab client secret and client id (hint: this is the code beneath 'personal use script')
5. Copy `env/docker.env.example` to `env/docker.env`
6. Enter the client secret and client id
7. Update the user agent string to something meaningful and with your username
8. Update the application secret if you are hosting this publicly  

Build the docker images and run the docker images:

```sh
$ # in aita/ directory
$ docker-compose build
$ docker-compose up
```

Note: in case you want to host this application yourself, be sure to change the secret key in `env/docker.env`!

Visit [localhost:8084](http://localhost:8090/) to access your local installation! 



## Who?

Copyright Tristan Kernan. Licensed GPLv3+.