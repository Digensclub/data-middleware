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
    
    # 1. Occupy ~6GB of RAM
    # A list of 750,000,000 floats/ints is roughly 6GB in Python
    global DUMMY_RAM_HOLDER
    if not DUMMY_RAM_HOLDER:
        logger.info("Allocating ~6GB RAM to meet Oracle 25% threshold...")
        DUMMY_RAM_HOLDER = [float(i) for i in range(750_000_000)]
        logger.info("RAM allocation complete.")

    # 2. Start CPU Stress Thread
    cpu_thread = threading.Thread(target=_maintain_cpu_load, daemon=True)
    cpu_thread.start()
    logger.info("CPU maintenance thread started (Target: 25% across 4 OCPUs).")

def _maintain_cpu_load():
    """Targeting ~25% load by working for 0.25s and sleeping for 0.75s."""
    target_load = 0.25
    while True:
        start_time = time.time()
        # Busy work
        while time.time() - start_time < target_load:
            _ = math.sqrt(999999.99 * 888888.88)
        # Rest
        time.sleep(1.0 - target_load)
