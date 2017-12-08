# MiniShogi Game

This project allows two people to play mini shogi via a command line interface. For more details on how to interact with the game, see the section on **Getting Started > Game Modes**. 

The project was written in `Python 3.5.3`.

## Getting Started

### Game Modes

Your program should accept command line flags to determine which mode to play in:

``` python myShogi.py -i ```
In interactive mode, two players enter keyboard commands to play moves against each other.

```python myShogi.py -f <filePath>```
In file mode, the specified file is read to determine the game state and which moves to make. File mode is how the game logic is tested in this project. You can see a list of the tests for this project [here](Tests/).

If you wish to see more detailed output as to what is happening behind the scenes, you can activate debug mode with a `-d` parameter. Specifying debug mode in the file game mode would look like this:

```python myShogi.py -d -f <filePath>```

### Testing

The [tests](Tests/) in the project validate the correctness of this implemnation of mini shogi. You may run the tests individually with the file mode command detailed below. In this case, ```<filepath>``` is the relative path to the single test case you wish to run.

Alternatively, `RunTestsWithDiff.sh` is bash script that will automatically run all tests and `diff` the output with the expected output. If you wish to run to `diff` the output of any single test case yourself, you can run the following command:

```python myShogi.py -f <path-to-testcase-input> | diff -u <path-to-testcase-output> -```


## Design
You can find specific design in the [src](src/) directory.

## Performance
There are a few computationally expensive functions, mainly involved with generating moves to escape check and checking whether or not a player is in checkmate. However, this fact does not necessarily affect the execution of the program too much because of the limited input size of variables and conditions of the game. For example, there are a max of **12 pieces** in the game, the board is a max size of `5x5`, and there can only be **400 moves** before the game ends in a tie. So, despite some expensive functions, the execution of the game isn't slowed down by too much.

## Error Handling
For most general errors that could occur such as an input file not existing, an error message will be printed to the screen but the execution of the game will end immediately instead of allowing unhandled exceptions to be printed in the console.

Errors such as an action other than `move` or `drop` or an invalid board position will result in the game ending as a result of an `INVALID MOVE`.