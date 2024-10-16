##Todo

- [x] Get DevContainers configured and running for fedora/wsl2
    - [x] Make devcontainer work platform agnostic
    - [x] Setup dependencies with poetry
    - [x] Setup make and create makefile 

- [x] Make very, very basic poc
    - [x] Understand how to return a basic html with flask
    - [x] Draft first interface
    - [x] Return basic text for tasks

- [ ] Implement modular OOP DB Code
    - [x] Config for SQL-Alchemy
        - [x] create from file, dict
        - [x] validate
    - [ ] Simple SQLAlchemy- init script
    - [ ] Data-Classes with pydantic
    - [ ] SQL-Alchecmy Objects 
    - [ ] Populate with test-data
    - [ ] App specific CRUD functionality
    - [ ] Init Script which checks and creates a sqllite db
        - [ ] is executed when no parameters are passed to script (prep for cli functionality)

- [ ] Package into a deployable container
    - [ ] Setup a Dockerfile and configure it to be deployable in a platform agnostic way
    - [ ] Get network/port config right for localhost
    - [ ] Make it work with Flask, render text/html

    