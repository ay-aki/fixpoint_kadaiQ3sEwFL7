

import datetime
import numpy as np


# データ数
n = 1000
# ipアドレス種類
ip = [
    "10.20.30.1/16", 
    "10.20.30.2/16", 
    "192.168.1.1/24", 
    "192.168.1.2/24"
]


dt = np.random.poisson(2, n)
b  = np.random.randint(0, len(ip), n)
c  = [0] * n #np.random.poisson(5, n)
for i in range(n):
    r = np.random.rand()
    if   r < 0.05:
        c[i] = np.random.poisson(500)
    elif r < 0.35:
        c[i] = "-"
    else:
        c[i] = np.random.poisson(3)

t = t0 = datetime.datetime(2020,10,19,13,31,24)
for i in range(n):
    t = t + datetime.timedelta(seconds=int(dt[i])+1)
    print(
        datetime.datetime.strftime(t, '%Y%m%d%H%M%S'), 
        ip[b[i]], 
        c[i], 
        sep=","
    )


