import time

# 1. Set the variable N = 1000
N = 1000

# Start the timer
start_time = time.perf_counter()

# 2. Run a simple loop for the baseline
for i in range(N):
    pass  # This just loops N times with no extra work

# End the timer
end_time = time.perf_counter()

# 3. Observe the output
duration = end_time - start_time
print(f"Loop of {N} iterations took: {duration:.6f} seconds")