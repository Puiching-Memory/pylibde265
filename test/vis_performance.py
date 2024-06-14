import matplotlib.pyplot as plt
from scipy.signal import savgol_filter  

fps_list = []
tps_list = []

with open('./cache/dec.txt') as file:
    data = file.readlines()
    for tps in data:
        tps = float(tps)
        fps = 1 / tps
        tps_list.append(tps)
        fps_list.append(fps)

print(sum(fps_list)/len(fps_list))

fps_all_list = []
tps_all_list = []

with open('./cache/all.txt') as file:
    data = file.readlines()
    for tps in data:
        tps = float(tps)
        fps = 1 / tps
        tps_all_list.append(tps)
        fps_all_list.append(fps)

print(sum(fps_all_list)/len(fps_all_list))

fps_after_list = []

with open('./cache/py.txt') as file:
    data = file.readlines()
    for index,tps in enumerate(data):
        tps = float(tps) + tps_all_list[index]
        fps = 1 / tps
        fps_after_list.append(fps)

print(sum(fps_after_list)/len(fps_after_list))

plt.plot(fps_list,label='libde265')
plt.plot(fps_all_list,label='pylibde265')
plt.plot(fps_after_list,label='after_effect')
plt.plot(savgol_filter(fps_list, window_length=501, polyorder=3),label='smooth-libde265')
plt.plot(savgol_filter(fps_all_list, window_length=501, polyorder=3),label='smooth-pylibde265')
plt.plot(savgol_filter(fps_after_list, window_length=501, polyorder=3),label='smooth-after_effect')
plt.title('Video decoding performance analysis(bbb-1280x720-cfg06)')  
plt.xlabel('Frame')  
plt.ylabel('FPS')  
plt.legend()  
plt.grid(True)  
plt.show()