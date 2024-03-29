import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt
import warnings


"""
To do
make rev,op_inc,eps,bv all arrays with len 20 (10 yrs forward 10 back)

"""

# if you have an error the chromedriver and chrome versions might not match
# to fix this go here https://chromedriver.chromium.org/downloads 
# and download the chromedriver that matches
# then move the new chromedriver to /usr/bin/ with this command 
# sudo cp chromedriver /usr/bin/chromedriver

#possible source http://download.macrotrends.net/assets/php/stock_data_export.php?t=MSFT
# posssible source yahoo finance
# possible source https://api.tiingo.com/documentation/fundamentals
# possible source http://financials.morningstar.com/ratios/r.html?t=ATD.B&region=can&culture=en-US&ownerCountry=USA

def dcf(ticker,symbol,region='can'):
    def get_prices(symbol):
        function = 'TIME_SERIES_DAILY'
        output = 'full'
        datatype = 'json'
        API_Key = 'XBET0AP2U4BAY3CK'
        url = 'https://www.alphavantage.co/query?function=' + function +'&symbol=' + symbol +'&outputsize='+output+'&apikey='+API_Key

        price_ticker = requests.get(url).json()

        #print(data)
        try:
            prices = price_ticker[list(price_ticker)[1]]
        except:
            prices = 0.0
        
        return prices



    def download_data(ticker):

        #from urllib.request import urlopen
        from selenium import webdriver
        import time
        if ticker=='BA':
            ticker='0P000000TU'
        elif ticker =='CI':
            ticker ='0P0000019K'
        elif ticker=='CCI':
            ticker='0P000001K3'
        elif ticker=='MMM':
            ticker='0P0000000I'
        elif ticker=='RTX':
            ticker='0P000005NO'
        elif ticker=='TSLA':
            ticker='0P0000OQN8'
        elif ticker=='BABA':
            ticker='0P00013K81'
        elif  ticker=='DIS':
            ticker='0P000005UJ'
        elif ticker=='A':
            ticker='0P0000007E'
        elif ticker=='NGT':
            ticker='0P0001HBP5'
        elif ticker=='BIDU':
            ticker = '0P000000OE'
        elif ticker=='CNC':
            ticker='0P0000015E'
        elif ticker =='COST':
            ticker='0P000001IK'
        elif ticker=='CRM':
            ticker='0P000004T1'
        elif ticker=='LEN':
            ticker='0P0000039N'
        elif ticker=='MSFT':
            ticker='0P000003MH'
        elif ticker=='GNW':
            ticker='0P000002EJ'
        elif ticker=='PNC':
            ticker='0P00000464'
        elif ticker=='SQ':
            ticker='0P00016Z2D'
        elif ticker=='MU':
            ticker='0P000003MC'
        
            
        url = "http://financials.morningstar.com/ratios/r.html?t="+ticker+"&region="+region+"&culture=en-US&ownerCountry=USA"
        print(url)

        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory' : '/media/adam/OS/Documents and Settings/amcmu/Documents/Random/Stock Scraper'}
        chrome_options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(chrome_options=chrome_options)


        #driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        driver.find_element_by_css_selector('.large_button').click()
        time.sleep(1.5)
        driver.quit()


    def load_data(ticker):
        try:
            data=pd.read_csv(ticker+" Key Ratios.csv",header=2,index_col=0).replace(',','',regex=True)
        except:
            download_data(ticker)
            data=pd.read_csv(ticker+" Key Ratios.csv",header=2,index_col=0).replace(',','',regex=True)
            
        return data

    def clean_data(df):
        df = df.rename(columns={df.columns[-1]: pd.Timestamp("today").strftime("%Y-%m")}, index={df.index[0]: "revenue", df.index[2]: "op income", df.index[5]: "eps", df.index[6]: "dividend", df.index[8]: "shares", df.index[9]: "book value", df.index[13]: "fcf"})
        df = df.drop([df.index[15], df.index[16], df.index[26], df.index[35], df.index[36], df.index[57], df.index[58], df.index[64], df.index[65], df.index[86], df.index[91], df.index[92]])
        df=df.astype(float)       
        return df
                
    def fit(x,y):
        idx = np.isfinite(x) & np.isfinite(y)
        z = np.polyfit(x[idx], y[idx], 1)
        f = np.poly1d(z)
        return f

    print('-----------')
    
    df=load_data(ticker)
    df=clean_data(df)

    #print(data)
    #print(data.keys())
    #print(data['Financials'].keys())
    print(ticker)
    print(df)

    def rolling_avg(x,period):
        return x.rolling(window=period,min_periods=period).mean()

    def get_change(x):
        yoy=x.pct_change()*100
        avg_3yr=rolling_avg(yoy,3)
        avg_5yr=rolling_avg(yoy,5)
        avg_10yr=rolling_avg(yoy,10)
        
        return pd.concat([yoy, avg_3yr, avg_5yr, avg_10yr],axis=1)

    def get_growth():
        try:
            rev_growth=df.iloc[33:37]#precomputed by morningstar
            rev_growth_avg=np.nanmean(rev_growth.mean(axis=1,skipna=True).values)
        except:
            rev_growth=get_change(df.loc['revenue'])
            rev_growth_avg = np.nanmean(rev_growth.mean().values)

        try:
            inc_growth=df.iloc[38:42]#precomputed by morningstar
            inc_growth_avg = np.nanmean(inc_growth.mean(axis=1, skipna=True).values)
        except:
            inc_growth=get_change(df.loc['op income'])
            inc_growth_avg = np.nanmean(inc_growth.mean().values)

        try:
            eps_growth=df.iloc[48:52]#precomputed by morningstar
            eps_growth_avg = np.nanmean(eps_growth.mean(axis=1, skipna=True).values)
        except:
            eps_growth=get_change(df.loc['eps'])
            eps_growth_avg = np.nanmean(eps_growth.mean().values)

        try:
            fcf_growth=df.loc['Free Cash Flow Growth % YOY']#precomputed by morningstar 53
            fcf_growth_avg = np.nanmean(fcf_growth.mean(skipna=True).values)
        except:
            fcf_growth=get_change(df.loc['fcf'])
            fcf_growth_avg = np.nanmean(fcf_growth.mean().values)
    
        try:
            bv_growth=get_change(df.loc['book value'])
            bv_growth_avg = np.nanmean(bv_growth.mean().values)
        except:
            bv_growth=df.loc['Return on Equity %']#roe
            bv_growth_avg = np.nanmean(bv_growth.mean(skipna=True).values)
            
        rate=np.nanmean([np.average(rev_growth_avg),np.average(inc_growth_avg),np.average(eps_growth_avg),np.average(fcf_growth_avg),np.average(bv_growth_avg)])
        return rate,rev_growth, inc_growth,eps_growth,fcf_growth,bv_growth,rev_growth_avg, inc_growth_avg,eps_growth_avg,fcf_growth_avg,bv_growth_avg

    #dates=data['Financials']['']
    #dates[dates.index('TTM')] = pd.Timestamp("today").strftime("%Y-%m")


#    print(df[0:15])
#    print(df)
#    print(df.index)
#    print(df.columns)
#    print(df.loc['revenue'])

    #rev_past=df.iloc[0].astype(float)
    #op_inc=df.iloc[2].astype(float)
#if op_inc=='na':
#    opc_inc=df.iloc[4].astype(float)
    #eps_past=df.iloc[5].astype(float)
    #div_past=df.iloc[6].astype(float)
    #shares_past=df.iloc[8].astype(float)
    #bv_past=df.iloc[9].astype(float)
    #fcf_past=df.iloc[13].astype(float)
#if fcfps=='na':
#    fcfps=df.iloc[12].astype(float)/shares



    #growth_rate=compute_growth()
    growth_rate,rev_growth, inc_growth,eps_growth,fcf_growth,bv_growth,rev_growth_avg, inc_growth_avg,eps_growth_avg,fcf_growth_avg,bv_growth_avg=get_growth()
    print(growth_rate)
    #print(df.loc['fcf'])

    
    discount_rate=0.15
    long_term_growth=0.02
    yrs_to_hold=10.0
    #base_fcf=fcf_y[-1]
    #base_eps=eps_y[-1]
    base_fcf=df.loc['fcf'][~np.isnan(df.loc['fcf'])][-1]
    base_eps=df.loc['eps'][~np.isnan(df.loc['eps'])][-1]
    years=np.arange(10)

    fcf=base_fcf*(1+growth_rate/100)**years
    eps = base_eps * (1 + growth_rate / 100) ** years


    #print(np.reshape(np.tile(rev_growth.columns.values,np.shape(rev_growth)[0]),np.shape(rev_growth)))

    def plot():
        years_past = np.arange(len(df.columns))

        print('Rev growth', rev_growth_avg)
        print('Inc growth', inc_growth_avg)
        print('Eps growth', eps_growth_avg)
        print('Fcf growth', fcf_growth_avg)
        print('Bv growth', bv_growth_avg)
        print('Growth', growth_rate)
        plt.plot(rev_growth.columns.values, np.asarray(rev_growth).T,'r')
        plt.plot(years_past, np.ones(len(years_past))*rev_growth_avg,'r')
        plt.plot(inc_growth.columns.values, np.asarray(inc_growth).T, 'b')
        plt.plot(years_past, np.ones(len(years_past)) * inc_growth_avg, 'b')
        plt.plot(eps_growth.columns.values, np.asarray(eps_growth).T, 'g')
        plt.plot(years_past, np.ones(len(years_past)) * eps_growth_avg, 'g')
        plt.plot(fcf_growth.T.columns.values, np.asarray(fcf_growth), 'c')
        plt.plot(years_past, np.ones(len(years_past)) * fcf_growth_avg, 'c')
        plt.plot(bv_growth.T.columns.values, np.asarray(bv_growth), 'y')
        plt.plot(years_past, np.ones(len(years_past)) * bv_growth_avg, 'y')
        plt.plot(years_past, np.ones(len(years_past))*growth_rate,'k')
        plt.xlabel('Year')
        plt.ylabel('Percent change')
        plt.show()

        print(df.loc['fcf'])
        fcf_fit = fit(years_past, df.loc['fcf'])
        plt.bar(years_past, df.loc['fcf'])
        plt.plot(np.append(years_past,len(years_past)+years), fcf_fit(np.append(years_past,len(years_past)+years)))
        plt.bar(years_past[-1], base_fcf)
        plt.bar(len(years_past)+years,fcf)
        plt.ylabel('Free cash flow per share')
        plt.xlabel('Year')
        plt.show()

        print(df.loc['eps'])
        eps_fit = fit(years_past, df.loc['eps'])
        plt.bar(years_past, df.loc['eps'])
        plt.plot(np.append(years_past, len(years_past) + years),
                 eps_fit(np.append(years_past, len(years_past) + years)))
        plt.bar(years_past[-1], base_eps)
        plt.bar(len(years_past) + years, eps)
        plt.ylabel('Earnings per share')
        plt.xlabel('Year')
        plt.show()


    plot()
    dfcf=base_fcf*((1-((1+growth_rate/100)/(1+discount_rate))**(yrs_to_hold+1))/(1-((1+growth_rate/100)/(1+discount_rate)))-1)
    dpfcf=base_fcf*(1+growth_rate/100)**yrs_to_hold*(1+long_term_growth)/(1+discount_rate)**(yrs_to_hold)/(discount_rate-long_term_growth)
    intrinsic_value=dfcf+dpfcf
    prices=get_prices(symbol)
    try:
        current_price=float(prices[list(prices)[0]]['4. close'])
    except:
        current_price=0.0

    current_discount=1-current_price/intrinsic_value

    print('-----------')
    print(ticker)
#    print([np.average(string2float(growth_rev_1)),np.average(string2float(growth_inc_1)),np.average(string2float(growth_eps_1)),np.average(string2float(growth_fcf)),np.average(string2float(growth_bv))])
    #print(string2float(growth_rev_1),string2float(growth_inc_1),string2float(growth_eps_1),string2float(growth_fcf),string2float(growth_bv)
    #print(list(data.keys())[0].replace('\ufeffGrowth Profitability and Financial Ratios for ','')) 
    print('Growth rate:', round(growth_rate,2), '%')
    print('Free cash flow: $', round(base_fcf,2))
    print('Earnings per share: $', round(base_eps,2))
    print('Intrinsic value: $', round(intrinsic_value,2))
    print('Current price: $', round(current_price,2))
    print('Current discount: ', round(current_discount*100,2), '%')


#TFSA ACCOUNT
dcf('AMZN','AMZN','us')
dcf('BA','BA','us')
dcf('BCE','BCE.TRT')
#dcf('BEPC','BEPC.TRT')
#dcf('BIPC','BIPC.TRT')
dcf('BEP.UN','BEP-UN.TRT')
dcf('BIP.UN','BIP-UN.TRT')
dcf('BRK.B','BRK-B','us')
dcf('CCA','CCA.TRT')
dcf('CCI','CCI','us')
dcf('CM','CM.TRT')
dcf('CNR','CNR.TRT')
dcf('ENB','ENB.TRT')
dcf('IMO','IMO.TRT')
dcf('KXS','KXS.TRT')
dcf('L','L.TRT')
dcf('MFC','MFC.TRT')
dcf('MG','MG.TRT')
dcf('MMM','MMM','us')
dcf('MU','MU','us')
dcf('NGT','NGT.TRT')
dcf('PLC','PLC.TRT')
dcf('REAL','REAL.TRT')
dcf('RTX','RTX','us')
dcf('RY','RY.TRT')
dcf('SNC','SNC.TRT')
dcf('T','T.TRT')
dcf('TD','TD.TRT')
dcf('TSLA','TSLA','us')

#NON-REGISTERED ACCOUNT
dcf('AQN','AQN.TRT')
dcf('ATD','ATD.TRT')
####dcf('BABA','BABA','us')
#dcf('BCE','BCE.TRT')
#dcf('BIPC','BIPC.TRT')
#dcf('BRK.B','BRK-B','us')
#dcf('CCA','CCA.TRT')
dcf('CNQ','CNQ.TRT')
dcf('CP','CP.TRT')
dcf('CPNG','CPNG','us')
#dcf('ENB','ENB.TRT')
dcf('ENGH','ENGH.TRT')
dcf('FTS','FTS.TRT')
dcf('GWO','GWO.TRT')
dcf('IAG','IAG.TRT')
dcf('INTC','INTC','us')
#dcf('L','L.TRT')
dcf('LMT','LMT','us')
#dcf('MFC','MFC.TRT')
#dcf('MU','MU','us')
dcf('NTR','NTR.TRT')
#dcf('REAL','REAL.TRT')
#dcf('RTX','RTX','us')
#dcf('RY','RY.TRT')
dcf('SLF','SLF.TRT')
dcf('SU','SU.TRT')
#dcf('TD','TD.TRT')

dcf('DIS','DIS','us')

# WATCHLIST
dcf('A','A','us')
dcf('AC','AC.TRT')
dcf('AD.UN','AD-UN.TRT')
dcf('AGF.B','AGF-B.TRT')
dcf('ALYA','ALYA.TRT')
dcf('AMD','AMD','us')
dcf('BAM.A','BAM-A.TRT')
###dcf('BIDU','BIDU','us') # need to do by hand
dcf('BB','BB.TRT')
dcf('BDT','BDT.TRT')
dcf('BERY','BERY','us')
dcf('BIIB','BIIB','us')
dcf('BLX','BLX.TRT')
dcf('BYD','BYD.TRT')
dcf('CAS','CAS.TRT')
dcf('CAE','CAE.TRT')
dcf('CAR.UN','CAR-UN.TRT')
dcf('CHR','CHR.TRT')
dcf('CI','CI','us')
dcf('CIX','CIX.TRT')
dcf('CJT','CJT.TRT')
dcf('CNC','CNC','us')
dcf('COST','COST','us')
dcf('CRM','CRM','us') #SALESFORCE
dcf('CRR.UN','CRR-UN.TRT')
dcf('CRSP','CRSP','us')
dcf('CRWD','CRWD','us')
dcf('CSU','CSU.TRT')
dcf('CTC.A','CTC-A.TRT')
dcf('CVE','CVE','us')
dcf('CVS','CVS','us')
dcf('CWL','CWL.TRT')
dcf('D.UN','D-UN.TRT')
dcf('DDOG','DDOG','us')
dcf('DHI','DHI','us')
dcf('DIR.UN','DIR-UN.TRT')
dcf('DOL','DOL.TRT')
dcf('DIV','DIV.TRT')
dcf('EMA','EMA.TRT')
dcf('GIB.A','GIB-A.TRT')
dcf('GIS','GIS','us')
dcf('GNW','GNW','us')
dcf('GOOGL','GOOGL','us')
dcf('GRT.UN','GRT-UN.TRT')
dcf('GSY','GSY.TRT')
dcf('HCG','HCG.TRT')
dcf('HD','HD','us')
dcf('HLF','HLF.TRT')
dcf('HMM.A','HMM-A.TRT')
dcf('HOT.UN','HOT-UN.TRT')
dcf('HPS.A','HPS-A.TRT')
dcf('HR.UN','HR-UN.TRT')
dcf('IFC','IFC.TRT')
dcf('IGM','IGM.TRT')
dcf('IIP.UN','IIP-UN.TRT')
dcf('ILMN','ILMN','us')
dcf('INE','INE.TRT')
###dcf('JD','JD','us')
dcf('JNJ','JNJ','us')
dcf('JWEL','JWEL.TRT')
dcf('LAS.A','LAS-A.TRT')
dcf('LEN','LEN','us')
dcf('LMND','LMND','us')
dcf('LNF','LNF.TRT')
dcf('LOW','LOW','us')
dcf('LRCX','LRCX','us')
dcf('LSPD','LSPD.TRT')
dcf('MA','MA','us')
dcf('MELI','MELI','us')
###dcf('META','META','us') too new
dcf('MSFT','MSFT','us')
dcf('MX','MX.TRT')
dcf('NPI','NPI.TRT')
dcf('NVDA','NVDA','us')
dcf('NVEI','NVEI.TRT')
dcf('OCSL','OCSL','us')
dcf('ONEX','ONEX.TRT')
dcf('PIF','PIF.TRT')
dcf('PNC','PNC','us')
dcf('QSR','QSR.TRT')
dcf('RCI.B','RCI-B.TRT')
dcf('RNW','RNW.TRT')
dcf('SHOP','SHOP.TRT')
dcf('SIS','SIS.TRT')
dcf('SOFI','SOFI','us')
dcf('SOT.UN','SOT-UN.TRT')
dcf('SQ','SQ','us')
dcf('SWKS','SWKS','us')
dcf('STN','STN.TRT')
dcf('TCN','TCN.TRT')
dcf('TCL.A','TCL-A.TRT')
dcf('TFII','TFII.TRT')
dcf('TROW','TROW','us')
dcf('UNH','UNH','us')
dcf('V','V','us')
dcf('WCN','WCN.TRT')
dcf('WN','WN.TRT')
dcf('X','X.TRT')
dcf('XTC','XTC.TRT')

quit()



print(get_percent_change(inc_y))
print(get_percent_change(inc_fit[0]*inc_x+inc_fit[1]))




plt.plot(inc_x,inc_y,'o', inc_x, inc_fit[0]*inc_x+inc_fit[1])
plt.show()
plt.plot(rev_x,rev_y,'o', rev_x, rev_fit[0]*rev_x+rev_fit[1])
plt.show()
plt.plot(eps_x,eps_y,'o', eps_x, eps_fit[0]*eps_x+eps_fit[1])
plt.show()
plt.plot(fcf_x,fcf_y,'o', fcf_x, fcf_fit[0]*fcf_x+fcf_fit[1])
plt.show()
plt.plot(bv_x,bv_y,'o', bv_x, bv_fit[0]*bv_x+bv_fit[1])
plt.show()


function = 'INCOME_STATEMENT'
symbol = 'TD'
output = 'full'
datatype = 'json'
API_Key = 'XBET0AP2U4BAY3CK'

url = 'https://www.alphavantage.co/query?function=' + function +'&symbol=' + symbol +'&outputsize='+output+'&apikey='+API_Key

data = requests.get(url).json()
print(data)
quit()




# API Key from ALpha Vantage(https://www.alphavantage.co/documentation/) XBET0AP2U4BAY3CK

