import st3m.run, random

from st3m.application import Application, ApplicationContext
from st3m.input import InputState
from ctx import Context

import leds
import json


class Diashow(Application):
    def __init__(self, app_ctx: ApplicationContext) -> None:
        super().__init__(app_ctx)
        self._timeout = 0
        self._index = 0
        self._led_index = 0
        self._timeout = 0
        self._change_time = 10000
        with open("/flash/sys/apps/diashow/images.json", "r") as file:
            content = file.read()
            self._images = json.loads(content)

    def think(self, ins: InputState, delta_ms: int) -> None:
        self._timeout += delta_ms
        if self._timeout >= self._change_time:
            self._index = self._index + 1
            self._timeout = 0
            self._led_index = 0
            if self._index >= len(self._images):
                self._index = 0
        if self._timeout > (self._led_index + 1) * (self._change_time / 40):
            self._led_index = self._led_index + 1

    def draw(self, ctx: Context) -> None:
        # Show logo
        image = self._images[self._index]
        ctx.image_smoothing = False
        ctx.rectangle(-120, -120, 240, 240)
        background_color = self.hex_to_rgb(image["backgroundColor"])
        ctx.rgb(background_color[0], background_color[1], background_color[2])
        ctx.fill()
        ctx.image(
            "/flash/sys/apps/diashow/images/" + image["fileName"],
            -120, -(image["ySize"] / 2), 240, image["ySize"]
        )
        # # Make leds colored
        color = self.hex_to_rgb(image["color"])
        comp_color = self.complement(color[0], color[1], color[2])
        leds.set_all_rgb(color[0], color[1], color[2])

        if self._led_index == 0:
            leds.set_rgb(39, comp_color[0], comp_color[1], comp_color[2])
            leds.set_rgb(1, comp_color[0], comp_color[1], comp_color[2])
        elif self._led_index == 39:
            leds.set_rgb(38, comp_color[0], comp_color[1], comp_color[2])
            leds.set_rgb(0, comp_color[0], comp_color[1], comp_color[2])
        else:
            leds.set_rgb(self._led_index-1, comp_color[0], comp_color[1], comp_color[2])
            leds.set_rgb(self._led_index, comp_color[0], comp_color[1], comp_color[2])
            leds.set_rgb(self._led_index+1, comp_color[0], comp_color[1], comp_color[2])
        leds.update()

    def hex_to_rgb(self, hex):
        h = hex.lstrip('#')
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    # Sum of the min & max of (a, b, c)
    def hilo(self, a, b, c):
        if c < b: b, c = c, b
        if b < a: a, b = b, a
        if c < b: b, c = c, b
        return a + c

    def complement(self, r, g, b):
        k = self.hilo(r, g, b)
        if(r == 255 and g == 255 and b == 255):
            return (255, 0, 0)
        return tuple(k - u for u in (r, g, b))
