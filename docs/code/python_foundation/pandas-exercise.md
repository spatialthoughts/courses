```python
import os
import pandas as pd
```


```python
home_dir = os.path.expanduser('~')
print(home_dir)
```

    /Users/ujaval



```python
filename = 'cities5000.txt'
folder = 'Downloads/python_geospatial/'
path = os.path.join(home_dir, folder, filename)
print(path)
```

    /Users/ujaval/Downloads/python_geospatial/cities5000.txt



```python
column_names = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature class', 'feature code', 'country code', 'cc2', 'admin1 code', 'admin2 code', 'admin3 code', 'admin4 code', 'population', 'elevation', 'dem', 'timezone', 'modification date']
df = pd.read_csv(path, sep='\t', names=column_names)
df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>geonameid</th>
      <th>name</th>
      <th>asciiname</th>
      <th>alternatenames</th>
      <th>latitude</th>
      <th>longitude</th>
      <th>feature class</th>
      <th>feature code</th>
      <th>country code</th>
      <th>cc2</th>
      <th>admin1 code</th>
      <th>admin2 code</th>
      <th>admin3 code</th>
      <th>admin4 code</th>
      <th>population</th>
      <th>elevation</th>
      <th>dem</th>
      <th>timezone</th>
      <th>modification date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>3039163</td>
      <td>Sant Julià de Lòria</td>
      <td>Sant Julia de Loria</td>
      <td>San Julia,San Julià,Sant Julia de Loria,Sant J...</td>
      <td>42.46372</td>
      <td>1.49129</td>
      <td>P</td>
      <td>PPLA</td>
      <td>AD</td>
      <td>NaN</td>
      <td>06</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>8022</td>
      <td>NaN</td>
      <td>921</td>
      <td>Europe/Andorra</td>
      <td>2013-11-23</td>
    </tr>
    <tr>
      <th>1</th>
      <td>3039678</td>
      <td>Ordino</td>
      <td>Ordino</td>
      <td>Ordino,ao er di nuo,orudino jiao qu,Ордино,オルデ...</td>
      <td>42.55623</td>
      <td>1.53319</td>
      <td>P</td>
      <td>PPLA</td>
      <td>AD</td>
      <td>NaN</td>
      <td>05</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>3066</td>
      <td>NaN</td>
      <td>1296</td>
      <td>Europe/Andorra</td>
      <td>2018-10-26</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3040051</td>
      <td>les Escaldes</td>
      <td>les Escaldes</td>
      <td>Ehskal'des-Ehndzhordani,Escaldes,Escaldes-Engo...</td>
      <td>42.50729</td>
      <td>1.53414</td>
      <td>P</td>
      <td>PPLA</td>
      <td>AD</td>
      <td>NaN</td>
      <td>08</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>15853</td>
      <td>NaN</td>
      <td>1033</td>
      <td>Europe/Andorra</td>
      <td>2008-10-15</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3040132</td>
      <td>la Massana</td>
      <td>la Massana</td>
      <td>La Macana,La Massana,La Maçana,La-Massana,la M...</td>
      <td>42.54499</td>
      <td>1.51483</td>
      <td>P</td>
      <td>PPLA</td>
      <td>AD</td>
      <td>NaN</td>
      <td>04</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>7211</td>
      <td>NaN</td>
      <td>1245</td>
      <td>Europe/Andorra</td>
      <td>2008-10-15</td>
    </tr>
    <tr>
      <th>4</th>
      <td>3040686</td>
      <td>Encamp</td>
      <td>Encamp</td>
      <td>Ehnkam,Encamp,en kan pu,enkanpu jiao qu,Энкам,...</td>
      <td>42.53474</td>
      <td>1.58014</td>
      <td>P</td>
      <td>PPLA</td>
      <td>AD</td>
      <td>NaN</td>
      <td>03</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>11223</td>
      <td>NaN</td>
      <td>1257</td>
      <td>Europe/Andorra</td>
      <td>2018-10-26</td>
    </tr>
  </tbody>
</table>
</div>




```python
df.shape
```




    (50118, 19)




```python
country = 'IN'
india_df = df[(df['country code']==country) & (df['population'] > 1000000)].copy()
india_df.shape
```




    (41, 19)




```python

```


```python
%run ./distance.ipynb
```


```python
india_df['distance'] = india_df.apply(lambda row: haversine_distance((77.56, 12.97), (row['longitude'], row['latitude'])), axis=1)
india_df['distance'] = india_df['distance'].apply(lambda x: '%.2f' % x)
display(india_df)

```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>geonameid</th>
      <th>name</th>
      <th>asciiname</th>
      <th>alternatenames</th>
      <th>latitude</th>
      <th>longitude</th>
      <th>feature class</th>
      <th>feature code</th>
      <th>country code</th>
      <th>cc2</th>
      <th>admin1 code</th>
      <th>admin2 code</th>
      <th>admin3 code</th>
      <th>admin4 code</th>
      <th>population</th>
      <th>elevation</th>
      <th>dem</th>
      <th>timezone</th>
      <th>modification date</th>
      <th>distance</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>19928</th>
      <td>1253102</td>
      <td>Visakhapatnam</td>
      <td>Visakhapatnam</td>
      <td>VTZ,Vaisakhapattanam,Vaisākhapattanam,Visak,Vi...</td>
      <td>17.68009</td>
      <td>83.20161</td>
      <td>P</td>
      <td>PPLA2</td>
      <td>IN</td>
      <td>NaN</td>
      <td>02</td>
      <td>544</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1063178</td>
      <td>NaN</td>
      <td>24</td>
      <td>Asia/Kolkata</td>
      <td>2019-09-05</td>
      <td>632.87</td>
    </tr>
    <tr>
      <th>19971</th>
      <td>1253405</td>
      <td>Varanasi</td>
      <td>Varanasi</td>
      <td>Banaras,Banares,Banāras,Benares,Benarés,Kashi,...</td>
      <td>25.31668</td>
      <td>83.01041</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>36</td>
      <td>197</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1164404</td>
      <td>NaN</td>
      <td>86</td>
      <td>Asia/Kolkata</td>
      <td>2019-05-07</td>
      <td>645.45</td>
    </tr>
    <tr>
      <th>19988</th>
      <td>1253573</td>
      <td>Vadodara</td>
      <td>Vadodara</td>
      <td>BDQ,Baroda,Vadodara,Vapadedara,ba luo da,badod...</td>
      <td>22.29941</td>
      <td>73.20812</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>09</td>
      <td>486</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1409476</td>
      <td>NaN</td>
      <td>46</td>
      <td>Asia/Kolkata</td>
      <td>2014-10-13</td>
      <td>548.69</td>
    </tr>
    <tr>
      <th>20089</th>
      <td>1254361</td>
      <td>Tirunelveli</td>
      <td>Tirunelveli</td>
      <td>Nellai,Tinnevelli,Tinnevelly,Tinnevelly Juncti...</td>
      <td>8.72742</td>
      <td>77.68380</td>
      <td>P</td>
      <td>PPLA2</td>
      <td>IN</td>
      <td>NaN</td>
      <td>25</td>
      <td>628</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1435844</td>
      <td>NaN</td>
      <td>49</td>
      <td>Asia/Kolkata</td>
      <td>2017-08-27</td>
      <td>102.04</td>
    </tr>
    <tr>
      <th>20120</th>
      <td>1254661</td>
      <td>Thāne</td>
      <td>Thane</td>
      <td>Tanja,Tanna,Thana,Thane,Thāna,Thāne,tanh,tany,...</td>
      <td>19.19704</td>
      <td>72.96355</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>16</td>
      <td>517</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1261517</td>
      <td>NaN</td>
      <td>23</td>
      <td>Asia/Kolkata</td>
      <td>2019-03-29</td>
      <td>539.90</td>
    </tr>
    <tr>
      <th>20131</th>
      <td>1254745</td>
      <td>Teni</td>
      <td>Teni</td>
      <td>Teni,Theni,Tkheni,Тхени</td>
      <td>10.01115</td>
      <td>77.47772</td>
      <td>P</td>
      <td>PPLX</td>
      <td>IN</td>
      <td>NaN</td>
      <td>25</td>
      <td>624</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1034724</td>
      <td>NaN</td>
      <td>300</td>
      <td>Asia/Kolkata</td>
      <td>2017-08-02</td>
      <td>71.68</td>
    </tr>
    <tr>
      <th>20188</th>
      <td>1255364</td>
      <td>Surat</td>
      <td>Surat</td>
      <td>STV,Surat,Suratas,Surate,Sūrat,su la te,surata...</td>
      <td>21.19594</td>
      <td>72.83023</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>09</td>
      <td>492</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2894504</td>
      <td>NaN</td>
      <td>20</td>
      <td>Asia/Kolkata</td>
      <td>2020-04-04</td>
      <td>574.26</td>
    </tr>
    <tr>
      <th>20607</th>
      <td>1258847</td>
      <td>Rājkot</td>
      <td>Rajkot</td>
      <td>RAJ,Radzhkot,Radzkot,Radzkotas,Radźkot,Radžkot...</td>
      <td>22.29161</td>
      <td>70.79322</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>09</td>
      <td>476</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1177362</td>
      <td>NaN</td>
      <td>140</td>
      <td>Asia/Kolkata</td>
      <td>2017-03-17</td>
      <td>801.44</td>
    </tr>
    <tr>
      <th>20668</th>
      <td>1259229</td>
      <td>Pune</td>
      <td>Pune</td>
      <td>PNQ,Pona,Poona,Poune,Pun,Puna,Pune,Puneo,Puno,...</td>
      <td>18.51957</td>
      <td>73.85535</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>16</td>
      <td>521</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2935744</td>
      <td>NaN</td>
      <td>554</td>
      <td>Asia/Kolkata</td>
      <td>2015-06-04</td>
      <td>438.75</td>
    </tr>
    <tr>
      <th>20720</th>
      <td>1259652</td>
      <td>Pimpri</td>
      <td>Pimpri</td>
      <td>Pimpri</td>
      <td>18.62292</td>
      <td>73.80696</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>16</td>
      <td>521</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1284606</td>
      <td>NaN</td>
      <td>571</td>
      <td>Asia/Kolkata</td>
      <td>2014-10-13</td>
      <td>444.85</td>
    </tr>
    <tr>
      <th>20779</th>
      <td>1260086</td>
      <td>Patna</td>
      <td>Patna</td>
      <td>'Azimabad,New Patna,PAT,Patna,Patna New City,P...</td>
      <td>25.59408</td>
      <td>85.13563</td>
      <td>P</td>
      <td>PPLA</td>
      <td>IN</td>
      <td>NaN</td>
      <td>34</td>
      <td>230</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1599920</td>
      <td>NaN</td>
      <td>53</td>
      <td>Asia/Kolkata</td>
      <td>2018-12-14</td>
      <td>863.45</td>
    </tr>
    <tr>
      <th>20901</th>
      <td>1261162</td>
      <td>Nowrangapur</td>
      <td>Nowrangapur</td>
      <td>Nabarangapur,Nabarangpur,Nowrangpur</td>
      <td>19.23114</td>
      <td>82.54826</td>
      <td>P</td>
      <td>PPLA2</td>
      <td>IN</td>
      <td>NaN</td>
      <td>21</td>
      <td>397</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1220946</td>
      <td>NaN</td>
      <td>578</td>
      <td>Asia/Kolkata</td>
      <td>2014-10-14</td>
      <td>566.75</td>
    </tr>
    <tr>
      <th>20963</th>
      <td>1261731</td>
      <td>Nashik</td>
      <td>Nashik</td>
      <td>ISK,Nashik,Nasik,Nasikas,Nasiko,Naszik,Našikas...</td>
      <td>19.99727</td>
      <td>73.79096</td>
      <td>P</td>
      <td>PPLA2</td>
      <td>IN</td>
      <td>NaN</td>
      <td>16</td>
      <td>516</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1289497</td>
      <td>NaN</td>
      <td>584</td>
      <td>Asia/Kolkata</td>
      <td>2014-10-13</td>
      <td>460.81</td>
    </tr>
    <tr>
      <th>21023</th>
      <td>1262111</td>
      <td>Najafgarh</td>
      <td>Najafgarh</td>
      <td>Najafgarh,Najafgarli</td>
      <td>28.60922</td>
      <td>76.97982</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>07</td>
      <td>097</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1365000</td>
      <td>NaN</td>
      <td>215</td>
      <td>Asia/Kolkata</td>
      <td>2019-07-18</td>
      <td>387.38</td>
    </tr>
    <tr>
      <th>21033</th>
      <td>1262180</td>
      <td>Nagpur</td>
      <td>Nagpur</td>
      <td>Ajni,NAG,Nagpore,Nagpur,Nagpura,Nagpuras,Nankp...</td>
      <td>21.14631</td>
      <td>79.08491</td>
      <td>P</td>
      <td>PPLA2</td>
      <td>IN</td>
      <td>NaN</td>
      <td>16</td>
      <td>505</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2228018</td>
      <td>NaN</td>
      <td>319</td>
      <td>Asia/Kolkata</td>
      <td>2019-10-22</td>
      <td>249.83</td>
    </tr>
    <tr>
      <th>21155</th>
      <td>1263214</td>
      <td>Meerut</td>
      <td>Meerut</td>
      <td>Meerut,Meerut City,Merath,Meratkh,Mirat,Mirata...</td>
      <td>28.98002</td>
      <td>77.70636</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>36</td>
      <td>138</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1223184</td>
      <td>NaN</td>
      <td>228</td>
      <td>Asia/Kolkata</td>
      <td>2015-05-06</td>
      <td>380.43</td>
    </tr>
    <tr>
      <th>21318</th>
      <td>1264527</td>
      <td>Chennai</td>
      <td>Chennai</td>
      <td>Cenaj,Cenajo,Cenajus,Cenay,Cennai,Cennaj,Chehn...</td>
      <td>13.08784</td>
      <td>80.27847</td>
      <td>P</td>
      <td>PPLA</td>
      <td>IN</td>
      <td>NaN</td>
      <td>25</td>
      <td>603</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>4328063</td>
      <td>NaN</td>
      <td>14</td>
      <td>Asia/Kolkata</td>
      <td>2019-09-05</td>
      <td>302.29</td>
    </tr>
    <tr>
      <th>21339</th>
      <td>1264728</td>
      <td>Ludhiāna</td>
      <td>Ludhiana</td>
      <td>LUH,Ludhiana,Ludhijana,Ludhiāna,Ludkhijana,lud...</td>
      <td>30.91204</td>
      <td>75.85379</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>23</td>
      <td>041</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1545368</td>
      <td>NaN</td>
      <td>256</td>
      <td>Asia/Kolkata</td>
      <td>2017-03-07</td>
      <td>493.92</td>
    </tr>
    <tr>
      <th>21340</th>
      <td>1264733</td>
      <td>Lucknow</td>
      <td>Lucknow</td>
      <td>LKO,Lakhnau,Lakkhnau,Lakkhnau shaary,Laknaou,L...</td>
      <td>26.83928</td>
      <td>80.92313</td>
      <td>P</td>
      <td>PPLA</td>
      <td>IN</td>
      <td>NaN</td>
      <td>36</td>
      <td>157</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2472011</td>
      <td>NaN</td>
      <td>126</td>
      <td>Asia/Kolkata</td>
      <td>2015-11-11</td>
      <td>469.40</td>
    </tr>
    <tr>
      <th>21679</th>
      <td>1267995</td>
      <td>Kanpur</td>
      <td>Kanpur</td>
      <td>Cawnpore,KNU,Kanpur,Kanpuras,Kanpwr,Kānpur,Kān...</td>
      <td>26.46523</td>
      <td>80.34975</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>36</td>
      <td>164</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2823249</td>
      <td>NaN</td>
      <td>137</td>
      <td>Asia/Kolkata</td>
      <td>2015-08-08</td>
      <td>420.97</td>
    </tr>
    <tr>
      <th>21717</th>
      <td>1268295</td>
      <td>Kalyān</td>
      <td>Kalyan</td>
      <td>Kal'jan,Kalyan,Kalyān,Кальян</td>
      <td>19.24370</td>
      <td>73.13554</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>16</td>
      <td>517</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1262255</td>
      <td>NaN</td>
      <td>10</td>
      <td>Asia/Kolkata</td>
      <td>2014-10-13</td>
      <td>521.97</td>
    </tr>
    <tr>
      <th>21875</th>
      <td>1269515</td>
      <td>Jaipur</td>
      <td>Jaipur</td>
      <td>Caypur,Dzaipur,Dzaipuras,Dzajpur,Dzajpura,Dzha...</td>
      <td>26.91962</td>
      <td>75.78781</td>
      <td>P</td>
      <td>PPLA</td>
      <td>IN</td>
      <td>NaN</td>
      <td>24</td>
      <td>110</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2711758</td>
      <td>NaN</td>
      <td>435</td>
      <td>Asia/Kolkata</td>
      <td>2019-09-05</td>
      <td>406.82</td>
    </tr>
    <tr>
      <th>21893</th>
      <td>1269633</td>
      <td>Jabalpur</td>
      <td>Jabalpur</td>
      <td>Dzabalpur,Dzabalpuras,Dzhabalpur,Dzsabalpur,Dż...</td>
      <td>23.16697</td>
      <td>79.95006</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>35</td>
      <td>451</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1030168</td>
      <td>NaN</td>
      <td>416</td>
      <td>Asia/Kolkata</td>
      <td>2014-10-14</td>
      <td>344.75</td>
    </tr>
    <tr>
      <th>21907</th>
      <td>1269743</td>
      <td>Indore</td>
      <td>Indore</td>
      <td>IDR,Indaur,Indor,Indore,Indore Madhya Pradesh,...</td>
      <td>22.71792</td>
      <td>75.83330</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>35</td>
      <td>439</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1837041</td>
      <td>NaN</td>
      <td>550</td>
      <td>Asia/Kolkata</td>
      <td>2014-10-14</td>
      <td>314.12</td>
    </tr>
    <tr>
      <th>21924</th>
      <td>1269843</td>
      <td>Hyderabad</td>
      <td>Hyderabad</td>
      <td>Bhaganagar,HYD,Haidarabadas,Haiderabad,Hajdara...</td>
      <td>17.38405</td>
      <td>78.45636</td>
      <td>P</td>
      <td>PPLA</td>
      <td>IN</td>
      <td>NaN</td>
      <td>40</td>
      <td>536</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>3597816</td>
      <td>NaN</td>
      <td>515</td>
      <td>Asia/Kolkata</td>
      <td>2014-10-10</td>
      <td>142.53</td>
    </tr>
    <tr>
      <th>21993</th>
      <td>1270396</td>
      <td>Hāora</td>
      <td>Haora</td>
      <td>Haora,Haura,Hawrah,Howrah,Hāora,ha'ora,haura,হ...</td>
      <td>22.57688</td>
      <td>88.31857</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>28</td>
      <td>341</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1027672</td>
      <td>NaN</td>
      <td>8</td>
      <td>Asia/Kolkata</td>
      <td>2014-10-14</td>
      <td>1199.32</td>
    </tr>
    <tr>
      <th>22063</th>
      <td>1270926</td>
      <td>Gorakhpur</td>
      <td>Gorakhpur</td>
      <td>Gorakhpur,Gorakpura,Горакпура</td>
      <td>29.44768</td>
      <td>75.67206</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>10</td>
      <td>078</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1324570</td>
      <td>NaN</td>
      <td>218</td>
      <td>Asia/Kolkata</td>
      <td>2017-09-05</td>
      <td>471.06</td>
    </tr>
    <tr>
      <th>22105</th>
      <td>1271308</td>
      <td>Ghāziābād</td>
      <td>Ghaziabad</td>
      <td>Gaziabad,Ghaziabad,Ghazibad,Ghāziābād,Газиабад</td>
      <td>28.66535</td>
      <td>77.43915</td>
      <td>P</td>
      <td>PPLA2</td>
      <td>IN</td>
      <td>NaN</td>
      <td>36</td>
      <td>140</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1199191</td>
      <td>NaN</td>
      <td>214</td>
      <td>Asia/Kolkata</td>
      <td>2018-07-13</td>
      <td>376.86</td>
    </tr>
    <tr>
      <th>22186</th>
      <td>1271951</td>
      <td>Faridabad</td>
      <td>Faridabad</td>
      <td>Faridabad,Faridabadas,Farīdābād,QNF,faridabado...</td>
      <td>28.41124</td>
      <td>77.31316</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>10</td>
      <td>088</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1220229</td>
      <td>NaN</td>
      <td>209</td>
      <td>Asia/Kolkata</td>
      <td>2017-05-06</td>
      <td>373.40</td>
    </tr>
    <tr>
      <th>22234</th>
      <td>1272423</td>
      <td>Dombivli</td>
      <td>Dombivli</td>
      <td>Dombivali</td>
      <td>19.21667</td>
      <td>73.08333</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>16</td>
      <td>517</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1193000</td>
      <td>NaN</td>
      <td>11</td>
      <td>Asia/Kolkata</td>
      <td>2014-10-13</td>
      <td>527.29</td>
    </tr>
    <tr>
      <th>22333</th>
      <td>1273294</td>
      <td>Delhi</td>
      <td>Delhi</td>
      <td>DEL,Daehli,Dehli,Dehlī,Delchi,Delhi,Delhio,Del...</td>
      <td>28.65195</td>
      <td>77.23149</td>
      <td>P</td>
      <td>PPLA</td>
      <td>IN</td>
      <td>NaN</td>
      <td>07</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>10927986</td>
      <td>NaN</td>
      <td>227</td>
      <td>Asia/Kolkata</td>
      <td>2019-09-05</td>
      <td>381.11</td>
    </tr>
    <tr>
      <th>22512</th>
      <td>1275004</td>
      <td>Kolkāta</td>
      <td>Kolkata</td>
      <td>CCU,Calcuta,Calcutta,Calcutá,Calcúta,Caligarda...</td>
      <td>22.56263</td>
      <td>88.36304</td>
      <td>P</td>
      <td>PPLA</td>
      <td>IN</td>
      <td>NaN</td>
      <td>28</td>
      <td>342</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>4631392</td>
      <td>NaN</td>
      <td>11</td>
      <td>Asia/Kolkata</td>
      <td>2020-04-08</td>
      <td>1204.16</td>
    </tr>
    <tr>
      <th>22534</th>
      <td>1275339</td>
      <td>Mumbai</td>
      <td>Mumbai</td>
      <td>Asumumbay,BOM,Bombai,Bombaim,Bombaj,Bombay,Bom...</td>
      <td>19.07283</td>
      <td>72.88261</td>
      <td>P</td>
      <td>PPLA</td>
      <td>IN</td>
      <td>NaN</td>
      <td>16</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>12691836</td>
      <td>NaN</td>
      <td>8</td>
      <td>Asia/Kolkata</td>
      <td>2019-09-05</td>
      <td>547.46</td>
    </tr>
    <tr>
      <th>22605</th>
      <td>1275841</td>
      <td>Bhopāl</td>
      <td>Bhopal</td>
      <td>BHO,Bhojpal,Bhopal,Bhopala,Bhopalas,Bhopalo,Bh...</td>
      <td>23.25469</td>
      <td>77.40289</td>
      <td>P</td>
      <td>PPLA</td>
      <td>IN</td>
      <td>NaN</td>
      <td>35</td>
      <td>444</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1599914</td>
      <td>NaN</td>
      <td>523</td>
      <td>Asia/Kolkata</td>
      <td>2020-04-08</td>
      <td>248.18</td>
    </tr>
    <tr>
      <th>22786</th>
      <td>1277333</td>
      <td>Bengaluru</td>
      <td>Bengaluru</td>
      <td>BLR,Ban'nkalor,Bangalor,Bangalora,Bangalore,Ba...</td>
      <td>12.97194</td>
      <td>77.59369</td>
      <td>P</td>
      <td>PPLA</td>
      <td>IN</td>
      <td>NaN</td>
      <td>19</td>
      <td>572</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>5104047</td>
      <td>920.0</td>
      <td>914</td>
      <td>Asia/Kolkata</td>
      <td>2019-09-05</td>
      <td>3.75</td>
    </tr>
    <tr>
      <th>22886</th>
      <td>1278149</td>
      <td>Aurangabad</td>
      <td>Aurangabad</td>
      <td>Aurangabad,Aurangabad - aurangabada,Aurangabad...</td>
      <td>19.87757</td>
      <td>75.34226</td>
      <td>P</td>
      <td>PPLA2</td>
      <td>IN</td>
      <td>NaN</td>
      <td>16</td>
      <td>515</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1016441</td>
      <td>NaN</td>
      <td>588</td>
      <td>Asia/Kolkata</td>
      <td>2019-03-29</td>
      <td>304.86</td>
    </tr>
    <tr>
      <th>22967</th>
      <td>1278710</td>
      <td>Amritsar</td>
      <td>Amritsar</td>
      <td>ATQ,Amricar,Amritsar,Amritsar - amritasara,Amr...</td>
      <td>31.62234</td>
      <td>74.87534</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>23</td>
      <td>049</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1092450</td>
      <td>NaN</td>
      <td>244</td>
      <td>Asia/Kolkata</td>
      <td>2015-11-08</td>
      <td>573.56</td>
    </tr>
    <tr>
      <th>23013</th>
      <td>1278994</td>
      <td>Allahābād</td>
      <td>Allahabad</td>
      <td>Alahabadas,Alla Abba Habab,Allahabad,Allahabad...</td>
      <td>25.44478</td>
      <td>81.84322</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>36</td>
      <td>175</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1073438</td>
      <td>NaN</td>
      <td>99</td>
      <td>Asia/Kolkata</td>
      <td>2020-01-17</td>
      <td>534.30</td>
    </tr>
    <tr>
      <th>23054</th>
      <td>1279233</td>
      <td>Ahmedabad</td>
      <td>Ahmedabad</td>
      <td>AMD,Achmentampant,Ahmadabad,Ahmadabadas,Ahmada...</td>
      <td>23.02579</td>
      <td>72.58727</td>
      <td>P</td>
      <td>PPL</td>
      <td>IN</td>
      <td>NaN</td>
      <td>09</td>
      <td>474</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>3719710</td>
      <td>NaN</td>
      <td>56</td>
      <td>Asia/Kolkata</td>
      <td>2019-09-05</td>
      <td>621.49</td>
    </tr>
    <tr>
      <th>23056</th>
      <td>1279259</td>
      <td>Agra</td>
      <td>Agra</td>
      <td>AGR,Agra,Agra - agara,Agra - आगरा,Lungsod ng A...</td>
      <td>27.18333</td>
      <td>78.01667</td>
      <td>P</td>
      <td>PPLA2</td>
      <td>IN</td>
      <td>NaN</td>
      <td>36</td>
      <td>146</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1430055</td>
      <td>NaN</td>
      <td>166</td>
      <td>Asia/Kolkata</td>
      <td>2016-10-17</td>
      <td>337.27</td>
    </tr>
    <tr>
      <th>23132</th>
      <td>6619347</td>
      <td>Navi Mumbai</td>
      <td>Navi Mumbai</td>
      <td>Marathi  Maharashtra,Navi Moembaai,Navi Mumbai...</td>
      <td>19.03681</td>
      <td>73.01582</td>
      <td>P</td>
      <td>PPLX</td>
      <td>IN</td>
      <td>NaN</td>
      <td>16</td>
      <td>517</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2600000</td>
      <td>NaN</td>
      <td>14</td>
      <td>Asia/Kolkata</td>
      <td>2018-12-04</td>
      <td>532.88</td>
    </tr>
  </tbody>
</table>
</div>



```python
output = os.path.join(home_dir, 'Downloads', 'output.csv')
print(output)
india_df.to_csv(output, index=False)
```

    /Users/ujaval/Downloads/output.csv



```python

```


```python

```


```python

```
