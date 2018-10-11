from pandas import*
from datetime import*
import matplotlib.pyplot as plt

#This function takes in the inputs:
#1) filename
#2) number of rows to skip
#and returns
#pandas dataframe

def skiprows(filename, rows):
    df=read_csv(filename,skiprows=range(rows),header=None)
    return df

#This function takes in the inputs:
#1) Dataframe with full columnns from csv
#2) List of columns to keep
#and returns
#pandas dataframe

def selectcolumns(df, clist):
    df2=df[clist] #Select just clist from df
    return df2

#This function takes in the inputs:
#1) string (s) in utc
#and returns
#string in akdt
def akdt(s):
    dt=datetime.strptime(s,'%Y%m%dT%H%M%SZ')
    dt2=dt-timedelta(hours=8)
    return dt2.strftime('%Y%m%dT%H%M%SZ')

#This function takes in the inputs:
#1) string (s) in utc
#and returns
#string in akdt
def akdt2(s):
    dt=datetime.strptime(s,'%d-%m-%Y %H:%M')
    dt2=dt-timedelta(hours=8)
    return dt2.strftime('%Y%m%dT%H%M%SZ')


#This function takes in the inputs:
#1) string in YYYYMMDDZHHMMSS
#and returns
#string in DOY.SSSSSS
def doy(s):
    currenttime=datetime.strptime(s, '%Y%m%dT%H%M%SZ')
    newyeartime=datetime.strptime(s[0:4]+'0101T000000Z', '%Y%m%dT%H%M%SZ')
    timedelta=currenttime-newyeartime
    days=timedelta.days
    seconds=timedelta.seconds
    #There are 86400 seconds in a day.
    return days+seconds/86400.0

flist= ['joe_2.csv']
masterdf=DataFrame()

for filename in flist:
    r=55
    df=skiprows(filename, r)
    clist=[0, 7, 8, 9, 20]
    df2=selectcolumns(df, clist)
    masterdf=masterdf.append(df2)
masterdf.index=range(len(masterdf)) #Reindex because we merged dataframes
masterdf['datetime_AKDT']=masterdf[0].apply(akdt)
masterdf['doy']=masterdf[0].apply(doy)

simpsondf=read_csv('simpson.csv')
#We will have to add a column called AMF in that and assign it a value 2.
simpsondf['AMF']=2.0
simpsondf['VCD']=(simpsondf['dSCD_HCHO_20']/simpsondf['AMF'])
#1 DU=2.69x10^16 mol/cm^-2
simpsondf['VCD']/=(2.69*10**16)
simpsondf['datetime_AKDT']=simpsondf['datetime_UTC'].apply(akdt2)
simpsondf['doy']=simpsondf['datetime_AKDT'].apply(doy)


#read conditions
conditions=read_csv('conditions.csv').fillna(0)
conditions['doy']=conditions['YYYYMMDDT000000Z'].apply(doy).apply(int)
conditions['Weather']=conditions['Clear']+conditions['Overcast']+conditions['Rainy']
conditions.index=conditions['doy']

masterdf['Weather']=0
for i in range(len(masterdf)):
    doy=int(masterdf['doy'][i])

    try:
        weather=conditions['Weather'][doy]
        masterdf.loc[i,'Weather']=weather
    except:
        masterdf.loc[i,'Weather']=3 #No data

gooddf=masterdf[masterdf[20]==0]
gooddf=gooddf[gooddf[7]>=0]
plt.scatter(gooddf['doy'][gooddf['Weather']==0],gooddf[7][gooddf['Weather']==0],color='r')
plt.scatter(gooddf['doy'][gooddf['Weather']==1],gooddf[7][gooddf['Weather']==1],color='g')
plt.scatter(gooddf['doy'][gooddf['Weather']==2],gooddf[7][gooddf['Weather']==2],color='b')
plt.scatter(gooddf['doy'][gooddf['Weather']==3],gooddf[7][gooddf['Weather']==3],color='y')
plt.show()

simpsondf['year']=simpsondf['datetime_AKDT'].apply(lambda x:x[0:4])
gooddf['year']=gooddf['datetime_AKDT'].apply(lambda x:x[0:4])


MAXDOASUAF=plt.scatter(simpsondf['doy'][simpsondf['VCD']>0],simpsondf['VCD'][simpsondf['VCD']>0],color='b')
PandoraUAF=plt.scatter(gooddf['doy'],gooddf[7],color='r')
plt.legend((MAXDOASUAF,PandoraUAF),('MAXDOASUAF','PandoraUAF'),scatterpoints=1,loc='upper right')
plt.title('VCD HCHO vs DOY')
plt.ylabel('Dobson Unit (DU)')
plt.xlabel('Day of Year (DOY)')
plt.show()

for year in ['2017','2018']:
    MAXDOASUAF=plt.scatter(simpsondf['doy'][(simpsondf['year']==year)],simpsondf['VCD'][(simpsondf['year']==year)],color='b')
    PandoraUAF=plt.scatter(gooddf['doy'][(gooddf['year']==year)],gooddf[7][(gooddf['year']==year)],color='r')
    plt.legend((MAXDOASUAF,PandoraUAF),('MAXDOASUAF','PandoraUAF'),scatterpoints=1,loc='upper right')
    plt.title('VCD HCHO vs DOY ({})'.format(year))
    plt.ylabel('Dobson Unit (DU)')
    plt.xlabel('Day of Year (DOY)')
    plt.show()
