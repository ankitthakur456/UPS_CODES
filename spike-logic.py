import time

data = [10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,100,101,102,103,70,71,72,73,74,75,76,77,78,79,80,81,
        82,83,84,85,86,87,88,89,150,151,152,100,101,102,103,104,105,106,107,108,109]

spike_threshold = 10
last_param_value = 0
FL_SPIKE = False
FL_PREV_SPIKE = False
spike_hold_duration = 3


for current_param in data:
    if current_param > last_param_value:
        if (current_param - last_param_value) > spike_threshold:
            FL_SPIKE = True:

    if FL_SPIKE != FL_PREV_SPIKE:
        spike_start_dur = time.time()

    if FL_SPIKE:
        
