# Project 5 - testing

For grading purposes, the provided `_test.py` file is used. The test data is present in the `test_data` directory. New test cases were generated for grading, and are included in the `test_data` directory.

## Usage
In order to run these tests, make sure to install `pytest` and `pytest-timeout` using `pip`. Replace the current `test.py` in your Project 5 files directory, with the provided `_test.py`. Similarly, copy the `test_data` directory to your Project 5 files as well.

Run the test, using the command:
```bash
$ pytest _test.py
```

The tests were ran with a timeout of 1 second, so if your implementation was particularly slow, the tests will fail. There were a total of 78 tests, each carrying equal weightage.