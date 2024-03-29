import daemon
from gpiozero import Button
import json
import keyboard
import os
import os.path as path
import traceback
from typing import Dict


HOME_DIR = os.getenv("HOME")
CONFIG_LOCATION = path.join("usr", "local", "etc", "pico-raspberry.json")
DEBUG = True


class ControllerConfig:
    BUTTONS = [
        "left",
        "right",
        "up",
        "down",
        "primary",
        "secondary",
    ]

    DEFAULT_GPIO = {
        "left": 13,
        "right": 19,
        "up": 16,
        "down": 26,
        "primary": 20,
        "secondary": 21,
    }

    DEFAULT_PICO = {
        "left": "left",
        "right": "right",
        "up": "up",
        "down": "down",
        "primary": "z",
        "secondary": "x",
    }

    def __init__(self, gpio={}, pico={}):
        self.gpio = self.DEFAULT_GPIO
        self.pico = self.DEFAULT_PICO
        for button in self.BUTTONS:
            if button in gpio:
                self.gpio[button] = gpio[button]
            if button in pico:
                self.pico[button] = pico[button]

    @staticmethod
    def from_dict(config_dict: Dict) -> "ControllerConfig":
        """
        Builds a ControllerConfig from an unstructured Dict. Assumes the
        structure to be:

        {
            "gpio": {
                ...
            },
            "pico": {
                ...
            }
        }

        Where each (...) corresponds to the BUTTONS enumerated above.
        """
        return ControllerConfig(
            gpio=config_dict.get("gpio", {}), pico=config_dict.get("pico", {})
        )

    @staticmethod
    def from_json(path: str) -> "ControllerConfig":
        """
        Loads a ControllerConfig from a JSON file. See from_dict for its
        structure.
        """
        with open(path, "r") as f:
            return ControllerConfig.from_dict(json.load(f))


class ControllerButton:
    def __init__(self, gpio_button: int, pico_button: str):
        self.gpio_button = gpio_button
        self.pico_button = pico_button
        self.button = Button(gpio_button, pull_up=True)

        self.button.when_pressed = self.__make_button_callback(True)
        self.button.when_released = self.__make_button_callback(False)

    def __make_button_callback(self, pressed: bool):
        """
        Constructs a callback used to simulate input
        """
        def callback():
            if DEBUG:
                action = "pressed" if pressed else "released"
                print(
                    "Button {} {}, simulating '{}' {}".format(
                        self.gpio_button, action, self.pico_button, action
                    )
                )

            if pressed:
                keyboard.press(self.pico_button)
            else:
                keyboard.release(self.pico_button)

        return callback


class Controller:
    def __init__(self, config: ControllerConfig):
        self.buttons = {}
        for button in config.BUTTONS:
            self.buttons[button] = ControllerButton(
                config.gpio[button], config.pico[button]
            )


def main():
    # Configuring the controller
    conf = ControllerConfig()
    try:
        conf = ControllerConfig.from_json(CONFIG_LOCATION)
    except FileNotFoundError:
        print("'{}' not found, using default config instead".format(CONFIG_LOCATION))
    except json.JSONDecodeError:
        print("'{}' malformed, using default config instead".format(CONFIG_LOCATION))
    except Exception as e:
        print("Encountered an unexpected error:")
        traceback.print_exception(type(e), e, e.__traceback__)

    # Registering the controller
    controller = Controller(conf)

    # Waiting for button input
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
