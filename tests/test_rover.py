import pytest

from rover import Plateau, Rover, RoverInputError, parse_plateau, parse_rover_position, run


def test_turn_left():
    rover = Rover(1, 2, "N")
    rover.turn_left()
    assert rover.position() == "1 2 W"


def test_turn_right():
    rover = Rover(1, 2, "N")
    rover.turn_right()
    assert rover.position() == "1 2 E"


def test_move_north():
    rover = Rover(1, 2, "N")
    rover.move(Plateau(5, 5))
    assert rover.position() == "1 3 N"


def test_move_respects_boundary():
    rover = Rover(5, 5, "N")
    with pytest.raises(RoverInputError):
        rover.move(Plateau(5, 5))


def test_invalid_command():
    rover = Rover(1, 2, "N")
    with pytest.raises(RoverInputError):
        rover.execute("MX", Plateau(5, 5))


def test_invalid_direction():
    with pytest.raises(RoverInputError):
        parse_rover_position("1 2 X", Plateau(5, 5))


def test_reference_input(tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text(
        "5 5\n1 2 N\nLMLMLMLMM\n3 3 E\nMMRMMRMRRM\n",
        encoding="utf-8",
    )
    assert run(str(input_file)) == ["1 3 N", "5 1 E"]


def test_invalid_plateau():
    with pytest.raises(RoverInputError):
        parse_plateau("5")


def test_starting_position_outside_plateau():
    with pytest.raises(RoverInputError):
        parse_rover_position("6 1 N", Plateau(5, 5))


def test_missing_rover_command(tmp_path):
    input_file = tmp_path / "bad.txt"
    input_file.write_text("5 5\n1 2 N\n", encoding="utf-8")
    with pytest.raises(RoverInputError):
        run(str(input_file))
