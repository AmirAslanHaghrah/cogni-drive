import time

from spara_sysmon.config import load_settings
from spara_sysmon.core.build_config import make_build_config
from spara_sysmon.logging import make_logger
from spara_sysmon.monitor.metrics import read_cpu_temp_c, read_cpu_percent, read_ram_usage
from spara_sysmon.hardware.status_led import StatusLed

def main() -> None:
    settings = load_settings()

    build_mode = str(settings.get("build_mode", "RELEASE"))
    build = make_build_config(build_mode, settings)

    logger = make_logger(
        name="spara_sysmon",
        min_level=build.min_log_level,
        log_to_console=build.log_to_console,
        log_to_file=bool(settings.get("log_to_file", True)),
        log_file=str(settings.get("log_file", "sysmon.log")),
    )

    sampling_interval = float(settings.get("sampling_interval_sec", 2.0))

    led = StatusLed(
        gpio_pin=int(settings.get("led_gpio_pin", 17)),
        blink_interval_sec=float(settings.get("led_blink_interval_sec", 0.5)),
    )
    led.start()

    logger.info("SysMon started | mode=%s | interval=%.2fs", build.mode.value, sampling_interval)

    try:
        while True:
            parts = []

            if build.enable_cpu_percent:
                cpu = read_cpu_percent(sample_window_sec=0.1)
                parts.append(f"CPU={cpu:5.1f}%")

            if build.enable_ram:
                ram = read_ram_usage()
                parts.append(f"RAM={ram['percent']:5.1f}% (used={ram['used_mb']:.0f}MB/total={ram['total_mb']:.0f}MB)")

            if build.enable_cpu_temp:
                temp = read_cpu_temp_c()
                if temp is not None:
                    parts.append(f"TEMP={temp:.1f}C")

            if parts:
                logger.info(" | ".join(parts))

            # DEBUG-only extra log (won't show in RELEASE)
            logger.debug("Loop OK")

            time.sleep(sampling_interval)

    except KeyboardInterrupt:
        logger.info("Stopped by user.")
    finally:
        led.stop()
