# github_watchdog

A little python exercise

A docker container can be built and run via:

touch githhub_watchdog.log

docker build -t git_watchdog .

docker run -dit -v ~/github_watchdog.log:/github_watchdog/github_watchdog.log -v ~/persist:/github_watchdog/persist git_watchdog
