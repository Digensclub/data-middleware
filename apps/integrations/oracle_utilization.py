import time
import math
import threading
import logging

# Setup basic logging to see it in your Docker logs
logger = logging.getLogger("oracle_utilization")

# 25% of 24GB is 6GB. 
# We'll use a list of large floats to occupy space.
DUMMY_RAM_HOLDER = []

def start_utilization_tasks():
    """Entry point to start the CPU and RAM maintenance."""


    # 1. RAM: ~666MB per worker (Total ~6GB for 9 workers)
    # 83 million floats is roughly 664MB in Python
    global DUMMY_RAM_HOLDER
    if not DUMMY_RAM_HOLDER:
        try:
            logger.info("Allocating RAM to meet Oracle 25% threshold...")
            DUMMY_RAM_HOLDER = [float(i) for i in range(40_000_000)]
            logger.info("RAM allocation ~660MB RAM.")
        except MemoryError:
            logger.error("Failed to allocate RAM. Insufficient memory.")

    # 2. Start CPU Stress Thread
    cpu_thread = threading.Thread(target=_maintain_cpu_load, daemon=True)
    cpu_thread.start()
    logger.info("CPU maintenance thread started (Target: 25% across 4 OCPUs).")

def _maintain_cpu_load():
    """
    Each worker works for 0.03s and sleeps for 0.97s.
    With 9 workers, this aggregates to ~27% total CPU load.
    """
    work_duration = 0.03 
    sleep_duration = 0.97
    
    while True:
        start_time = time.time()
        # Busy work
        while (time.time() - start_time) < work_duration:
            _ = math.sqrt(123456.789 * 987654.321)
        # Rest
        time.sleep(sleep_duration)
