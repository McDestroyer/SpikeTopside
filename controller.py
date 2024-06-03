"""Provides an interface for a game controller."""

import pygame
from pygame.locals import *


# Zero deadband of controller
# Very high because white controller is very imprecise
JOY_DEADBAND = 0.15


def deadband(x, deadband):
    if abs(x) > deadband:
        return x
    return 0.0


class Controller:
    """An interface for a pygame controller"""

    def __init__(self):
        self.attempt_connect()

    def attempt_connect(self):
        try:
            self.joystick = pygame.joystick.Joystick(0)
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEREMOVED:
                self.enabled = False
            elif event.type == pygame.JOYDEVICEADDED:
                self.attempt_connect()

    def get_left(self):
        if not self.enabled:
            return 0, 0
        return (
            deadband(self.joystick.get_axis(0), JOY_DEADBAND),
            deadband(self.joystick.get_axis(1), JOY_DEADBAND),
        )

    def get_right(self):
        if not self.enabled:
            return 0, 0
        return (
            deadband(self.joystick.get_axis(2), JOY_DEADBAND),
            deadband(self.joystick.get_axis(3), JOY_DEADBAND),
        )

    def get_trigger_right(self):
        if not self.enabled:
            return 0
        return (self.joystick.get_axis(5) + 1) / 2

    def get_trigger_left(self):
        if not self.enabled:
            return 0
        return (self.joystick.get_axis(4) + 1) / 2

    def get_trigger(self):
        if not self.enabled:
            return 0
        return self.get_trigger_right() - self.get_trigger_left()

    def get_button(self, button):
        if not self.enabled:
            return 0
        return self.joystick.get_button(button)

    def get_a_button(self):
        return self.get_button(0)

    def get_b_button(self):
        return self.get_button(1)

    def get_x_button(self):
        return self.get_button(2)

    def get_y_button(self):
        return self.get_button(3)
