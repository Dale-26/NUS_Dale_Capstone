import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
logger=logging.getLogger(__name__)
def plot_all(df,out):
    out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'figure.figsize':(9,5),'axes.spines.top':False,'axes.spines.right':False})
    def save(name,title,ylabel):
        plt.title(title);plt.ylabel(ylabel);plt.tight_layout();path=out/name;plt.savefig(path,dpi=160);plt.close();logger.info('Figure saved: %s',path)
    df.groupby(['hour','weekend']).traffic_volume.mean().unstack().rename(columns={0:'Weekday',1:'Weekend'}).plot(color=['#155e75','#d97706']);save('hourly.png','Traffic demand by hour and day type','Mean vehicles per observed hour')
    df.groupby('weather_main').traffic_volume.mean().sort_values().plot.barh(color='#155e75');save('weather.png','Traffic by selected hourly weather report','Weather')
    plt.scatter(df.temp_c,df.traffic_volume,s=3,alpha=.12,color='#155e75');plt.xlabel('Temperature (°C)');save('temperature.png','Temperature and traffic volume','Vehicles per observed hour')
    df.traffic_volume.plot.hist(bins=40,color='#155e75');plt.xlabel('Vehicles per observed hour');save('distribution.png','Distribution of observed hourly traffic','Hours')
