# orders
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

NYU DevOps project

## Introduction
This project is the back end for an eCommerce web site as a RESTful microservice for the resource order. An order is a collection of order items created from products and quantity. This microservice supports the complete Create, Read, Update, & Delete (CRUD) lifecycle calls plus List, Query, and Cancel.


## Setup
 The easiest way to run this project is with [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/). If you don't have these softwares, download and install them first.

Then, all you have to do is clone this repo and invoke vagrant:

```shell
    $ git clone https://github.com/NYU-Devops-2020-Orders-Team/orders.git
    $ cd orders
    $ vagrant up
    $ vagrant ssh
    $ cd /vagrant
```

To run the Flask server, use
```shell
    $ FLASK_APP=service:app flask run -h 0.0.0.0
```

## Running the Tests and Pylint

You can run the tests using `nose`

```shell
    $ nosetests
```

Also, you can run Pylint as the following. Our current score is 9.87/10.
```shell
    $ pylint --rcfile=pylint.conf **/*.py
```


When you are done, you can exit and shut down the vm with:

```shell
    $ exit
    $ vagrant halt
```

If the VM is no longer needed you can remove it with:

```shell
    $ vagrant destroy
```

## What's featured in the project?

| Endpoint       |    Method  | Rule          |                      Description
|----------------|-------|-------------|     -------------------------
| index        |      GET    |  /          |                  
| create_orders | POST   |   /orders  |  Create an order based the data in the body that is posted  
| list_orders   |  GET     |  /orders            |             Return all of the Orders
| get_orders    | GET    |  /orders/<int:order_id>       |   Retrieve a single Order
|update_orders | PUT     | /orders/<int:order_id>      |   update an Order based the body that is posted
| update_order_items  | PUT | /orders/<int:order_id>/items/<int:item_id>  | Update an Order item based the body that is posted
| delete_orders   |   DELETE | /orders/<int:order_id>   |    Delete an Order based the id specified in the path
| cancel_orders  | PUT  |  /orders/<int:order_id>/cancel  |  Cancel all the items of the Order that have not being shipped yet
| cancel_item | PUT  | /orders/<int:order_id>/items/<int:item_id>/cancel | Cancel a single item in the Order that have not being shipped yet

## Contents

The project contains the following:

```text
.github/
└── ISSUE_TEMLATE.md    - github issue template

service/                - service python package
├── __init__.py         - package initializer
├── models.py           - module with business models
└── service.py          - module with service routes

tests/                  - test cases package
├── __init__.py         - package initializer
├── order_factory.py    - order factory
├── test_order_items.py - test suite for the order item model
├── test_orders.py      - test suite for the order model
└── test_service.py     - test suite for service routes

.coveragerc             - settings file for code coverage options
.dockerignore           - file that prevents files from being added to the initial build context in docker build
.gitignore              - file that specifies intentionally untracked files that Git should ignore
Dockerfile              - Docker file that contains all the commands a user could call on the command line to assemble an image
Vagrantfile             - Vagrant file that installs Python 3 and PostgreSQL
guincorn.conf.py        - configuration file for Gunicorn
config.py               - configuration parameters
requirements.txt        - file that lists if Python libraries required by your code
setup.cfg               - configuration file for the behavior of the various setup commands
```

## License
[Apache-2.0](https://github.com/NYU-Devops-2020-Orders-Team/orders/blob/master/LICENSE)