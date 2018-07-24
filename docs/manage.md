# Patterns
This document outlines some of the patterns used by hello_world

## Manage.py
The `manage.py` file is a simple interface that allows developers to interact with portions of their applications without running the associated service.

Behind the scenes, commands behind the `manage.py` interface create a real instance of the application, and run inside of its context

Example:
```bash
jwoodward@ALT00424 test_app (master) $ docker-compose run devbox
[root@test_app] app # python manage.py print_hello_world
Hello World called from test_app
```

In the above example, the `print_hello_world` entrypoint lives in `manage.py`, and relies on the `print_hello_world` command in `hello_world/commands/examples` to perform the action

You could feasibly put anything you would like into the `manage.py` interface. Some other examples of commands are:

* [Warm Tensorflow Models](https://git.csnzoo.com/wayfair/honeycomb/blob/master/manage.py#L20)
* [Bootstrap Local Database](https://git.csnzoo.com/wayfair/waybot_service/blob/master/manage.py#L37)
* [Delete Old Spider Jobs](https://git.csnzoo.com/wayfair/waybot_service/blob/master/manage.py#L28)
