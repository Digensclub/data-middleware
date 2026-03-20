import time, math, threading, logging

# Setup basic logging to see it in your Docker logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("oracle_utilization")

# 25% of 24GB is 6GB. 
# We'll use a list of large floats to occupy space.
DUMMY_RAM_HOLDER = []
STOP_EVENT = threading.Event()
GLOBAL_CYCLE_TOTAL = 0
COUNTER_LOCK = threading.Lock()

def manage_utilization(active: bool, ram_count: int = 40_000_000):
    """Entry point to start the CPU and RAM maintenance."""
    # 1. RAM: ~666MB per worker (Total ~6GB for 9 workers)
    # 40 million floats is roughly 664MB in Python (since a float is 8 bytes, 40M * 8 = 320MB, but Python's overhead makes it larger)
    global DUMMY_RAM_HOLDER, GLOBAL_CYCLE_TOTAL
    
    try:
        if active:
            STOP_EVENT.clear()
            # Allocate RAM if empty
            if not DUMMY_RAM_HOLDER:
                try:
                    logger.info("Allocating RAM to meet Oracle 25% threshold...")
                    DUMMY_RAM_HOLDER = [float(i) for i in range(ram_count)]
                    logger.info(f"Allocated {ram_count} floats.")
                except MemoryError:
                    logger.error(f"Failed to allocate {ram_count} floats: Out of memory.")
                    DUMMY_RAM_HOLDER = [] # Ensure it stays empty on failure
            
            # Start CPU thread if not already running
            if not any(t.name == "OracleStressor" for t in threading.enumerate()):
                threading.Thread(target=_cpu_stress, daemon=True, name="OracleStressor").start()
                logger.info("CPU stress thread started.")
        else:
            # Stop CPU and Free RAM
            STOP_EVENT.set()
            DUMMY_RAM_HOLDER = []
            logger.info("Utilization stopped and RAM cleared.")
            
    except Exception as e:
        logger.error(f"Error managing utilization: {e}")

def _cpu_stress():
    """
    Each worker works for 0.03s and sleeps for 0.97s.
    With 9 workers, this aggregates to ~27% total CPU load.
    """
    global GLOBAL_CYCLE_TOTAL
    try:
        while not STOP_EVENT.is_set():
            logger.info("Starting CPU stress cycle.")
            start = time.time()
            # 3% duty cycle roughly
            while time.time() - start < 0.03:
                _ = math.sqrt(999.99)
            # Increment and release lock quickly
            with COUNTER_LOCK:
                GLOBAL_CYCLE_TOTAL += 1
                current_total = GLOBAL_CYCLE_TOTAL

                logger.info(f"Cycle finished. Global Total: {current_total}")

            time.sleep(0.97)
            logger.info("Completed CPU stress cycle, sleeping for 0.97s.")
    except Exception as e:
        logger.error(f"CPU stress thread encountered an error: {e}")

