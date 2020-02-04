IoT-LAB monkey-tools
====================

IoT-LAB monkey-tools provide a basic set of loading tests for IoT-LAB REST API.

License
-------

IoT-LAB monkey-tools, including all examples, code snippets and attached
documentation is covered by the CeCILL v2.1 free software licence.

Install
-------

.. code-block::

    $ export VIRTUALENV_PYTHON=/usr/bin/python3
    $ pip install virtualenvwrapper
    $ mkvirtualenv iotlabmonkey
    $ pip install -e .

As we use IoT-LAB CLI-tools you can use ``~/.iotlab.api-url`` or
``IOTLAB_API_URL`` environment variable to specify which REST API url is used
by loading tests.


Command-line options
--------------------

Let’s run a test in console mode just once with –max-run

.. code-block::

    $ molotov --max-runs 1 -x iotlabmonkey.<module_test_name>

you can stop the test anytime with Ctrl+C.

Let’s try for 3 seconds now

.. code-block::

    $ molotov -d 3 -x iotlabmonkey.<module_test_name>

The next step is to add more workers with -w. A worker is a coroutine that
will run the scenario concurrently. Let’s run the same test with 10 workers
for a duration of ten seconds:

.. code-block::

    $ molotov -w 10 -d 10 -x iotlabmonkey.<module_test_name>

You can also run several processes in parallel, each one running its own set
of workers. Let’s try with 4 processes and 10 workers (concurrency = 40):

.. code-block::

    $ molotov -w 10 -p 4 -d 10 -x iotlabmonkey.<module_test_name>

When the –sizing option is used,  we will slowly ramp-up the number of workers
per process and will stop once there are too many failures per minute.
The default tolerance for failure is 5%, but this can be tweaked with
the –sizing-tolerance option.
We will use 500 workers that are getting ramped up in 5 minutes, but you can
set your own values with –workers and –ramp-up if you want to autosize at a
different pace.

.. code-block::

    $ molotov --sizing iotlabmonkey.<module_test_name>
