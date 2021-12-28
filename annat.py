from microbit import *
import music


def test():
    analog_pins = [pin1, pin2]  # pin1 höger #pin2 vänster
    arrows = [Image.ARROW_W, Image.ARROW_E, Image.HEART]
    pin12.write_digital(1)
    # pin12.write_analog(0)
    idx = 2
    start = running_time()
    while True:
        if button_a.was_pressed():
            # idx = (idx + 1) % (len(analog_pins) + 1)
            idx = 2 if idx != 2 else 0
            start = running_time()
        if idx < 2:
            idx = ((running_time() - start) // 1000) % 2
            pin = analog_pins[idx]
            val = pin.read_analog()
            music.pitch(min(val * 10, 2000), 50)
            # display.scroll(": " + str(val))

        display.show(arrows[idx])
        # display.scroll("hej")
