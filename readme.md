## Moving Sh*t with Python!

Hey are you moving shit - especially WordPress shit - between hosts? Want to learn some Python?!?

<<<<<<< HEAD
Well I was and I did - so I did! I wrote a bunch of little scripts `doit.py`, `drop_comments.py`, `heller.py`, `backup.py` all use some handy classes to move stuff between two hosts, install / mess with WordPress, and do some other stuff.
=======
Well I did. So I wrote a bunch of scripts! These little scripts in the [examples](/examples) directory like `doit.py`, `drop_comments.py`, `heller.py`, `backup.py` all use some handy classes to move stuff between two hosts, install / mess with WordPress, and do some other stuff.

All of these can be run using run.py - which makes importing and whatnot work better, just pass the name of the script you'd like to run. Arguments and what not are passed along (well not the first one).

For example: `python run.py deploy /my/local/site /my/remote/site` will move your site

There's also `console.py` for loading everything in the models subfolder and creating some `WebFaction` and `SSH` objects with the passwords loaded from secrets.ini. How useful, eh?
>>>>>>> Updating readme.md

I'm going to keep using - and improving on these classes - to do random shit!

### The modules that matter:
All of these are in in the [models](/models) directory

 * *WebFaction* - Uses the [WebFaction](docs.webfaction.com/xmlrpc-api/) API to create WordPress sites and such.

 * *SSH* - Uses [Parmiko](https://github.com/paramiko/paramiko) to control some severs. Does some error handling and processing of STDOUT

 * *Local* - Basically *SSH* for doing stuff on a local machine. Woo!

 * *Sites* - Is a framework for most of the action in `doit.py`. This manages the backing up, installing (using WebFactin's API), and moving of WordPress sites. Uses the *WebFaction* and *SSH* classes extensively.


