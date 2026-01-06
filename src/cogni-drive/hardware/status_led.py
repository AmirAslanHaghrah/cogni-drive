from gpiozero import LED
from time import sleep
import threading

class StatusLed:
    """
    Blink a status LED in a background thread.
    """
    def __init__(self, gpio_pin: int, blink_interval_sec: float = 0.5):
        self.led = LED(gpio_pin)
        self.blink_interval = float(blink_interval_sec)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._stop.clear()
        if not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        try:
            self.led.off()
        except Exception:
            pass

    def _run(self) -> None:
        while not self._stop.is_set():
            self.led.on()
            sleep(self.blink_interval)
            self.led.off()
            sleep(self.blink_interval)
