## Installation

```shell
$ git clone git@github.com:ambv/benchmark-annotations.git
$ cd benchmark-annotations
$ python3.10 -m venv /tmp/test
$ . /tmp/test/bin/activate  # or activate.fish, etc.
(test)$ poetry install
(test)$ python -m benchmark_annotations
*************** example_no_future ****************
.....................
Import time: 1.79s ±0.02s
RSS Memory usage: 143.62 MB
************** example_with_future ***************
.....................
Import time: 1.16s ±0.02s
RSS Memory usage: 93.29 MB
```