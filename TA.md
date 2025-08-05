# Neuralk DevOps practical exercise

The exercise is meant to be quite open and serve as a starting point for
technical discussion and implementation. There is probably not enough time to
cover everything so feel free to focus on a subset of the tasks described below.

However the first section of the exercise,
["Preparing deployment"](#preparing-deployment) **is mandatory**.

## Introduction

This directory contains a toy application that is used similarly to the current
version of the Neuralk API. The user uploads a training dataset and triggers the
training of a model. Later, they upload a batch of new, unlabelled data and
trigger a prediction. Then they can download the results (the predicted labels).

We will use it to discuss some of the tasks involved in building and maintaining
the Neuralk platform:

- deployment: preparing the application to run on the cloud
- concurrency and scaling: making sure no task waits too long to be executed
- debugging, monitoring, inspection: helping both maintainers and users when
  something goes wrong
- security: preparing the application to process customer data

The goal of the exercise is to actually write code and configuration for a first
few simple tasks, and plan and discuss at a higher level the more advanced
topics.

You are asked to provide a link to a **private** github repository containing
the code and configuration that you wrote, as well as a short report describing
what you did and commenting on the discussion points below. This will serve as a
basis for discussion during the interview.

### Description of the toy example

The goal is to allow users to run the functions `fit` and `predict` defined in
`ml.py` on their data, through an API.

The current example relies on several parts:

- the web server in `server.py` handles requests from users
- data is stored in a MinIO store
- when a user needs to upload a dataset or download results, the server sends a
  presigned url
- when a user needs to launch a computation (`fit` or `predict`), the server
  enqueues it in a RQ queue (a task queue backed by Redis).
- a minimalistic Python client module is provided in `client.py` and can help
  using the API, as shown in `example_1.py` (perform a full workflow including
  `fit` and `predict`) and `example_2.py` (launch multiple fits at the same time).

Note: the software stack for this toy example is entirely different from the
actual Neuralk platform, only the overall workflow from the user's point of view
is vaguely similar.

You can tailor your approach by choosing which part of the exercise to explore:
feel free swap out the underlying tools, replace sections of the code, use a
different programming language etc. -- the existing boilerplate is only here to
help and there is no obligation to use it.

⚠️ The only constraint is that the `fit` and `predict` functions **must remain
basically unchanged** (you can add logging or error handling if needed but these
2 functions must still be written in Python and use a
`HistGradientBoostingClassifier` from scikit-learn, and operate on Parquet files).

### Installation & usage

You will need:

- To install Python and the dependencies:
  - you may want to use a virtual environment for example conda or:
    `python -m venv neuralk-exo && source neuralk-exo/bin/activate`
  - `pip install -r ./requirements.txt`
- To install [Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/) and start the service
- To install [MinIO](https://docs.min.io/community/minio-object-store/operations/deployments/installation.html) and start the service

Then, you can start the toy server with

```
python ./server.py
```

(You can change the port it listens on with the `-p` flag)

You can start an [RQ worker](https://python-rq.org/docs/workers/):

(If you are on MacOS, first **export this environment variable**:
`export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`)

```
rq worker -w worker.Worker
```

(the `-w worker.Worker` is optional but allows controlling how errors/retries
should be handled by editing `worker.py`. Alternatively see the
`--exception-handler` option).

Or multiple workers (for example 5) with

```
rq worker-pool -n 5 -w worker.Worker
```

To monitor the RQ workers you can use

```
rq info -i 1
```

or

```
rq-dashboard
```

You can now check that everything is working properly by running one of the
examples.

Generate example data with:

```
python make_data.py
```

This generates:

- `train.parquet`: a training dataset
- `test.parquet`: a test dataset for which we can get predictions once we have a
  trained model

And 2 files you can use to check the system's behavior on bad user data:

- `BAD_train.parquet`: a training dataset with an error (missing `y` column)
- `BAD_test.parquet`: a test dataset with an error (missing the first column)

You can now run:

```
python example_1.py
```

Fits one model and makes a prediction with it. You can control the training and
test data with `--train` and `--test`, for example this will fail at the "fit"
stage:

```
python example_1.py --train BAD_train.parquet
```

To launch multiple `fit` tasks at once:

```
python example_2.py
```

Note: you are free to not use any of this as long as the `fit` and `predict`
functions can still be used in a similar way.

## Exercise

### Preparing deployment

⚠️ **This section is not optional**

#### Context

Suppose the app will be deployed on one cloud (GCP), and possibly in the long
term several clouds or on customer's infrastructure.

#### Task

Add the necessary tooling so that the application can be easily launched. This
should include creating containers for the different components (the web server,
Redis, Minio and the workers), and configuring an orchestration layer to start,
manage and monitor those containers.

In practice for the exercise we will run it on a single machine, but the tooling
should be a first step toward easily deploying it on a cloud like GCP.

#### Discussion

CI/CD: how would you make it easy and reliable to deploy new versions of the
application? Describe the mechanisms you would put in place to go from a change
to the application's code to making it available to users (e.g. running tests,
deploying in a staging environment, deploying in production).

Portability: how would you take into account the future need to deploy on a
different (possibly multiple) infrastructure?

### Managing the work load

#### Context

We want to handle tasks efficiently. Typical jobs last from a few minutes to a
few hours. Users may also experiment with toy datasets or launch erroneous jobs
which may complete or fail in a few seconds.

- We need to scale resources according to the work load
- Other strategies may include: enforcing limits, assigning priorities based on
  estimated job duration (eg dataset size), failing early, caching and
  deduplicating data and results, offering user-facing controls to prevent or
  stop unneeded tasks, ...

#### Task

Select one or more of the aspects above and write the necessary code and
configuration to make the application more efficient in that regard.

#### Discussion

Describe in a more comprehensive way how you would approach the problem of making
the system fast and efficient. In particular, provide details on the auto
scaling (which technologies to use etc.), and the data transfers both between
the user and the application, and within the application itself.

In the real platform, the tasks are composed of several steps: preprocessing the
data which only uses CPUs, and using the pre-trained model which needs a large
GPU. How would you separate those parts to ensure the GPU is used efficiently,
and how would you transfer data between the different workers?

### Debugging and monitoring

#### Context

We need to provide clear, actionable feedback to users, especially in failure
cases and for long-running jobs.

#### Task

Add the possibility to report some errors to users in a way that helps them fix
the issue if it is on their side.

#### Discussion

What would you put in place to make the system more transparent, allowing admins
and users to understand what tasks are running, which succeeded or failed and
why, where delays come from, etc. ?
