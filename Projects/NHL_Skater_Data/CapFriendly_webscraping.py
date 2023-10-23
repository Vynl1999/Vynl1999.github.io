# Setting up webscraper to grab the table where data is housed
from bs4 import BeautifulSoup
import requests

year = 2023
while year > 2008:
    url = 'https://www.capfriendly.com/browse/active/%s/salary?display=signing-team,birthday,weight,height,draft,caphit-percent,length,skater-individual-advanced-stats,skater-on-ice-advanced-stats,signing-age&hide=caphit,goalie-stats' % year
    rq = requests.get(url)
    soup = BeautifulSoup(rq.text, features='html.parser')

    col_names = soup.find_all('th')
    pd_columns = [ title.text for title in col_names ]
    print(pd_columns)

    # Setting up pandas dataframe to collect & organize the scraped data
    import pandas as pd

    df = pd.DataFrame(columns = pd_columns)
    df

    # Taking data from HTML table & inserting it into df
    column_data = soup.find_all('tr')
    for row in column_data[1:]:
        row_data = row.find_all('td')
        idv_row_data = [data.text for data in row_data]

        length = len(df)
        df.loc[length] = idv_row_data    
    print(df.head())
    print(len(df))

    # Setting up loop to collect player data from all each page of the table
    import re
    last_pg = str(soup.find_all('a', string='Last')).split()[3]
    pattern = r'"(.*?)"'
    loop_len = int(re.findall(pattern, last_pg)[0])-1
    print(loop_len)

    loops = 0
    pg = 2
    while (loops < loop_len):
        # URL changes after 1st page to track the depth into the table, allowing us to measurably increment and pull the entire table
        url = 'https://www.capfriendly.com/browse/active/%s/salary?stats-season=2023&display=signing-team,birthday,weight,height,draft,caphit-percent,length,skater-individual-advanced-stats,skater-on-ice-advanced-stats,signing-age&hide=caphit,goalie-stats&pg=%s' % (year,pg)
        rq = requests.get(url)
        soup = BeautifulSoup(rq.text, features='html.parser')

        column_data = soup.find_all('tr')

        for row in column_data[1:]:
            row_data = row.find_all('td')
            idv_row_data = [data.text for data in row_data]

            length = len(df)
            df.loc[length] = idv_row_data    

        pg = pg + 1
        loops = loops + 1
    print(df.head())
    print(len(df))

    # Removing Goalie Data for data cleaning
    df_no_goalies = df.loc[df['POS'] != 'G']

    # Correcting numeric attributes' dtypes
    to_numeric = ['WEIGHT','GP','G','A','P','+/-','Sh','SF','SA','CF','CA','FF','FA','iSh','iCF','iFF','SIGNING AGE','LENGTH','P/GP','Sh%','ixG','ixG60','iSh60','iCF60','iFF60','SF%','CF%','FF%','xGF','xGA','xGF%']
    df_no_goalies[to_numeric] = df_no_goalies[to_numeric].apply(pd.to_numeric)

    # Cases needing additional transformation
    ht_list = df_no_goalies['HEIGHT'].str.split("'")
    feet = ht_list.str[0].astype(int)
    inches = ht_list.str[1].str.replace('"', '').astype(int)
    total_in = (feet*12) + inches
    df_no_goalies['HEIGHT'] = total_in
    df_no_goalies.dtypes

    ts = df_no_goalies['TOI'].replace('','0:0').str.split(':')
    mn = ts.str[0].astype(int)
    sc = ts.str[1].astype(int)
    total_avg_sec = (mn*60) + sc
    df_no_goalies['TOI'] = total_avg_sec

    age = df_no_goalies['AGE'].str.extract(pat='(\d+)', expand=False).astype(int)
    df_no_goalies['AGE'] = age

    salary = df_no_goalies['SALARY'].str.replace('[^0-9]','').astype(int)
    df_no_goalies['SALARY'] = salary

    caph = df_no_goalies['CAP HIT %'].str.rstrip('%').astype(float)
    df_no_goalies['CAP HIT %'] = caph

    # Cleaning up the PlAYER attribute to show only player name
    df_no_goalies['PLAYER'] = df_no_goalies['PLAYER'].str.lstrip('1234567890. ')

    file_name = 'NHL_skaters_%s.csv' % year
    df_no_goalies.to_csv(file_name)

    print('%s Completed & exported' % year)
    year = year - 1
