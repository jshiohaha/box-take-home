# MiniShogi Game

This project allows two people to play mini shogi via a command line interface. For more details on how to interact with the game, see the section on **Getting Started > Game Modes**. 

The project was written in `Python 3.5.3`. There are no `pip` packages used, so you should be able to just run the project aftering cloning the repository. However, if you are attempting to run the program via Windows, you will most likely have to modify your `PYTHONPATH` to contain the path of this project. Otherwise, Windows will not recognize any of the classes as modules when some files try to import them.

## Getting Started

All of the example commands listed in this `README` assume that you are in the root directory of the project. If not, just update the commands to have the relative filepath to your current directory.

### Game Modes

In interactive mode, two players enter keyboard commands to play moves against each other. Interactive mode can be started with the following command:

```python src/myShogi.py -i```


In file mode, the specified file is read to determine the game state and which moves to make. File mode is how the game logic is tested in this project. You can see a list of the tests for this project [here](Tests/). File mode can be started with the following command:

```python src/myShogi.py -f Tests/<inputTestCaseName>```

If you wish to see more detailed output as to what is happening behind the scenes, you can activate debug mode with a `-d` parameter. Specifying debug mode in the interactive game mode would look like this:

```python src/myShogi.py -d -i```

It should be noted that if you run debug mode with file game mode and try to diff the output, it will not match the expected output of the testcase you are running. Specifying debug mode in the file game mode would look like this:

```python src/myShogi.py -d -f Tests/<inputTestCaseName>```

### Testing

The [tests](Tests/) in the project validate the correctness of this implementation of mini shogi. If you wish to run any single test case and `diff` the output, you can run the following command:

```python src/myShogi.py -f Tests/<inputTestCaseName> | diff -u Tests/<outputTestCaseName> -```

Alternatively, `RunTestsWithDiff.sh` is bash script that will automatically run all tests and `diff` the output with the expected output. You can expect to see output that looks like the following screenshot:

![RunTestsWithDiff Output](http://jacobshiohira.com/static/media/SampleRunTestsWithDiff.png)

## Design
You can find specific design in the [src](src/) directory.

## Performance
There are a few computationally expensive functions, mainly involved with generating moves to escape check and checking whether or not a player is in checkmate. However, this fact does not necessarily affect the execution of the program too much because of the limited input size of variables and conditions of the game. For example, there are a max of **12 pieces** in the game, the board is a max size of **5x5**, and there can only be **400 moves** before the game ends in a tie. So, despite some expensive functions, the execution of the game isn't slowed down by too much.

## Error Handling
For most general errors that could occur such as an input file not existing, an error message will be printed to the screen but the execution of the game will end immediately instead of allowing unhandled exceptions to be printed in the console.

Errors such as an action other than `move` or `drop` or an invalid board position will result in the game ending as a result of an `INVALID MOVE`.
