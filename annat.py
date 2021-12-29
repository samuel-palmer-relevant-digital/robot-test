import microbit as mb
import music


def sätt_pixlar(hur_många):
    for n in range(25):
        mb.display.set_pixel(n % 5, n // 5, 9 if n < hur_många else 0)


# sätt_pixlar(kraschen.genomsnitt() // 20)
# sätt_pixlar(abs(mb.accelerometer.get_z()) // 40)
# sätt_pixlar((tiden // 100) % 26)

def test():
    analog_pins = [mb.pin1, mb.pin2]  # pin1 höger #pin2 vänster
    arrows = [mb.Image.ARROW_W, mb.Image.ARROW_E, mb.Image.HEART]
    mb.pin12.write_digital(1)
    # pin12.write_analog(0)
    idx = 2
    start = mb.running_time()
    while True:
        if mb.button_a.was_pressed():
            # idx = (idx + 1) % (len(analog_pins) + 1)
            idx = 2 if idx != 2 else 0
            start = mb.running_time()
        if idx < 2:
            idx = ((mb.running_time() - start) // 1000) % 2
            pin = analog_pins[idx]
            val = pin.read_analog()
            music.pitch(min(val * 10, 2000), 50)
            # display.scroll(": " + str(val))

        mb.display.show(arrows[idx])
        # display.scroll("hej")
