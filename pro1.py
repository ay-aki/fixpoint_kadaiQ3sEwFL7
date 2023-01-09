# (c) A. YAMADA
# >> python pro1.py log4.txt


import sys
import csv
import datetime
import numpy as np  # not-built-in
import pandas as pd # not-built-in
import netaddr      # not-built-in




"""
# TYPE conversion foreach line # 
[ex]
# input  # l     : ["20201019133124", "10.20.30.1/16" ,"2"]
# output # result: [datetime.datetime(...), netaddr.IPNetwork(...), 2]
"""
def format_transform(l):
    t = l[0]
    Y,M,D,h,m,s = map(int, [t[0:4], t[4:6], t[6:8], t[8:10], t[10:12], t[12:14]])
    timesatmp = datetime.datetime(Y,M,D,h,m,s)
    ipaddress = l[1] # netaddr.IPNetwork(l[1])
    ack       = int(l[2]) if not l[2] == "-" else np.inf
    return [timesatmp, ipaddress, ack]


"""
# read log file & make pd.DataFrame(...) # 
[ex]
# input  # filename: "log0.txt"
# output # df      : dataframe of ["timestamp", "ipaddress", "response", "response_mean"]
"""
def read_logfile(filename):
    # read file
    with open(filename, "r") as fp:
        lines = (list(
                map(format_transform, csv.reader(fp)) # TYPE conversion
            )
        )
    # transform LIST to DATAFRAME
    df = pd.DataFrame(
        data = lines, 
        columns = ["timestamp", "ipaddress", "response"]
    )
    # mean of m results
    df["response_mean"] = df.loc[:, "response"] 
    return df


def foreach_ip(failure_list, df, ip):
    # for each ip address (this section can be parallelized)
    df_bool = df.loc[:, "ipaddress"] == ip
    df_ip   = df.loc[df_bool, :]

    flag_in_failure = False
    num_in_failure  = 0
    for row in df_ip.itertuples():
        if row.response == np.inf: 
            if flag_in_failure == False: 
                # to start
                ts_start = row.timestamp
                flag_in_failure = True
                num_in_failure  = 0
            num_in_failure += 1
        else:
            if flag_in_failure == True:
                # to end
                ts_end = row.timestamp
                ts_delta = ts_end - ts_start
                failure_list.append([ip, ts_start, ts_end, ts_delta, num_in_failure])
                flag_in_failure = False


"""
# main section #
"""
def main(argv):
    # error handling
    if not len(argv) == 1: exit(1)

    # options named
    filename, = argv

    df = read_logfile(filename)

    # ipaddresses
    l_ip_unique = df["ipaddress"].unique()

    # main process
    failure_list = [] # 故障状態を保存するリスト(現時点で故障しているものは扱わない)
    for ip in l_ip_unique:
        foreach_ip(failure_list, df, ip)
        
    # prorblem 1 故障状態(timeout)
    print("# 故障状態")
    print("総数: ", len([print("ipaddress: {0}, failure period: {1} ({2} ~ {3})".format(t[0], t[3], t[1], t[2])) for t in failure_list]))


main(sys.argv[1::])
