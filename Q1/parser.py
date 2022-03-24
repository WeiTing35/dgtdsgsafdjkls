import pandas as pd
import csv
import datetime
import argparse

def rate_limit(dataframe_ip_login, time_slot_end, time_delta: int, threshold: int, file, is_login_check: bool, ban_minutes: int):
    time_slot_start = time_slot_end - datetime.timedelta(minutes=time_delta)
    filtered_df = dataframe_ip_login.loc[time_slot_start:time_slot_end]

    if is_login_check:
        filtered_df = filtered_df[filtered_df['Login']==True]

    freq = filtered_df.groupby(['IP']).count() 
    
    time_stamp = int(time_slot_end.timestamp()) 
    writer = csv.writer(f)

    for row in freq.iterrows():
        if (row[1]['Login']) > threshold:
            writer.writerow([time_stamp, 'BAN', row[0], "Ban: " + str(ban_minutes) + " mins"])
            print(time_stamp, ',BAN,', row[0], "Ban:" + str(ban_minutes) + " mins")
        else:
            writer.writerow([time_stamp, 'UNBAN', row[0], ''])
            print(time_stamp, ',UNBAN,', row[0])


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='This program outputs instructions for the load balancer to ban offending IP addresses.')
    parser.add_argument('-o', '--output', required=True,  help='Folder for output CSV file')
    parser.add_argument('-l', '--log', required=True,  help='Raw lof file for processing')
    
    args = parser.parse_args()

    output_path = args.output
    log_file = args.log

    # Process dataframe as below
    #
    #                      |  IP	       | Login
    # Timestamp            |            
    # 2018-12-31 23:55:00  | 163.15.145.50 | True
    # 2018-12-31 23:55:00  | 134.44.70.43  | False
    # ...

    df = pd.read_csv(log_file,delimiter=' ',header = None)[[0, 3, 5]]

    df = df.rename(columns={0: 'IP', 3: 'Timestamp', 5: 'Login'})
    df.set_index('Timestamp')
    df['Timestamp']=pd.to_datetime(df['Timestamp'], format="[%d/%b/%Y:%H:%M:%S")
    df['Login']=df['Login'].str.contains("login")
    df.set_index('Timestamp', inplace = True)

    time_slot_end = df.index[0]

    # open the file in the write mode
    with open(output_path + '/'+ str(datetime.datetime.now().timestamp())+'.csv' , 'w', encoding='UTF8') as f:
        
        while time_slot_end < df.index[-1]:
            # More than 40 requests from one IP address, in the past 1 minute 
	        # IP address banned for the next 10 minutes 
            rate_limit(df, time_slot_end, 1, 40, f, False, 10)

            # More than 100 requests from one IP address, in the past 10 minutes 	
            # IP address banned for the next 1 hour				
            rate_limit(df, time_slot_end, 10, 100, f, False, 60)

            # More than 20 requests to /login from one IP address, in the past 10 minutes 			
            # IP address banned for the next 2 hours 
            rate_limit(df, time_slot_end, 10, 20, f, True, 120)

            time_slot_end = time_slot_end + datetime.timedelta(seconds=10)
