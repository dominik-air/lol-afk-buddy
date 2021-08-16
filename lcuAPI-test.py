import utillity.lcuapimaster.lcuapi.lcuapi as lcu# Create the LCU object. Make sure the client is open on your computer.

lcu = lcu.LCU()

# Optionally attach `EventProcessor` classes to handle incoming events. See usage.py
#lcu.attach_event_processor(...)

lcu.wait_for_client_to_open()
lcu.wait_for_login()

# Open a background thread and listen for & process incoming events
# using the EventProcessors that were attached to the LCU (not shown here, see usage.py).
lcu.process_event_stream()

# Here is an example request to get data from the LCU
finished = lcu.get('/lol-platform-config/v1/initial-configuration-complete')
print("Has the client finished it's starting up?", finished)

# ...  # Make more requests to the LCU if you want.

# Prevent this program from exiting so that the event stream continues to be read.
# Press Ctrl+C (and wait for another event to get triggered by the LCU) to gracefully terminate the program.
lcu.wait()