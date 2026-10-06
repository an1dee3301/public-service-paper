#!/usr/bin/env python3
"""phase: exact affine-cell phase diagrams, not a raster classification grid.
Run with Python containing matplotlib and shapely (local: /opt/homebrew/bin/python3.11).
All output and Matplotlib cache stay beside this script. Lead code is read-only;
only the cells() definition is extracted, never its top-level simulation/run().
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import ast
import hashlib
import json
import os
import sys

HERE = Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR'] = str(HERE / '.mplconfig')
sys.dont_write_bytecode = True
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PatchPolygon, Patch
from shapely.geometry import Polygon
from shapely.ops import unary_union

V, c, b, h = map(Q, (10, 6, 2, 3))
HALF = Q(1, 2)
LEAD = HERE.parent / 'closed_form' / 'classification.py'
source = LEAD.read_text()
tree = ast.parse(source)
node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'cells')
namespace = {'F': Q}
exec(compile(ast.Module(body=[node], type_ignores=[]), str(LEAD), 'exec'), namespace)
lead_cells = namespace['cells']

# source is optional while it is running; use its independent primitive formula
# when its completion record is present, without importing output-writing code.
J35_DIR = HERE.parent / 'independent'
j35_case = None
j35_hash = None
if (J35_DIR/'solver.py').exists():
    j35_text = (J35_DIR/'solver.py').read_text()
    j35_node = next(n for n in ast.parse(j35_text).body
                   if isinstance(n, ast.FunctionDef) and n.name == 'primitive_case')
    j35_ns = {}
    exec(compile(ast.Module(body=[j35_node], type_ignores=[]), str(J35_DIR/'solver.py'), 'exec'), j35_ns)
    j35_case = j35_ns['primitive_case']
    j35_hash = hashlib.sha256(j35_text.encode()).hexdigest()
COMPARISONS = Counter()


def continuation(B, k, O, x, resident_accepts):
    """Independent enumeration from region 5.2; compares offers, not slack formulas."""
    cash, alternative = B-k*x, O if x else Q(0)
    offers = []
    for q in (0, 1):
        p = min(cash, V-alternative-h*q*resident_accepts)
        profit = p-c+b*q
        if p >= 0 and profit >= 0:
            offers.append((profit, -q, p, q))
    if not offers:
        return ('f', alternative-k*x, alternative-k*x, None)
    _, _, p, q = max(offers)
    A = V-p-k*x
    return ('H' if q else 'N', A, A-h*q, p)


def independent_pattern(B, k, O):
    out = []
    for resident_invests, resident_accepts in ((0, 0), (1, 0), (0, 1), (1, 1)):
        states = [continuation(B, k, O, x, resident_accepts) for x in (0, 1)]
        payoff_index = 2 if resident_invests else 1
        x = int(states[1][payoff_index] > states[0][payoff_index])
        out.append((states[x][0], x, states[x]))
    return out


def classify(B, k, O):
    if k <= 0 or B < k:
        return 'X'
    pattern = independent_pattern(B, k, O)
    harmful = [p[0] == 'H' for p in pattern]
    D, F, T, drain, types = lead_cells(V, c, b, h, B, k, O)
    onlyjoint = harmful == [True, True, True, False]
    assert onlyjoint == (D and (F or T or drain)), (B, k, O, pattern)
    COMPARISONS['lead_in_scope'] += 1
    if j35_case is not None:
        got_j35 = j35_case((V, c, b, h, B, k, O))
        expected_j35 = ('F' if F else ('T' if T else 'D')) if onlyjoint else None
        assert got_j35 == expected_j35, (B, k, O, got_j35, expected_j35)
        COMPARISONS['independent_in_scope'] += 1
    # Also check the lead's two resident-acceptance continuation types directly.
    assert types == [continuation(B, k, O, x, 1)[0] for x in (0, 1)]
    if all(harmful):
        return 'H'
    if not any(harmful):
        return 'I'
    if onlyjoint:
        assert sum((F, T, drain)) == 1
        return 'F' if F else ('T' if T else 'D')
    if not harmful[2]:
        return 'R'
    if not harmful[1]:
        return 'M'
    raise AssertionError(('unclassified', B, k, O, pattern))


def closed_A(B, O):
    """Simplified primitive partition at k=1/2, including exact tie ownership."""
    if B < HALF:
        return 'X'
    if B < 4 or (4 <= B < Q(9, 2) and O > Q(21, 2)-B) or (B >= Q(9, 2) and O > 6):
        return 'I'
    if Q(9, 2) <= B < Q(13, 2) and 3 < O <= Q(21, 2)-B:
        return 'F'
    if (Q(13, 2) <= B <= 7 and Q(19, 2)-B <= O <= Q(21, 2)-B) or (7 < B < 9 and Q(19, 2)-B <= O <= Q(7, 2)):
        return 'T'
    if 9 <= B < Q(19, 2) and O < Q(19, 2)-B:
        return 'D'
    if B >= 9 or (4 <= B < 9 and O > Q(21, 2)-min(B, 7)):
        return 'R'
    if 4 <= B < Q(9, 2) and Q(15, 2)-B < O <= Q(21, 2)-B:
        return 'M'
    return 'H'


def closed_B(k, O):
    """Simplified primitive partition at B=8, including exact tie ownership."""
    if k <= 0 or k > 8:
        return 'X'
    if (k > 4 or O > 6) and O > k+3:
        return 'I'
    if (1 < k <= 2 and 4 < O <= k+3) or (2 < k <= 4 and max(Q(3), k) < O <= min(Q(6), k+3)):
        return 'F'
    if k <= 2 and 1+k <= O <= min(Q(4), 3+k):
        return 'T'
    if O > k+3:
        return 'R'
    if (k > 4 or O > 6) and k-1 < O <= k+3:
        return 'M'
    return 'H'


# Rational half-plane clipping: every vertex is an exact line intersection.
def signed(point, line):
    a, b_, d = line
    return a*point[0]+b_*point[1]-d


def clip(poly, line, positive):
    result = []
    for start, end in zip(poly, poly[1:]+poly[:1]):
        f, g = signed(start, line), signed(end, line)
        inside_f = f >= 0 if positive else f <= 0
        inside_g = g >= 0 if positive else g <= 0
        if inside_f:
            result.append(start)
        if inside_f != inside_g:
            t = f/(f-g)
            result.append((start[0]+t*(end[0]-start[0]), start[1]+t*(end[1]-start[1])))
    # Remove consecutive duplicates at vertices on the clipping line.
    cleaned = []
    for p in result:
        if not cleaned or p != cleaned[-1]:
            cleaned.append(p)
    if len(cleaned) > 1 and cleaned[0] == cleaned[-1]:
        cleaned.pop()
    return cleaned


def area(poly):
    if len(poly) < 3:
        return Q(0)
    return abs(sum(p[0]*q[1]-q[0]*p[1] for p, q in zip(poly, poly[1:]+poly[:1])))/2


def arrangement(rect, lines):
    x0, x1, y0, y1 = map(Q, rect)
    polys = [[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
    for line in lines:
        new = []
        for poly in polys:
            values = [signed(p, line) for p in poly]
            if min(values) < 0 < max(values):
                for sign in (False, True):
                    piece = clip(poly, line, sign)
                    if area(piece):
                        new.append(piece)
            else:
                new.append(poly)
        polys = new
    assert sum(map(area, polys)) == (x1-x0)*(y1-y0)
    return polys


A_LINES = ([(Q(1), Q(0), Q(t)) for t in (HALF, 4, Q(9,2), Q(13,2), 7, 9, Q(19,2))]
           + [(Q(0), Q(1), Q(t)) for t in (3, Q(7,2), 4, 6)]
           + [(Q(1), Q(1), Q(t)) for t in (Q(15,2), Q(19,2), Q(21,2))])
B_LINES = ([(Q(1), Q(0), Q(t)) for t in (0, 1, 2, 3, 4)]
           + [(Q(0), Q(1), Q(t)) for t in (3, 4, 6)]
           + [(Q(-1), Q(1), Q(t)) for t in (-1, 0, 1, 2, 3)])
RECT_A, RECT_B = (0, 12, 0, 8), (0, 6, 0, 10)


def build_panel(panel, rect, lines):
    polys = arrangement(rect, lines)
    groups = {}
    serial = []
    checks = 0
    for poly in polys:
        centre = tuple(sum(p[j] for p in poly)/len(poly) for j in (0, 1))
        x, O = centre
        B, k = (x, HALF) if panel == 'A' else (Q(8), x)
        label = classify(B, k, O)
        primitive = closed_A(x, O) if panel == 'A' else closed_B(x, O)
        assert label == primitive, (panel, centre, label, primitive)
        # Four strict interior points detect accidental missed break lines.
        for vertex in poly:
            z = tuple((centre[j]+vertex[j])/2 for j in (0, 1))
            zB, zk = (z[0], HALF) if panel == 'A' else (Q(8), z[0])
            assert classify(zB, zk, z[1]) == label, (panel, poly, z)
            checks += 1
        groups.setdefault(label, []).append(Polygon([(float(x), float(y)) for x, y in poly]))
        serial.append({'class': label, 'vertices': [[str(x), str(y)] for x, y in poly]})
    # This dissolves internal affine-cell edges only; it never interpolates data.
    merged = {key: unary_union(value) for key, value in groups.items()}
    return merged, serial, checks


STYLES = {
    'H': ('0.92', 'xx', 'H: harmful under all four allocations'),
    'R': ('1.0', '//', 'R: refusal alone suffices'),
    'I': ('1.0', '', 'I: no harmful trade under any allocation'),
    'F': ('0.80', '..', 'F: joint rights only; fallback used'),
    'T': ('1.0', '\\\\', 'T: joint rights only; harmless incumbent'),
    'D': ('0.68', '++', 'D: joint rights only; no spending'),
    'M': ('0.96', '--', 'M: financing alone suffices (joint may fail)'),
    'X': ('0.85', 'oo', 'Outside scope: building infeasible'),
}


def draw_regions(ax, merged):
    for key, geom in merged.items():
        fc, hatch, _ = STYLES[key]
        parts = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
        for part in parts:
            assert not part.interiors, ('unexpected hole', key)
            patch = PatchPolygon(list(part.exterior.coords), facecolor=fc, edgecolor='0.28',
                                 hatch=hatch, linewidth=0.65, zorder=1)
            ax.add_patch(patch)


def label(ax, text, x, y):
    ax.text(x, y, text, ha='center', va='center', fontsize=12, weight='bold',
            bbox=dict(facecolor='white', edgecolor='none', pad=1.7), zorder=5)


def validate_lattices():
    counts, n = {}, 0
    for panel in ('A', 'B'):
        tally = Counter()
        xmax, ymax = (12, 8) if panel == 'A' else (8, 12)
        for i in range(xmax*8+1):
            for j in range(ymax*8+1):
                x, O = Q(i, 8), Q(j, 8)
                B, k = (x, HALF) if panel == 'A' else (Q(8), x)
                got = classify(B, k, O)
                expected = closed_A(x, O) if panel == 'A' else closed_B(x, O)
                assert got == expected, (panel, x, O, got, expected)
                tally[got] += 1
                n += 1
        counts[panel] = dict(tally)
    # Non-lattice values and exact epsilon attacks on every arrangement boundary.
    attacks = 0
    for panel, lines, rect in (('A', A_LINES, RECT_A), ('B', B_LINES, RECT_B)):
        for a, b_, d in lines:
            for t in range(1, 60):
                if b_:
                    x = Q(t, 7)
                    O = (d-a*x)/b_
                else:
                    x, O = d/a, Q(t, 7)
                for eps in (-Q(1, 1009), Q(0), Q(1, 1009)):
                    xx, yy = (x, O+eps) if b_ else (x+eps, O)
                    if not (rect[0] <= xx <= rect[1] and rect[2] <= yy <= rect[3]):
                        continue
                    B, k = (xx, HALF) if panel == 'A' else (Q(8), xx)
                    expected = closed_A(xx, yy) if panel == 'A' else closed_B(xx, yy)
                    assert classify(B, k, yy) == expected
                    attacks += 1
    return {'lattice_points': n, 'counts': counts, 'boundary_attacks': attacks, 'mismatches': 0}


def main():
    checks = validate_lattices()
    mergedA, cellsA, interiorA = build_panel('A', RECT_A, A_LINES)
    mergedB, cellsB, interiorB = build_panel('B', RECT_B, B_LINES)
    assert 'D' in mergedA and 'D' not in mergedB
    examples = {}
    for name, B, k, O in (('worked F', Q(5), HALF, Q(4)), ('note T', Q(8), HALF, Q(3)), ('note D', Q(9), HALF, Q(0))):
        examples[name] = {'class': classify(B, k, O), 'allocations': [
            {'outcome': r[0], 'build': r[1], 'agency': str(r[2][1]),
             'residents': str(r[2][2]), 'price': str(r[2][3])} for r in independent_pattern(B, k, O)]}
    checks.update({'affine_cells': {'A': len(cellsA), 'B': len(cellsB)},
                   'interior_checks': interiorA+interiorB, 'examples': examples,
                   'lead_source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                   'independent_completed_comparison': j35_case is not None,
                   'independent_solver_sha256': j35_hash, 'function_comparisons': dict(COMPARISONS),
                   'method': 'Exact Fraction half-plane intersections; lead cells versus independent offer enumeration. No pixel grid used to draw.'})
    (HERE/'CHECKS.json').write_text(json.dumps(checks, indent=2)+'\n')
    (HERE/'EXACT_CELLS.json').write_text(json.dumps({'A': cellsA, 'B': cellsB}, indent=2)+'\n')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'mathtext.fontset': 'dejavusans',
                         'pdf.fonttype': 42, 'ps.fonttype': 42, 'hatch.linewidth': 0.45,
                         'axes.spines.top': False, 'axes.spines.right': False, 'savefig.dpi': 300})
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 6.7))
    fig.subplots_adjust(left=0.06, right=0.98, top=0.91, bottom=0.27, wspace=0.20)
    for ax, merged, rect in zip(axes, (mergedA, mergedB), (RECT_A, RECT_B)):
        draw_regions(ax, merged)
        ax.set_xlim(rect[0], rect[1]); ax.set_ylim(rect[2], rect[3])
        ax.set_ylabel(r'Net fallback value $O_1$')
        ax.tick_params(direction='out', length=3)
    ax = axes[0]
    ax.set_title(r'(a) Budget and fallback value: $k=1/2$', loc='left', fontsize=12)
    ax.set_xlabel(r'Budget $B$')
    ax.set_xticks([0, 2, 4, 6, 8, 10, 12]); ax.set_yticks([0, 2, 4, 6, 8])
    label(ax, 'H', 6.0, 1.0); label(ax, 'I', 2.1, 4.6)
    label(ax, 'R', 10.2, 3.1); label(ax, 'F', 5.1, 4.9); label(ax, 'T', 8.0, 2.4)
    for text, pos, target in (('M', (3.05, 6.9), (4.2, 5.3)), ('D', (10.5, 0.9), (9.13, 0.17))):
        ax.annotate(text, xy=target, xytext=pos, weight='bold', fontsize=12,
                    bbox=dict(facecolor='white', edgecolor='none', pad=1.5),
                    arrowprops=dict(arrowstyle='->', color='black', lw=0.9), zorder=6)
    # Closure of Corollary 1: the actual corollary region is its strict interior.
    p2 = [(4.5, 3), (6, 3), (6, 4.5), (4.5, 6), (4.5, 3)]
    ax.plot(*zip(*p2), color='black', linewidth=1.9, linestyle=(0, (2.5, 1.8)), zorder=4)
    ax.annotate('Corollary 1\n(strict interior)', xy=(5.95, 4.1), xytext=(6.45, 6.55),
                fontsize=9, ha='left', va='center', bbox=dict(facecolor='white', edgecolor='none', pad=2),
                arrowprops=dict(arrowstyle='->', lw=0.8, color='black'), zorder=6)
    ax.plot(5, 4, 'k*', markersize=12, zorder=7)
    ax.annotate('Worked example\n(5, 4)', xy=(5, 4), xytext=(2.8, 2.6), fontsize=9,
                bbox=dict(facecolor='white', edgecolor='none', pad=2),
                arrowprops=dict(arrowstyle='->', lw=0.8, color='black'), zorder=6)
    ax = axes[1]
    ax.set_title(r'(b) Investment cost and fallback value: $B=8$', loc='left', fontsize=12)
    ax.set_xlabel(r'Investment cost $k$ (positive)')
    ax.set_xticks(range(7)); ax.set_yticks(range(0, 11, 2))
    label(ax, 'I', 1.0, 8.3); label(ax, 'R', 1.5, 5.4)
    label(ax, 'M', 5.1, 6.6); label(ax, 'H', 4.8, 1.5)
    label(ax, 'F', 2.55, 4.5); label(ax, 'T', 0.65, 2.65)
    ax.text(0.97, 0.97, 'No Case D on this slice', ha='right', va='top', transform=ax.transAxes,
            fontsize=9, bbox=dict(facecolor='white', edgecolor='black', linewidth=0.5, pad=3), zorder=6)
    ax.plot(HALF, 3, 'ko', markersize=4, zorder=7)
    ax.annotate('Note’s T example', xy=(0.5, 3), xytext=(0.15, 4.35), fontsize=8.5,
                bbox=dict(facecolor='white', edgecolor='none', pad=1.5),
                arrowprops=dict(arrowstyle='->', lw=0.75, color='black'), zorder=6)
    handles = [Patch(facecolor=STYLES[key][0], edgecolor='0.28', hatch=STYLES[key][1],
                     label=STYLES[key][2]) for key in ('H', 'R', 'I', 'M', 'F', 'T', 'D', 'X')]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.51, 0.065), ncol=2,
               frameon=False, fontsize=9, handlelength=2.2, handleheight=1.4, columnspacing=2.1)
    fig.text(0.06, 0.025, r'$V=10,\ c=6,\ b=2,\ h=3$; $F=O_0=0$; affordable alternative; region tie rules. '
             'Exact line boundaries; tie rules follow the reference.', fontsize=9)
    for suffix in ('pdf', 'eps', 'png'):
        fig.savefig(HERE/f'fig_cases.{suffix}', facecolor='white', metadata=({'Creator': 'phase fig_cases.py'} if suffix in ('pdf', 'eps') else None))
    plt.close(fig)
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
