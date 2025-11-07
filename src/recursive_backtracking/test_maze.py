import pytest
from maze import Maze


def test_size_maze():
    expected_width = 19
    expected_height = 39

    maze = Maze(expected_width, expected_height, 10, 3, 5)
    maze.generate_maze()

    # On vérifie les attributs de la classe
    assert maze.height == expected_height
    assert maze.width == expected_width

    # On vérifie la taille réelle du dictionnaire maze.maze
    assert len(maze.maze) == expected_width * expected_height
