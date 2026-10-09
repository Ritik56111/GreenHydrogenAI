from datetime import datetime,timedelta
import math,random
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestRegressor

app=FastAPI(title='GreenHydrogen AI API',version='2.0')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_methods=['*'],allow_headers=['*'])

class Input(BaseModel):
    solar:float=Field(ge=0); wind:float=Field(ge=0); hydro:float=Field(ge=0)
    temperature:float=25; humidity:float=Field(50,ge=0,le=100)
    electrolyzer_efficiency:float=Field(.78,gt=0,le=1)

def calc(s,w,h,t,hu,eff=.78):
    total=max(0,s+w+h); tf=1-min(abs(t-28)/100,.18); hf=1-min(abs(hu-50)/500,.10)
    return max(0,total*.0235*tf*hf*eff)
def efficiency(s,w,h,eff=.78): return round(min(.98,.45+.32*min(1,(s+w+h)/180)+.23*eff)*100,1)
def carbon(h): return round(max(0,h)*3.6,2)

H=[]; now=datetime.now().replace(minute=0,second=0,microsecond=0)
for i in range(72):
    ts=now-timedelta(hours=71-i); hr=ts.hour
    s=max(0,120*math.sin(math.pi*(hr-6)/12)) if 6<=hr<=18 else 0
    s*=random.uniform(.8,1.12); w=random.uniform(25,85); h=random.uniform(15,45)
    t=25+8*math.sin((hr-8)*math.pi/12)+random.uniform(-2,2); hu=random.uniform(35,80); ef=random.uniform(.68,.86)
    hyd=calc(s,w,h,t,hu,ef); H.append({'timestamp':ts.isoformat(),'solar':round(s,2),'wind':round(w,2),'hydro':round(h,2),'temperature':round(t,2),'humidity':round(hu,2),'hydrogen':round(hyd,2),'efficiency':efficiency(s,w,h,ef),'carbon_saving':carbon(hyd)})

rng=np.random.default_rng(42); X=[]; y=[]
for _ in range(900):
    s,w,h=rng.uniform(0,140),rng.uniform(0,90),rng.uniform(0,50); t,hu=rng.uniform(15,42),rng.uniform(20,90); ef=rng.uniform(.6,.9)
    X.append([s,w,h,t,hu,ef]); y.append(calc(s,w,h,t,hu,ef)+rng.normal(0,.06))
model=RandomForestRegressor(n_estimators=180,random_state=42,max_depth=11).fit(X,np.maximum(y,0))

def analyze(x):
    vals={'Solar':x.solar,'Wind':x.wind,'Hydro':x.hydro}; dominant=max(vals,key=vals.get); total=sum(vals.values()); hyd=calc(x.solar,x.wind,x.hydro,x.temperature,x.humidity,x.electrolyzer_efficiency); ef=efficiency(x.solar,x.wind,x.hydro,x.electrolyzer_efficiency)
    insights=[]; rec=[]
    insights.append(f'{dominant} is the dominant renewable source in the current scenario.')
    insights.append('Hydrogen output is being estimated from renewable availability and operating conditions.')
    if x.electrolyzer_efficiency<.65: insights.append('Electrolyzer efficiency is below the preferred simulated range.'); rec.append('Shift flexible load to high-renewable periods and review electrolyzer efficiency.')
    else: rec.append(f'Prioritize {dominant} during its strongest availability window.')
    if total<80: insights.append('Renewable availability is relatively low.'); rec.append('Avoid aggressive electrolyzer loading until renewable availability improves.')
    else: rec.append('Use renewable-rich windows to improve hydrogen yield and utilization.')
    if x.temperature>40: rec.append('Monitor high-temperature operating conditions.')
    status='EXCELLENT' if ef>=80 else 'GOOD' if ef>=65 else 'NEEDS ATTENTION'
    confidence=round(min(96,70+ef*.25),1)
    return {'status':status,'confidence':confidence,'dominant_source':dominant,'hydrogen':round(hyd,2),'efficiency':ef,'carbon_saving':carbon(hyd),'insights':insights,'recommendations':rec}

def anomalies(x):
    alerts=[]; severity='LOW'; total=x.solar+x.wind+x.hydro
    if x.electrolyzer_efficiency<.5: alerts.append({'severity':'HIGH','message':'Electrolyzer efficiency is critically low.'}); severity='HIGH'
    if total<45: alerts.append({'severity':'MEDIUM','message':'Renewable availability is low; hydrogen yield may fall.'}); severity='HIGH' if severity=='HIGH' else 'MEDIUM'
    if x.temperature>42: alerts.append({'severity':'MEDIUM','message':'Temperature is unusually high for this simulation.'}); severity='HIGH' if severity=='HIGH' else 'MEDIUM'
    if not alerts: alerts=[{'severity':'LOW','message':'No major anomaly detected in the current scenario.'}]
    return {'severity':severity,'alerts':alerts}

@app.get('/')
def root(): return {'project':'AI-Based Green Hydrogen Production Optimization and Monitoring','status':'running','docs':'/docs'}
@app.get('/api/health')
def health(): return {'status':'healthy'}
@app.get('/api/dashboard')
def dashboard():
    x=H[-1]; a=analyze(Input(**{k:x[k] for k in ['solar','wind','hydro','temperature','humidity']})); return {'solar':x['solar'],'wind':x['wind'],'hydro':x['hydro'],'total_renewable':round(x['solar']+x['wind']+x['hydro'],2),'hydrogen':x['hydrogen'],'efficiency':x['efficiency'],'carbon_saving':x['carbon_saving'],'ai_confidence':a['confidence'],'dominant_source':a['dominant_source']}
@app.get('/api/history')
def history(): return H
@app.post('/api/predict')
def predict(x:Input):
    hyd=max(0,float(model.predict([[x.solar,x.wind,x.hydro,x.temperature,x.humidity,x.electrolyzer_efficiency]])[0])); return {'hydrogen':round(hyd,2),'efficiency':efficiency(x.solar,x.wind,x.hydro,x.electrolyzer_efficiency),'carbon_saving':carbon(hyd),'model':'Random Forest prototype model'}
@app.post('/api/ai/analyze')
def ai_analysis(x:Input): return analyze(x)
@app.post('/api/anomaly')
def anomaly(x:Input): return anomalies(x)
@app.post('/api/optimize')
def optimize(x:Input):
    vals={'Solar':x.solar,'Wind':x.wind,'Hydro':x.hydro}; dominant=max(vals,key=vals.get); base=calc(x.solar,x.wind,x.hydro,x.temperature,x.humidity,x.electrolyzer_efficiency); new=min(.95,x.electrolyzer_efficiency+.07); improved=calc(x.solar*1.08,x.wind*1.04,x.hydro,x.temperature,x.humidity,new); gain=round((improved-base)/base*100,1) if base else 0
    return {'recommended_source':dominant,'baseline_hydrogen':round(base,2),'optimized_hydrogen':round(improved,2),'estimated_improvement':gain,'recommendations':[f'Prioritize {dominant} during high-availability periods.','Shift flexible electrolyzer load toward renewable-rich windows.','Monitor efficiency before increasing simulated load.']}
@app.post('/api/forecast')
def forecast(x:Input):
    base=x.solar+x.wind+x.hydro; h=calc(x.solar,x.wind,x.hydro,x.temperature,x.humidity,x.electrolyzer_efficiency); rows=[]
    for hour in range(1,25):
        factor=.78+.18*((hour%8)/7); rows.append({'hour':hour,'renewable':round(base*factor,2),'hydrogen':round(h*factor,2)})
    return {'forecast':rows}
@app.post('/api/what-if')
def what_if(x:Input):
    base=calc(x.solar,x.wind,x.hydro,x.temperature,x.humidity,x.electrolyzer_efficiency); scenario=calc(x.solar*1.15,x.wind*1.08,x.hydro,x.temperature,x.humidity,min(.95,x.electrolyzer_efficiency+.08)); gain=round((scenario-base)/base*100,1) if base else 0
    return {'current_hydrogen':round(base,2),'scenario_hydrogen':round(scenario,2),'hydrogen_improvement':gain,'current_efficiency':round(x.electrolyzer_efficiency*100,1),'scenario_efficiency':round(min(.95,x.electrolyzer_efficiency+.08)*100,1),'carbon_saving':carbon(scenario)}
