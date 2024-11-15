import time

def elapsedTime():
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time  # Calculate elapsed time
        print(f"{elapsed_time:.2f}", end="\r")  # Print the time with 2 decimal places, overwrite the line
        time.sleep(0.1)  # Sleep for 0.1 seconds (100 milliseconds)

# Start the timer
elapsedTime()
