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
    - [ ] Make use of temlpates
    - [ ] Use CRUD to display and manage task-app


- [x] Make it possible to Create and Delete a Task
    - [x] Make Use of templates to load and display the tasks
    - [x] Display all the tasks for the Users at the start of the session
        - [x] Always get the tasks at page refresh
    - [x] Make Add Task Clickable, Pop-up for all Input fields
    - [x] Introduce Button on the Right of the Task Field for deletion
        - [x] Make a new item tamplate which gets activated on mouse-hover, which shows deletion and update icon
        - [x] When delete is clicked -> db- delete -> list-refresh
    - [x] Make search dynamic, hx-tager=list, return a renderd version of the list
    
 - [ ] Make tasks editable
    - [ ] When edit is clicked -> make content editable -> when title is changed
        - [ ] this might be tricky, as i have to update and then instantly refresh, maybe introdcue an delay to minimize db requests

- [ ] Unit Testing
    - [ ] config
    - [ ] database
    - [ ] crud
    - [ ] Build github actions pipeline with them


- [ ] Package into a deployable container
    - [ ] Setup a Dockerfile and configure it to be deployable in a platform agnostic way
    - [ ] Get network/port config right for localhost
    - [ ] Make it work with Flask, render text/html

    