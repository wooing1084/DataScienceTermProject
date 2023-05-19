import pandas as pd
import numpy as np

# Define the file names and directory
inputDirs = ['2009', '2010', '2011', '2012', '2013', '2014',
             '2015', '2016', '2017', '2017_1', '2018', '2019']
fileNames = ['6시간강수량', '강수확률', '습도',
             '일최고기온', '일최저기온', '풍속', '풍향', '하늘상태']
fileNames_eng = ['rainfall', 'probability of precipitation', 'humidity', 'highest temperature', 'lowest temperature',
                 'wind speed', 'wind direction', 'sky state']

# Read the csv files in the assets/input and merge all of features


def mergeForecastDataset():
    for fileName in fileNames:
        allYears = pd.DataFrame()

        for dir in inputDirs:
            try:
                df = pd.read_csv('./assets/input/' + dir+'/부림동_' +
                                 fileName + '_'+dir+'.csv')
            except FileNotFoundError:
                print("Error: File not found!")
                continue
            except pd.errors.EmptyDataError:
                print("Error: File is empty")
                continue
            except Exception as e:
                print("Error:", str(e))
                continue
            print(df)
            df = df.loc[:,['timestamp', 'value']]
            allYears = pd.concat([df, allYears])
        allYears.set_index('timestamp', inplace=True)    
        allYears.to_csv("assets/output/부림동_" + fileName + ".csv")


# Visitor
def makeVisitor():
    years = ['2008', '2009', '2010', '2011', '2012', '2013', '2014',
         '2015', '2016', '2017', '2018', '2019', '2020']

    years.reverse()
    visitor = pd.DataFrame()
    for year in years:
        try:
            data = pd.read_csv(
                'assets/input/SGPyear/Visitor_'+year+'.csv', skiprows=2, usecols=[0, 5])
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
    visitor.set_index('date', inplace=True)
    visitor.to_csv("assets/output/visitors.csv")


def makeAtmosphere():
    years = ['2008' , '2009', '2010', '2011', '2012', '2013', '2014',
         '2015', '2016', '2017', '2018', '2019' ]
    years.reverse()
    atmosphere = pd.DataFrame()
    for year in years:
        try:
            if year == '2018' or year == '2019':
                data = pd.read_csv('assets/input/Atmosphere/Atmosphere_'+year+'.csv', encoding='cp949', usecols=range(1,12))
            else:
                data = pd.read_csv('assets/input/Atmosphere/Atmosphere_'+year+'.csv', encoding='cp949')
            data.columns = ['city', 'town', 'established', 'position', 'timestamp', 
                                'sulfur_dioxide', 'carbon_monoxide', 'ozone', 'nitrogen_dioxide', 
                                'fine_dust_pm10', 'fine_dust_pm2.5']
            df = pd.DataFrame(data)
            # Extract only data close to Seoul Grand Park
            df = df.loc[(df['city']=='Gwacheon') & (df['established']!=1991)]
            # Unnecessary data: "설치년도", "측정망 정보"   
            # Unavailable data (many missing data): "미세먼지PM2.5농도값(μg/m³)"
            df.drop(['established', 'position', 'fine_dust_pm2.5'], axis=1, inplace=True)
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

        atmosphere = pd.concat([df, atmosphere])
    
    group = atmosphere.groupby('date')
    days = atmosphere['date'].unique()
    
    sulfur_dioxide = getGroupDescribe(group['sulfur_dioxide'], 'sulfur_dioxide')
    carbon_monoxide = getGroupDescribe(group['carbon_monoxide'], 'carbon_monoxide')
    ozone = getGroupDescribe(group['ozone'], 'ozone')
    nitrogen_dioxide = getGroupDescribe(group['nitrogen_dioxide'], 'fine_dust_pm10')
    fine_dust_pm10 = getGroupDescribe(group['fine_dust_pm10'], 'fine_dust_pm10')
    
    result = pd.DataFrame({'date' : days})
    result = pd.concat([result, sulfur_dioxide,carbon_monoxide,ozone,nitrogen_dioxide,fine_dust_pm10], axis=1)
    result.reset_index(inplace=True, drop=True)
    result.set_index('date', inplace=True)
    result.to_csv("assets/output/atmosphere.csv", encoding='cp949')

def getGroupDescribe(group, name):
    min = group.min().values.ravel()
    max = group.max().values.ravel()
    mean = group.mean().values.ravel()
    median = group.median().values.ravel()
    std = group.std().values.ravel()
    
    result = pd.DataFrame({
            name+'_min': min,
            name+'_max': max,
            name+'_mean': mean,
            name+'_median': median,
            name+'_std': std
        })
    
    return result

def addOutputDataset():
    for i, file in enumerate(fileNames):
        df = pd.read_csv('./assets/output/부림동_'+file+'.csv')
        
        days = df['timestamp'].unique()
        
        name = fileNames_eng[i]
        group = getGroupDescribe(group=df.groupby('timestamp'), name=name)
        
        
        temp_df = pd.DataFrame({
            'timestamp': days,
        })
        
        temp_df = pd.concat([temp_df, group], axis=1)
        
        temp_df.set_index('timestamp', inplace=True)    
        temp_df.to_csv("assets/output/부림동_" + file + ".csv")

def makeFinalResult():
    result = pd.read_csv('./src/assets/output/atmosphere.csv')
    
    for file in fileNames:
        f = pd.read_csv('./src/assets/output/부림동_'+file+'.csv')
        f.rename(columns={'timestamp' : 'date'}, inplace=True)
        
        
        result = pd.merge(result, f, how='outer', on='date')
    
    week = pd.read_csv('./src/assets/input/WeekSet.csv')
    result = pd.merge(result, week, how='outer', on='date')
    target = pd.read_csv('./src/assets/output/visitors.csv')
    result = pd.merge(result, target, how='right', on='date')
    
    print(result)
    result.set_index('date', inplace=True)    
    result.to_csv("src/assets/output/finalDataset.csv")
makeFinalResult()
    