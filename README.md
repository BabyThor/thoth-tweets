# thoth-tweets

**Requirements**
- Docker compose

**How to setup project**
1. Clone project.
2. Create settings.py from `settings-example.py` and update API key in settings file
3. run command `docker-compose up --build`
  - check your docker host IP `docker-machine env default`
4. access application by `docker-host-ip:5000/`
