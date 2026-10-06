"""Extract only numerical expectations and hashes from a read-only reference.
No manuscript, prose, identity, literature or empirical record is copied.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from dataclasses import replace
import ast, types, hashlib, importlib.util, json, re, sys
ROOT=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def definitions(name,path):
    module=types.ModuleType(name);sys.modules[name]=module
    tree=ast.parse((ROOT/path).read_text())
    nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.ClassDef,ast.FunctionDef))]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(ROOT/path),'exec'),module.__dict__)
    return module

def number(s):
    s=re.sub(r'\[\[AUTHOR:.*?\]\]','',s).replace('−','-').replace('–','-')
    # Remove math delimiters and thousands separators.
    s=s.replace('$','').replace(',','')
    found=re.findall(r'(?<![A-Za-z_])[-+]?\d+(?:\.\d+)?(?:/\d+)?',s)
    return [str(Q(n)) for n in found]

def extract(path):
    text=Path(path).read_text();lines=text.splitlines();out={'sha256':hashlib.sha256(text.encode()).hexdigest(),'tables':{},'statements':{},'scalars':{}}
    titles={'1A':'**Table 1a.','1B':'**Table 1.','A1':'**Table A1.','A2':'**Table A2.','A3':'**Table A3.','A4A':'**Table A4.','A4B':'**Table A4, panel b.','A5':'**Table A5.'}
    aliases={'1B':('**Table 1, panel B.',), 'A4A':('**Table A4, panel A.',), 'A4B':('**Table A4, panel B.',)}
    for name,prefix in titles.items():
        prefixes=(prefix,)+aliases.get(name,())
        start=next((i for i,l in enumerate(lines) if l.startswith(prefixes)),None)
        if start is None:out['tables'][name]=dict(status='ABSENT');continue
        rows=[];begun=False
        for i in range(start+1,len(lines)):
            line=lines[i]
            if line.startswith('|'):
                begun=True
                if re.match(r'^\|[- :|]+\|$',line):continue
                rows.append(dict(line=i+1,cells=[number(c) for c in line.strip('|').split('|')]))
            elif begun:break
        out['tables'][name]=dict(status='PRESENT',rows=rows[1:])
    for name in ('Lemma 1','Theorem 1','Corollary 1','Theorem 2','Proposition 1'):
        matches=[(i+1,l) for i,l in enumerate(lines) if l.startswith('**'+name+' (')]
        out['statements'][name]=dict(status='PRESENT' if matches else 'ABSENT',line=matches[0][0] if matches else None,
          statement_line_sha256=hashlib.sha256(matches[0][1].encode()).hexdigest() if matches else None)
    out['phase_figure_in_reference']=any('fig_cases.' in l for l in lines if l.startswith('!['))
    patterns={
      'figure_areas':r'The three protected areas are (\d+(?:/\d+)?), (\d+(?:/\d+)?) and (\d+(?:/\d+)?)',
      'criteria_II':r'coincide at ([\d,]+) and differ at ([\d,]+)',
      'criteria_I':r"Grid I's ([\d,]+) points they differ at ([\d,]+)",
      'region_surplus':r'\(([\d,]+), ([\d,]+) and ([\d,]+) of 187 Grid II points',
      'topup_equal_higher':r'equal at ([\d,]+) and higher at ([\d,]+) of 187',
      'topup_nofallback_below':r'below joint rights at ([\d,]+) of 187',
      'transfer_points':r'holds at ([\d,]+) of the 187',
      'reserve_sample_points':r'checked in exact arithmetic on ([\d,]+) synthetic region points',
      'consolidation_comparisons':r'exact for the six institutions listed, ([\d,]+) comparisons',
      'legacy_comparison_states':r'matched it on ([\d,]+) random states',
    }
    for name,pat in patterns.items():
        m=re.search(pat,text)
        out['scalars'][name]=dict(status='PRESENT' if m else 'ABSENT',values=[str(Q(g.replace(',',''))) for g in m.groups()] if m else [],line=text[:m.start()].count('\n')+1 if m else None)
    return out

def protection(os):
    if os[0]['q']==0:return 'none'
    if os[1]['q']==0:return 'financing'
    if os[2]['q']==0:return 'refusal'
    if os[3]['q']==0:return 'joint'
    return 'unprotected'

def welfare(os):
    top=max(z['W'] for z in os)
    if top==os[0]['W']:return 'none'
    f=top==os[1]['W'];r=top==os[2]['W']
    return 'either' if f and r else 'financing' if f else 'refusal' if r else 'joint'

def compare(expected):
    # Core finite-action solver has no import side effects.
    independent=load('independent',Path('independent/solver.py'))
    historical=load('historical',Path('historical/model_extensions.py'))
    general=load('general',Path('general/check_theory.py'))
    robust=definitions('robust',Path('institutions/solver.py'))
    checks=[];mismatches=[];absent=[]
    def check(label,actual,printed,line=None):
        a=[str(Q(v)) for v in actual];p=[str(Q(v)) for v in printed]
        row=dict(item=label,actual=a,printed=p,line=line,status='MATCH' if a==p else 'MISMATCH');checks.append(row)
        if a!=p:mismatches.append(row)
    def cell(table,row,col,actual):
        tab=expected['tables'].get(table,{})
        if tab.get('status')!='PRESENT':absent.append(table);return
        r=tab['rows'][row];check(f'Table {table}, row {row+1}, column {col+1}',actual,r['cells'][col],r['line'])
    cases=((5,Q(1,2),4),(8,Q(1,2),Q(13,4)),(Q(19,2),1,Q(1,4)))
    for row,(B,k,O) in enumerate(cases):
        t=tuple(map(Q,(10,6,2,3,B,k,O)));os=independent.outcomes(t)
        assert independent.primitive_case(t)==('F','T','D')[row]
        for col,val in enumerate((B,k,O),1):cell('1A',row,col,[val])
        for i,z in enumerate(os):cell('1A',row,i+4,[z['W']])
    # Module executes its own exact Table 2 and institution checks once on load.
    saved=json.loads((ROOT/'institutions/RESULTS.json').read_text())
    w=saved['worked']
    for row,key in enumerate(('Table1_joint','Table1_topup_resident_borne','Table1_clause','Table1_outside_fallback','Table1_aligned','Table1_refusal_only')):
        cell('1B',row,3,[w[key]['q']]);cell('1B',row,4,[w[key]['W']])
    grid_actual={};scalar={}
    for name,Bs,Os in [('I',[Q(n,4) for n in range(16,25)],[Q(n,4) for n in range(33)]),('II',[Q(n,8) for n in range(24,65)],[Q(n,8) for n in range(73)])]:
        rows=[];prot=Counter();wel=Counter();preg=Counter();wreg=Counter();different=0;counts=Counter()
        for B in Bs:
            for O in Os:
                t=tuple(map(Q,(10,6,2,3,B,Q(1,2),O)));os=independent.outcomes(t)
                pr=protection(os);wc=welfare(os);inside=independent.prop2(t)
                prot[pr]+=1;wel[wc]+=1;different+=('none' if pr=='unprotected' else pr)!=wc
                if inside:
                    preg[pr]+=1;wreg[wc]+=1
                    delta=os[3]['W']+os[3]['profit']-os[0]['W']-os[0]['profit']
                    counts['low' if delta<0 else 'equal' if delta==0 else 'high']+=1
                    counts['transfer']+=O>Q(10)-B+Q(1,2)-Q(3,2)
                    hp=replace(historical.P(),B=B,a1=O+1)
                    _,top,nofb,clause=historical.topup_outcomes(hp)
                    counts['top_equal']+=top['W']==os[3]['W'];counts['top_higher']+=top['W']>os[3]['W']
                    counts['nofb_below']+=nofb['W']<os[3]['W']
                rows.append(os)
        grid_actual[name]=dict(n=len(rows),region=sum(preg.values()),protection=dict(prot),welfare=dict(wel),protection_in_region=dict(preg),welfare_in_region=dict(wreg),different=different,counts=dict(counts))
    for row,(name,lo,hi,omax,step) in enumerate((('I',4,6,8,Q(1,4)),('II',3,8,9,Q(1,8)))):
        g=grid_actual[name]
        cell('A1',row,1,[lo,hi]);cell('A1',row,2,[0,omax]);cell('A1',row,3,[step]);cell('A1',row,4,[g['n'],int((hi-lo)/step)+1,int(omax/step)+1]);cell('A1',row,5,[g['region']])
    for i,key in enumerate(('none','financing','refusal','joint','unprotected')):
        cell('A2',i,2,[grid_actual['I']['protection'].get(key,0)]);cell('A2',i,3,[grid_actual['I']['protection_in_region'].get(key,0)])
    for i,key in enumerate(('none','financing','refusal','either','joint')):
        cell('A2',5+i,2,[grid_actual['II']['welfare'].get(key,0)]);cell('A2',5+i,3,[grid_actual['II']['welfare_in_region'].get(key,0)])
    sample=json.loads((ROOT/'historical/model_extensions_results.json').read_text())
    schemes=list(sample['surplus_schemes'].values())
    for row,name in enumerate(('I','II')):
        g=grid_actual[name];cell('A3',row,1,[g['region']]);cell('A3',row,2,[g['counts']['low']]);cell('A3',row,3,[Q(str(round(100*g['counts']['low']/g['region'],1)))])
    cell('A3',2,3,[20])
    for row,s in enumerate(schemes[:2],3):
        cell('A3',row,1,[s['region']]);cell('A3',row,2,[s['lowers']]);cell('A3',row,3,[Q(str(round(100*s['lowers']/s['region'],1)))])
    base=historical.P();os=historical.all_alloc(base);plain=list(os.values())
    _,top,_,clause=historical.topup_outcomes(base)
    external=[historical.state(replace(base,k=Q(0)),1,d) for d in (0,1)]
    data=plain+[top]+external
    for row,z in enumerate(data):
        G=z['G']-(Q(1,2) if row>=5 else 0);outside=1 if row==4 else Q(1,2) if row>=5 else 0
        for col,val in enumerate((z['q'],z['W'],z['profit'],G,outside),1):cell('A4A',row,col,[val])
    # Accounting contrasts derived from actual continuation outcomes.
    t=tuple(map(Q,(10,6,2,3,5,Q(1,2),4)))
    built=independent.outcomes(t,build_tie=True)[0]
    joint=plain[3];none=plain[0]
    diff=lambda z,ref=none:(z['W']-ref['W'],z['profit']-ref['profit'])
    reserve_outcome=robust.solve(robust.P(),0,0,mode='reserve')
    rowsB=[[*diff(joint),0,joint['G']-none['G']],
      [joint['W']-built['W'],joint['profit']-built['profit'],0,joint['G']-built['W']-built['profit']],
      [*diff(clause),0,clause['G']-none['G']],
      [*diff(top),0,top['G']-none['G']],
      [top['W']+1-none['W'],top['profit']-none['profit'],-1,top['G']-none['G']],
      [external[1]['W']-none['W'],external[1]['profit']-none['profit'],-Q(1,2),external[1]['G']-Q(1,2)-none['G']],
      [reserve_outcome['W']-none['W'],reserve_outcome['profit']-none['profit'],0,reserve_outcome['G']-none['G']]]
    for row,vals in enumerate(rowsB):
        for col,val in enumerate(vals,1):cell('A4B',row,col,[val])
    # A5 uses existing source variants, plus fixed price caps in general solver.
    benchmark=general.P()
    source_results=json.loads((ROOT/'institutions/RESULTS.json').read_text())
    for row in range(6):
        if row in (3,4):
            zs=general.full(benchmark,cap=Q(9,2) if row==3 else Q(4));out=[(zs[i].q,zs[i].W) for i in (0,2,1,3)]
        elif row==5:
            zs=[general.eq(benchmark,1,d) for d in (0,0,1,1)];out=[(z.q,z.W) for z in zs]
        elif row in (1,2):
            zs=[robust.solve(robust.P(),f,d,mode='nash',beta=Q(1,2) if row==1 else Q(4,5)) for f,d in ((0,0),(1,0),(0,1),(1,1))];out=[(z['q'],z['W']) for z in zs]
        else:out=[(z['q'],z['W']) for z in plain]
        for col,vals in enumerate(out,1):cell('A5',row,col,vals)
    reserve=json.loads((ROOT/'historical/reserve_results.json').read_text())
    consolidation=json.loads((ROOT/'historical/results.json').read_text())
    scalar['reserve_sample_points']=[reserve['region_points']]
    scalar['consolidation_comparisons']=[sum(v for k,v in consolidation['checks'].items() if not k.startswith('continuous_'))+consolidation['checks']['continuous_baseline']]
    scalar['figure_areas']=[Q(v) for v in saved['figure_areas'].values()]
    scalar['criteria_II']=[2993-grid_actual['II']['different'],grid_actual['II']['different']]
    scalar['criteria_I']=[grid_actual['I']['n'],grid_actual['I']['different']]
    scalar['region_surplus']=[grid_actual['II']['counts'][k] for k in ('low','equal','high')]
    scalar['topup_equal_higher']=[grid_actual['II']['counts'][k] for k in ('top_equal','top_higher')]
    scalar['topup_nofallback_below']=[grid_actual['II']['counts']['nofb_below']]
    scalar['transfer_points']=[grid_actual['II']['counts']['transfer']]
    scalar['legacy_comparison_states']=[sample['crosscheck_vs_author_program(n_states,n_mismatch)'][0]]
    for name,actual in scalar.items():
        e=expected['scalars'][name]
        if e['status']=='PRESENT':check(name,actual,e['values'],e['line'])
        elif name != 'consolidation_comparisons':absent.append(name)
    for name,e in expected['statements'].items():
        if e['status']=='ABSENT':absent.append(name)
    if not expected['phase_figure_in_reference']:absent.append('phase figure')
    # Supplemental objects requested by the brief, not asserted as printed in reference.
    z=replace(benchmark,B=Q(8),k=Q(5),a1=Q(9,2),r1=Q(0));m=general.full(z)
    assert m[2].W==Q(-1,2) and m[2].q==0 and m[3].W==0 and m[3].q==1
    z=replace(benchmark,a1=Q(17,4));mon=general.full(z)[3];cost=general.full(z,cap=Q(4))[3]
    assert mon.W==Q(11,4) and cost.W==cost.G==3 and cost.q==1
    return dict(checks=checks,mismatches=mismatches,absent_from_reference=sorted(set(absent)),grids=grid_actual,
      supplemental_examples={'historical_consolidation_comparisons':scalar['consolidation_comparisons'][0], 'welfare_financing_only':str(m[2].W),'welfare_joint':str(m[3].W),'price_monopoly':str(mon.W),'price_cost':str(cost.W)},
      scope='Model arithmetic, figures and synthetic tables. Documentary counts and literature dates are not solver outputs and are excluded.')
