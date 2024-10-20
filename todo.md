##Todo

- [x] Get DevContainers configured and running for fedora/wsl2
    - [x] Make devcontainer work platform agnostic
    - [x] Setup dependencies with poetry
    - [x] Setup make and create makefile 

- [x] Make very, very basic poc
    - [x] Understand how to return a basic html with flask
    - [x] Draft first interface
    - [x] Return basic text for tasks

- [x] Implement modular OOP DB MVP Code
    - [x] Config for SQL-Alchemy
        - [x] create from file, dict
        - [x] validate
    - [x] Simple SQLAlchemy- init script
    - [x] Data-Classes with pydantic
    - [x] SQL-Alchecmy Objects 
    - [x] App specific CRUD functionality
    - [x] Populate with test-data

- [ ] Work on App / Frontend
    - [ ] Conceptualize different parts of the FE
    - [ ] Think about the routes and DB interactions it will have
    - [ ] Make use of tempates
    - [ ] Use CRUD to display and manage task-app

- [ ] Implement Template DB MVP
    - [ ] Make it possible to Create and Delete a Task
        - [x] Make Use of templates to load and display the tasks
            - [ ] Redesign to display description and maybe deadline
        - [x] Display all the tasks for the Users at the start of the session
            - [x] Always get the tasks at page refresh
        - [x] Make Add Task Clickable, Pop-up for all Input fields
        - [ ] Introduce Button on the Right of the Task Field for deletion

- [ ] Unit Testing
    - [ ] config
    - [ ] database
    - [ ] crud
    - [ ] Build github actions pipeline with them


- [ ] Package into a deployable container
    - [ ] Setup a Dockerfile and configure it to be deployable in a platform agnostic way
    - [ ] Get network/port config right for localhost
    - [ ] Make it work with Flask, render text/html

    