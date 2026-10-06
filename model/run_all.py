#!/usr/bin/env python3
"""Run local-only exact checks, all figures, and printed-number comparisons."""
from pathlib import Path
import re, argparse, concurrent.futures, importlib.metadata, json, os, subprocess, sys, time
from check_printed import extract,compare
ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',type=Path,help='Optional read-only Markdown reference; defaults to supplied numerical snapshot.')
    parser.add_argument('--jobs',type=int,default=3,choices=range(1,5),help='Concurrent local processes (default 3).')
    args=parser.parse_args();start=time.monotonic()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',MPLCONFIGDIR=str(ROOT/'.mplconfig'),SOURCE_DATE_EPOCH='1791216000',TZ='UTC')
    sources=['closed_form/characterise.py','closed_form/classification.py','independent/solver.py','independent/audit.py','independent/boundaries.py',
       'general/check_theory.py','extensions/check_extensions.py','institutions/solver.py','historical/model_extensions.py','historical/reserve_checks.py','historical/consolidation.py','phase/fig_cases.py','region/fig_region.py']
    def run(path):
        then=time.monotonic();p=ROOT/path
        cwd=p.parent if path=='region/fig_region.py' else ROOT
        result=subprocess.run([sys.executable,str(p)],cwd=cwd,env=env,text=True,capture_output=True,timeout=900)
        if path=='historical/reserve_checks.py' and result.returncode==0:
            nums=re.search(r'region points (\d+) \| shared pattern holds (\d+) \| earmark pattern holds (\d+) \| earmark==predicted threshold (\d+)',result.stdout)
            if not nums:raise RuntimeError('Reserve numeric receipt missing')
            (ROOT/'historical/reserve_results.json').write_text(json.dumps(dict(zip(('region_points','shared_holds','reserve_holds','threshold_matches'),map(int,nums.groups()))),indent=2)+'\n')
        # Retain failure diagnostics only, not copies of routine source stdout.
        return dict(file=path,exit_code=result.returncode,seconds=round(time.monotonic()-then,3),
          diagnostic=(result.stderr+result.stdout)[-5000:] if result.returncode else '',
          warnings=result.stderr.strip().splitlines())
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        runs=list(pool.map(run,sources))
    failures=[r for r in runs if r['exit_code']]
    expected=extract(args.reference) if args.reference else json.loads((ROOT/'printed_values.json').read_text())
    report=compare(expected) if not failures else dict(checks=[],mismatches=[],absent_from_reference=[],scope='Comparison skipped because a source check failed.')
    if not failures:
        table2=json.loads((ROOT/'institutions/RESULTS.json').read_text())
        if table2['failures']:failures.append(dict(file='institutions/solver.py',diagnostic=table2['failures']))
    receipt=dict(status='FAILED' if failures or report['mismatches'] else 'ARITHMETIC_PASS_WITH_REFERENCE_GAPS' if report['absent_from_reference'] else 'PASS',
      source_failures=failures,runs=runs,comparison=report,reference_sha256=expected['sha256'],
      seconds=round(time.monotonic()-start,3),software={'python':sys.version.split()[0],**{k:importlib.metadata.version(k) for k in ('numpy','matplotlib','shapely')}},
      exit_policy='1: computational failure or numerical mismatch; 2: all arithmetic passed but required objects absent from reference; 0: complete agreement.')
    (ROOT/'results.json').write_text(json.dumps(receipt,indent=2)+'\n')
    checks=report['checks'];lines=['# Replication checks','',f"Status: {receipt['status']}",f"Printed numerical comparisons: {len(checks)}; mismatches: {len(report['mismatches'])}.",'',
       '## Every mismatch','']
    lines += [json.dumps(r) for r in report['mismatches']] or ['None.']
    lines += ['', '## Required objects absent from the specified reference','']+[f'- {x}' for x in report['absent_from_reference']]
    lines += ['', '## Failed source checks','']+[json.dumps(r) for r in failures]
    lines += ['', '## Numerical comparison register','', '| Item | Reference line | Recomputed | Printed | Status |','|---|---|---|---|---|']
    lines += [f"| {r['item']} | {r['line']} | {', '.join(r['actual'])} | {', '.join(r['printed'])} | {r['status']} |" for r in checks]
    (ROOT/'CHECKS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','seconds','reference_sha256')},indent=2))
    print('comparisons',len(checks),'mismatches',len(report['mismatches']),'failed source checks',len(failures),flush=True)
    return 1 if failures or report['mismatches'] else 2 if report['absent_from_reference'] else 0
if __name__=='__main__':raise SystemExit(main())
