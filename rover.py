#!/usr/bin/env python3
from __future__ import annotations

import sys
from dataclasses import dataclass

DIRECTIONS = ("N", "E", "S", "W")
MOVES = {"N": (0, 1), "E": (1, 0), "S": (0, -1), "W": (-1, 0)}


class RoverInputError(ValueError):
    pass


@dataclass
class Plateau:
    max_x: int
    max_y: int

    def validate_position(self, x: int, y: int) -> None:
        if not (0 <= x <= self.max_x and 0 <= y <= self.max_y):
            raise RoverInputError(
                f"Position ({x}, {y}) is outside plateau 0 0 {self.max_x} {self.max_y}"
            )


@dataclass
class Rover:
    x: int
    y: int
    heading: str

    def turn_left(self) -> None:
        self.heading = DIRECTIONS[(DIRECTIONS.index(self.heading) - 1) % 4]

    def turn_right(self) -> None:
        self.heading = DIRECTIONS[(DIRECTIONS.index(self.heading) + 1) % 4]

    def move(self, plateau: Plateau) -> None:
        dx, dy = MOVES[self.heading]
        new_x, new_y = self.x + dx, self.y + dy
        plateau.validate_position(new_x, new_y)
        self.x, self.y = new_x, new_y

    def execute(self, commands: str, plateau: Plateau) -> None:
        for command in commands:
            if command == "L":
                self.turn_left()
            elif command == "R":
                self.turn_right()
            elif command == "M":
                self.move(plateau)
            else:
                raise RoverInputError(f"Invalid command: {command!r}")

    def position(self) -> str:
        return f"{self.x} {self.y} {self.heading}"


def parse_plateau(line: str) -> Plateau:
    parts = line.split()
    if len(parts) != 2:
        raise RoverInputError("Plateau line must contain exactly two integers")
    try:
        max_x, max_y = map(int, parts)
    except ValueError as exc:
        raise RoverInputError("Plateau coordinates must be integers") from exc
    if max_x < 0 or max_y < 0:
        raise RoverInputError("Plateau coordinates cannot be negative")
    return Plateau(max_x, max_y)


def parse_rover_position(line: str, plateau: Plateau) -> Rover:
    parts = line.split()
    if len(parts) != 3:
        raise RoverInputError("Rover position must be: x y direction")
    try:
        x, y = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise RoverInputError("Rover coordinates must be integers") from exc
    heading = parts[2].upper()
    if heading not in DIRECTIONS:
        raise RoverInputError("Direction must be one of N, E, S, W")
    plateau.validate_position(x, y)
    return Rover(x, y, heading)


def read_input(path: str) -> tuple[Plateau, list[tuple[Rover, str]]]:
    with open(path, encoding="utf-8") as handle:
        lines = [line.strip() for line in handle if line.strip()]
    if not lines:
        raise RoverInputError("Input file is empty")

    plateau = parse_plateau(lines[0])
    if (len(lines) - 1) % 2 != 0:
        raise RoverInputError("Each rover must have a position line and command line")

    rovers = []
    for index in range(1, len(lines), 2):
        rover = parse_rover_position(lines[index], plateau)
        commands = lines[index + 1].upper()
        if any(command not in {"L", "R", "M"} for command in commands):
            raise RoverInputError("Commands may contain only L, R and M")
        rovers.append((rover, commands))
    return plateau, rovers


def run(path: str) -> list[str]:
    plateau, rovers = read_input(path)
    outputs = []
    for rover, commands in rovers:
        rover.execute(commands, plateau)
        outputs.append(rover.position())
    return outputs


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python rover.py input.txt", file=sys.stderr)
        return 2
    try:
        for output in run(sys.argv[1]):
            print(output)
        return 0
    except (OSError, RoverInputError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
