### WordPress CL

What do I want it to do next week

> run and execute from the command line - like phpsh - after installing for user

> installs a .sh file on first use for easy of use (on click)

> run natively and save options to local file deploy.json or something
OPTIONAL > can run from any wp directory, will move up to 

> somehow does SCP. Actually will just prompt for a password. THAT WORKS!

'bloop'
'bb1c76be'





What would it need to do?

 1. Run deploy scripts to a server, can specify what can be migrated - should save some of these options

 2. Launch a shell - phpsh

 3. Install PHPMyAdmin

 4. Install a fresh version of wordpress from cl

 5. Install a fresh DB from cl

 6. Change DB's from cl

Fork http://wp-cli.org/ ?


? http://www.saintsjd.com/2011/01/continuous-deployment-for-wordpress-using-git-and-fabric/
? http://blog.loopion.com/post/wordpress-bash-deployment-script/
? https://github.com/newsapps/wp-project-tools
? http://docs.python.org/2/distutils/setupscript.html


>>>> DEPLOYING FROM NOAH AND ME
Part 1: have a deploy scrpt built the site. I don't know how this would work... a plugin maybe? Could run ` ./wp-content/deploy ` to get the 

Part 2: Git - `git add .; git commit -m "pushing"; git push origin master;`

Part 3: Post receive-push do a mysql load (another script?)

Part 4: `./wp-content/dbpull ` or something to grab the external db