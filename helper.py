# Helper functions file. Contains functions to assist in data pipeline

import pandas as pd
import numpy as np

def generate_receipt_numbers(start_receipt_num, cnt):
        """Function to generate reciept numbers close to interested one"""
        loc, base = start_receipt_num[:4], int(start_receipt_num[4:])
        base = int(base - (cnt/2))
        receipt_numbers = []
        for idx in range(cnt):
            num = "{}{:d}".format(loc, base + idx)
            if len(num) > 13:
                break
            receipt_numbers.append(num)
        return receipt_numbers

def get_date(x):
    """Return Date from case description"""
    substr = x[:30].split()
    month = {'JANUARY':'01','FEBRUARY':'02','MARCH':'03',
             'APRIL':'04','MAY':'05','JUNE':'06','JULY':'07',
             'AUGUST':'08','SEPTEMBER':'09','OCTOBER':'10',
             'NOVEMBER':'11','DECEMBER':'12'}
    # Remove unwanted keywords
    try:
        substr.remove('As')
        substr.remove('of')
    except Exception as e:
        try:
            substr.remove('On')
        except Exception as e:
            pass
    try:
        return "-".join([month[substr[0].upper()],substr[1],substr[2]]).replace(',','')
    except:
        return 'NaN'

def get_form_type(x):
    """Return Form-Type from case description"""
    ind = x.find("I-")
    return x[ind:ind+5]

def get_rcpt_num(num):
    """Get Reciept Number from case description"""
    ind = num.find("Receipt")
    return num[ind+15:ind+28]

def transform_data(df):
    """Transform raw data to generate structured dataframe"""
    df["Date"] = df.Description.apply(get_date)
    df["Form-Type"] = df.Description.apply(get_form_type)
    df["RNS"] = df.Description.apply(get_rcpt_num)
    return df

def case_distribution(df,form_type):
    """Show Case Status Distribution for a given dataframe"""
    print(df["Form-Type"].count()," cases from ",pd.to_datetime(df.Date).min().date(), " to ", pd.to_datetime(df.Date).max().date())
    print("\nCase Status Distribution:\n",df[df["Form-Type"] == form_type]["Case_Status"].value_counts())

def save_df(df,filepath):
    """Save dataframe in csv form at a given filepath"""
    df.to_csv(filepath)

def active_cases(df):

    """Return a list of reciept number of active cases"""

    decision_made = df[(df['Case_Status'].str.contains('Card')) | df['Case_Status'].str.contains('Rejected') | 
    df['Case_Status'].str.contains('Approved') | df['Case_Status'].str.contains('Closed') |
    df['Case_Status'].str.contains('Denied')]["Reciept_Number"]

    # Active Cases: Receipt Numbers waiting for decision/ in process
    cases_to_follow = df[~df["Reciept_Number"].isin(decision_made)]["Reciept_Number"]

    return list(cases_to_follow)

def approved_cases(df):
    return df[(df['Case_Status'].str.contains('Card')) | df['Case_Status'].str.contains('Approved')][["Reciept_Number","Form-Type","Case_Status","Date"]]


def summary(df):
    """Returns DataFrame Summary by Case Status"""
    
    approved_count = df[(df['Case_Status'].str.contains('Card')) | df['Case_Status'].str.contains('Approved')][["Reciept_Number"]].count()[0]
    rejected_count = df[(df['Case_Status'].str.contains('Denied')) | df['Case_Status'].str.contains('Rejected')][["Reciept_Number"]].count()[0]
    rfe_sent_count = df[(df['Case_Status'].str.contains('Request for Initial Evidence Was Sent'))][["Reciept_Number"]].count()[0]
    rfe_recieved_count = df[(df['Case_Status'].str.contains('Request For Evidence Was Received'))][["Reciept_Number"]].count()[0]
    other_count = len(df.index) - (approved_count + rejected_count + rfe_sent_count + rfe_recieved_count)

    data = {"Case Status" : ["Approved","Rejected or Denied","RFE Sent","RFE Received","Other"],
            "Count": [approved_count, rejected_count,rfe_sent_count,rfe_recieved_count,other_count]}

    return pd.DataFrame(data)

# Function to track status change
def update_status_changes(main_df, recent_df):
    # Join New File with Main Data
    merged_df = pd.merge(main_df,recent_df,
                         on=["Reciept_Number","Form-Type"],
                         suffixes=('','_recent'),
                         how="left")

    # Get Cases where status was changed
    merged_df['Status Changed'] = np.where((
                                                    (pd.notna(merged_df['Case_Status_recent']))
                                                    &
                                                (merged_df['Case_Status'] != merged_df['Case_Status_recent']) 
                                                &
                                                (merged_df['Case_Status_new'] != merged_df['Case_Status_recent'])

                                            ) , 1, 0)

    # Replace Change Tracking Columns (Case_Status_new, Date_new)
    merged_df.loc[merged_df["Status Changed"] == 1, 'Case_Status_new'] = merged_df["Case_Status_recent"]
    merged_df.loc[merged_df["Status Changed"] == 1, 'Date_new'] = merged_df["Date_recent"]

    # Return results
    return merged_df[["Reciept_Number","Form-Type","Case_Status","Date",'Case_Status_new', "Date_new"]]



