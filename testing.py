import threading
import time


def superman():
    for i in range(10):
        print("S - SUPERMAN, S Stands for HOPE")
        time.sleep(1)

def batman():
    for i in range(10):
        print("B - BATMAN, MEN are Brave")
        time.sleep(2)


t_list = [[threading.Thread(target=superman), superman], [threading.Thread(target=batman), batman]]
while True:
    for i in t_list:
        if not i[0].is_alive():
            try:
                i[0].join()
                i[0] = threading.Thread(target=i[1])
                i[0].start()
            except Exception as e:
                print(e)
            else:
                i[0] = threading.Thread(target=i[1])
                i[0].start()