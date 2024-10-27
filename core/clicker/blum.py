import asyncio
import random
from itertools import product

import keyboard
import pygetwindow as gw
from pynput.mouse import Button, Controller

from typing import Tuple, Any
from core.utils import Utilities
from main.static import WINDOW_NOT_FOUND


class BlumClicker:
    def __init__(self):
        self.mouse: Controller = Controller()
        self.utils = Utilities()

        self.paused: bool = True
        self.window_options: str | None = None

    async def click(self, x: int, y: int) -> None:
        """
        Click the mouse.

        :param x: the x coordinate
        :param y: the y coordinate
        :return: None
        """
        self.mouse.position = (x, y + random.randint(1, 3))
        self.mouse.press(Button.left)
        self.mouse.release(Button.left)

    async def handle_input(self) -> bool:
        """
        Handles the input.

        :return: whether the input was handled
        """
        if keyboard.is_pressed("s") and self.paused:
            self.paused = False
            await asyncio.sleep(0.2)

        elif keyboard.is_pressed("p"):
            self.paused = not self.paused
            await asyncio.sleep(0.2)

        return self.paused

    @staticmethod
    def activate_window(window: Any) -> None:
        """
        Activate the window.

        :param window: the window
        :return: None
        """
        if not window:
            return

        try:
            window.activate()
        except (Exception, ExceptionGroup):
            window.minimize()
            window.restore()

    async def click_on_found(
        self, screen: Any, rect: Tuple[int, int, int, int]
    ) -> bool:
        """
        Click on the found image.

        :param screen: the screenshot
        :param rect: the rectangle
        :return: whether the image was found
        """
        width, height = screen.size

        for x, y in product(range(0, width, 20), range(0, height, 20)):
            r, g, b = screen.getpixel((x, y))

            greenish_range = (b < 125) and (102 <= r < 220) and (200 <= g < 255)
            white_range = (r, g, b) == (255, 255, 255)  # Check for white pixels

            if greenish_range or white_range:
                screen_x = rect[0] + x
                screen_y = rect[1] + y
                await self.click(screen_x, screen_y)  # No offset for white pixels
                return True

        return False

    async def click_on_play_button(
        self, screen: Any, rect: Tuple[int, int, int, int]
    ) -> bool:
        """
        Click on the 'Play (nn left)' button if found.

        :param screen: the screenshot
        :param rect: the rectangle
        :return: whether the button was found and clicked
        """
        width, height = screen.size

        for x, y in product(range(0, width, 20), range(0, height, 20)):
            r, g, b = screen.getpixel((x, y))

            if (r, g, b) == (255, 255, 255):  # Assuming the button has white text
                screen_x = rect[0] + x
                screen_y = rect[1] + y
                await self.click(screen_x, screen_y)
                return True

        return False

    async def run(self) -> None:
        """Runs the clicker."""
        try:
            window = next(
                (
                    gw.getWindowsWithTitle(opt)
                    for opt in ["TelegramDesktop", "64Gram"]
                    if gw.getWindowsWithTitle(opt)
                ),
                None,
            )

            if not window:
                print(WINDOW_NOT_FOUND)
                return

            print("Initialized blum-clicker!")
            print(f"Found blum window: {window[0].title}")
            print("Press 's' to start the program.")

            rect = self.utils.get_rect(window[0])
            # Oříznutí o 1 cm (přibližně 37 pixelů)
            top_offset = 185
            bottom_offset = 74

            # Upravíme velikost obdélníku o 1 cm z horní a dolní části
            new_rect = (
                rect[0],
                rect[1] + top_offset,
                rect[2],
                rect[3] - top_offset - bottom_offset,
            )

            while True:
                if await self.handle_input():
                    continue

                self.activate_window(window[0])

                screenshot = self.utils.capture_screenshot(new_rect)

                tasks = []
                for _ in range(10):
                    tasks.append(self.click_on_found(screenshot, new_rect))

                await asyncio.gather(*tasks)
                await self.click_on_play_button(screenshot, new_rect)

        except gw.PyGetWindowException as error:
            print(f"The window might have been closed. Window error: {str(error)}.")