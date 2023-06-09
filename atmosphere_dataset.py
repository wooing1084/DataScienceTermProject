import pandas as pd
import numpy as np

years = ['2008', '2009', '2010', '2011', '2012', '2013', '2014',
         '2015', '2016', '2017', '2018', '2019', '2020']

years.reverse()
visitor = pd.DataFrame()
for year in years:
    try:
        data = pd.read_excel(
            './src/assets/SGPyear/Visitor_'+year+'.xlsx', skiprows=2, usecols=[0, 5])
    except FileNotFoundError:
        print("Error: File not found!")
        continue
    except pd.errors.EmptyDataError:
        print("Error: File is empty")
        continue
    except Exception as e:
        print("Error:", str(e))
        continue
    data.columns = ['date', 'visitor']
    visitor = pd.concat([data, visitor])
visitor.reset_index(inplace=True, drop=True)
visitor.to_csv("./src/assets/output/visitors.csv")

years = ['2008', '2009', '2010', '2011', '2012', '2013', '2014',
            '2015', '2016', '2017', '2018', '2019']
# Atmosphere
years.reverse()
atmosphere = pd.DataFrame()
for year in years:
    try:
        data = pd.read_csv(
            './src/assets/Atmosphere/Atmosphere_'+year+'.csv', encoding='cp949')
        data.columns = ['city', 'town', 'established', 'position', 'timestamp', 
                        'sulfur_dioxide', 'carbon monoxide', 'ozone', 'nitrogen_dioxide', 
                        'fine_dust_pm10', 'fine_dust_pm2.5']
        df = pd.DataFrame(data)
        # Unnecessary data: "설치년도", "측정망 정보"   
        # Unavailable data (many missing data): "미세먼지PM2.5농도값(μg/m³)"
        df.drop(['established', 'position', 'fine_dust_pm2.5'], axis=1, inplace=True)
        # Extract only data close to Seoul Grand Park
        df = df.loc[(df['city']=="과천시") & (df['town']=="과천동")]
        # Unnecessary data (because all data values are same): "시군명", "측정소명"
        df.drop(['city', 'town'], axis=1, inplace=True)
        # Split the data with Date/Time
        df[['date', 'hour']] = df['timestamp'].str.split(" ", 1, expand=True)
        df.drop(['timestamp'], axis=1, inplace=True)
    except FileNotFoundError:
        print("Error: File not found!")
        continue
    except pd.errors.EmptyDataError:
        print("Error: File is empty")
        continue
    except Exception as e:
        print("Error:", str(e))
        continue

    atmosphere = pd.concat([data, atmosphere])
atmosphere.reset_index(inplace=True, drop=True)
atmosphere.to_csv("./src/assets/output/atmosphere.csv", encoding='cp949')