import os, re, warnings, sys
import pandas as pd, openpyxl
warnings.filterwarnings('ignore')
ROOT='/storage/scratch1/4/nbawana3/furnace-project/data/raw/Tests_Foyers_unzipped/Tests_Foyers'
OUT='/storage/scratch1/4/nbawana3/furnace-project/data/processed'
os.makedirs(OUT, exist_ok=True)
RE_FMT=re.compile(r'\b(HS|HM|HL|CS|CL)\b',re.I)
RE_CPA=re.compile(r'CPA\s*([1-4])',re.I)
def pmeta(p):
    r=p.replace(ROOT+'/','')
    parts=r.split('/'); top=parts[0]; tl=top.lower()
    brand='Unknown'; country='Togo'; mat='clay'
    if 'toyola' in tl or 'cathy' in tl or 'fiches' in tl: brand='Toyola'
    elif 'sequoia' in tl: brand='SEQUOIA-tested'; mat='ceramic'
    elif 'ghana' in tl: brand='Ghana-MAN'; country='Ghana'
    elif 'suraj' in tl: brand='Toyola-Nigeria'; country='Nigeria'
    elif 'prakash' in tl: brand='Prakash'
    if 'optima' in p.lower() or 'tchatcha' in p.lower() or 'farm commod' in p.lower(): mat='ceramic'
    fmt=None
    mC=RE_CPA.search(r)
    if mC: fmt='CPA'+mC.group(1)
    else:
        for c in parts:
            m=RE_FMT.search(c)
            if m: fmt=m.group(1).upper(); break
    yr=None
    yfm=re.search(r'(HS|HM|HL|CS|CL)\s*(20\d{2})',os.path.basename(p),re.I)
    if yfm: yr=int(yfm.group(2))
    return dict(campaign=top, brand=brand, format=fmt, sale_year=yr, material=mat, country_make=country, src_path=r)
PHASES=['cold','hot','simmer']
def parse_wbt(p):
    try: wb=openpyxl.load_workbook(p,data_only=True,read_only=True)
    except Exception: return None
    if 'General Information' not in wb.sheetnames or 'Results' not in wb.sheetnames:
        wb.close(); return None
    md={}
    try:
        for row in wb['General Information'].iter_rows(min_row=1,max_row=25,max_col=4,values_only=True):
            if not row or row[0] is None: continue
            lab=str(row[0]).lower(); val=row[1] if len(row)>1 else None
            if 'tester' in lab: md['tester']=val
            elif 'test year' in lab: md['test_year']=val
            elif 'test location' in lab: md['location']=val
            elif 'manufactured by' in lab: md['manufacturer']=val
            elif 'stove type' in lab or 'stove model' in lab: md['stove_model']=val
            elif 'altitude' in lab or 'elevation' in lab: md['altitude']=val
        rows=list(wb['Results'].iter_rows(min_row=1,max_row=60,max_col=8,values_only=True))
    finally:
        wb.close()
    pidx=-1; phase=None; out=[]
    for r in rows:
        if not r or len(r)<2: continue
        c1=str(r[1]).lower() if r[1] else ''
        if 'high power' in c1 or 'low power' in c1:
            pidx+=1
            phase=PHASES[pidx] if pidx<3 else None
            continue
        if phase is None: continue
        if 'temp-corrected' in c1 or 'temp corrected' in c1: continue
        mn=None
        if 'thermal efficiency' in c1: mn='eff'
        elif 'firepower' in c1: mn='fp'
        elif 'burning rate' in c1: mn='br'
        elif 'specific fuel' in c1: mn='sfc'
        if mn is None: continue
        for i,lab in [(3,'T1'),(4,'T2'),(5,'T3'),(6,'T4'),(7,'avg')]:
            if i>=len(r): continue
            v=r[i]
            try: v=float(v) if v not in (None,'') else None
            except: v=None
            if v is None: continue
            out.append(dict(phase=phase,metric=mn,replicate=lab,value=v,**md))
    return out
files=[]
for root,_,fs in os.walk(ROOT):
    for fn in fs:
        if fn.endswith('.xlsx') and not fn.startswith('~'): files.append(os.path.join(root,fn))
print(f'Scanning {len(files)} xlsx files...', flush=True)
recs=[]; n_wbt=0; n_other=0; n_wbt_empty=0
for i,p in enumerate(files):
    if i%25==0: print(f' {i}/{len(files)} wbt={n_wbt} empty={n_wbt_empty}', flush=True)
    res=parse_wbt(p)
    if res is None: n_other+=1; continue
    if not res: n_wbt_empty+=1; continue
    pm=pmeta(p)
    for r in res: r.update(pm); recs.append(r)
    n_wbt+=1
print(f'WBT={n_wbt}, WBT-empty={n_wbt_empty}, non-WBT={n_other}', flush=True)
df=pd.DataFrame(recs)
print(f'long shape: {df.shape}', flush=True)
df.to_csv(os.path.join(OUT,'wbt_long_mvp.csv'),index=False)
print(f'wrote {OUT}/wbt_long_mvp.csv', flush=True)
print('counts by campaign,format:'); print(df.groupby(['campaign','format'],dropna=False).size().head(40).to_string())
print('\nphase x metric counts:'); print(df.groupby(['phase','metric']).size().to_string())
