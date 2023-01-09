# (c) A. YAMADA
# >> python pro2.py log4.txt 3



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
# output # result: [datetime.datetime(...), "10.20.30.1/16", 2]
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
                failure_list[ip] = ([ip, ts_start, ts_end, ts_delta, num_in_failure])
                flag_in_failure = False


def ip_analy(failure_list, failure_list2):
    ip_network = np.array([ip for ip in failure_list])
    network    = np.array([netaddr.IPNetwork(ip).network for ip in ip_network])
    network_unique = np.unique(network)
    for ipp in network_unique:
        ipps = ip_network[ipp == network]
        failure_list2[ipp] = failure_list[ipps[0]]
        for ip in ipps:
            print(failure_list2, netaddr.IPNetwork(ip))
            x = failure_list2[netaddr.IPNetwork(ip)]
            # x[1]とx[2]を比較して、failure_list2を編集する
            for p in failure_list:
                y = failure_list[p]
                if y[1] < x[1] < x[2] < y[2]:
                    x[1], x[2] = x[1], x[2]
                elif x[1] < y[1] < x[2] < y[2]:
                    x[1], x[2] = y[1], x[2]
                elif y[1] < x[1] < y[2] < x[2]:
                    x[1], x[2] = x[1], y[2]
                elif x[1] < y[1] < y[2] < x[2]:
                    x[1], x[2] = y[1], x[2]
                else:
                    failure_list2.pop(p)
    pass



"""
# main section #
"""
def main(argv):
    # error handling
    if not len(argv) == 2: exit(1)

    # options named
    filename,N = argv
    N = int(N)

    df = read_logfile(filename)

    # ipaddresses
    l_ip_unique = df["ipaddress"].unique()

    # main process
    failure_list = {} # 故障状態を保存するリスト(現時点で故障しているものは扱わない)
    for ip in l_ip_unique:
        foreach_ip(failure_list, df, ip)
    failure_list2 = {}
    ip_analy(failure_list, failure_list2)

    print(failure_list2)
    # print(failure_list)
    
        
    # problem 4 (problem 2)をベースに、ネットワークごとの故障状態を表示(only num_in_failure >= N)
    #print("総数:", len([print("ipaddress: {0}, failure period: {1} ({2} ~ {3})".format(t[0], t[3], t[1], t[2])) for t in failure_list if t[4] >= N]))


main(sys.argv[1::])
