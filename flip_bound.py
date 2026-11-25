"""Checks for the one-flip argument (README item 9).

Setting: F is a k-CNF (k distinct variables per clause), every literal occurs at most
k-1 times, N(x) = number of clauses falsified by x.

Step 1. If F is unsatisfiable, #{x : N(x) = 1} >= 2^n - sum_x (N(x)-1) = 2^n (2 - m/2^k).
Step 2. If N(x) = 1 with C the falsified clause, flipping any variable v of C must falsify
        a clause D containing the complement of C's literal on v whose other literals are
        false at x ("v is blocked at x").  So x lies in B_C = {x in Q_C : every variable of
        C is blocked}, where Q_C is the set of assignments falsifying C.
Step 3. beta_C = |B_C| / |Q_C| <= 5/8, 17/32, 7/16 for k = 4, 5, 6 (README item 9).
Together: m * beta / 2^k >= 2 - m/2^k, i.e. m >= 2^(k+1) / (1 + beta).

This script checks Step 2 by brute force on random unsatisfiable formulas (no literal
bound needed for Step 2), checks the Step 3 bound on random literal-bounded formulas,
and prints the resulting clause bounds and vertex ranges.
"""
import itertools
import random
from fractions import Fraction as Fr
from math import ceil, floor


def var(l):
    return l if l >= 0 else ~l


def false_at(l, x):
    # literal v is false when x_v = 0; literal ~v is false when x_v = 1
    return ((x >> var(l)) & 1) == (0 if l >= 0 else 1)


def random_formula(n, m, k, max_lit, rng):
    for _ in range(500):
        occ, F = {}, []
        for _ in range(m):
            for _ in range(300):
                vs = rng.sample(range(n), k)
                c = tuple(sorted(v if rng.random() < 0.5 else ~v for v in vs))
                if max_lit is None or all(occ.get(l, 0) < max_lit for l in c):
                    for l in c:
                        occ[l] = occ.get(l, 0) + 1
                    F.append(c)
                    break
            else:
                break
        if len(F) == m:
            return F
    return None


def blockers(F, C):
    """For each literal l of C: the clauses containing ~l and no other complement of C."""
    Cs = set(C)
    out = []
    for l in C:
        bl = []
        for D in F:
            if ~l in D and not any(~t in D for t in C if t != l):
                bl.append([t for t in D if t != ~l and t not in Cs])   # free literals of D
        out.append(bl)
    return out


def beta(F, C):
    bl = blockers(F, C)
    free_vars = sorted({var(t) for b in bl for D in b for t in D})
    idx = {v: i for i, v in enumerate(free_vars)}
    good = 0
    for z in range(1 << len(free_vars)):
        x = 0
        for v, i in idx.items():
            if (z >> i) & 1:
                x |= 1 << v
        if all(any(all(false_at(t, x) for t in D) for D in b) for b in bl):
            good += 1
    return Fr(good, 1 << len(free_vars))


def check_step2(rng, trials=40):
    """Every point with exactly one falsified clause lies in B_C (unsatisfiable formulas)."""
    done = 0
    while done < trials:
        n, k = rng.randint(6, 9), 4
        F = random_formula(n, rng.randint(14 * n, 22 * n), k, None, rng)
        N = [sum(all(false_at(l, x) for l in c) for c in F) for x in range(1 << n)]
        if min(N) == 0:
            continue
        for x in range(1 << n):
            if N[x] == 1:
                C = next(c for c in F if all(false_at(l, x) for l in c))
                for l in C:
                    y = x ^ (1 << var(l))
                    assert N[y] >= 1
                    # the clauses falsified at y are exactly the active blockers of l
                    act = [D for D in F if ~l in D and all(false_at(t, x) for t in D if t != ~l)]
                    assert len(act) == N[y]
        done += 1
    return done


def main():
    rng = random.Random(7)
    print("Step 2 (inclusion N=1 points in B_C) verified on", check_step2(rng), "random unsatisfiable 4-CNFs")
    bounds = {4: Fr(5, 8), 5: Fr(17, 32), 6: Fr(7, 16)}
    for k, b in bounds.items():
        worst = Fr(0)
        for _ in range({4: 400, 5: 150, 6: 60}[k]):
            n = rng.randint(2 * k, 3 * k + 2)
            m = rng.randint(n, (2 * (k - 1) * n) // k)
            F = random_formula(n, m, k, k - 1, rng)
            if F is None:
                continue
            for C in F:
                bl = blockers(F, C)
                if len({var(t) for b_ in bl for D in b_ for t in D}) <= 16:
                    worst = max(worst, beta(F, C))
        assert worst <= b
        print(f"k={k}: largest beta_C seen on random literal-bounded formulas = {worst} "
              f"({float(worst):.4f}); proved bound {b} ({float(b):.4f})")
    exec(open("ranges.py").read().split("for delta, gupta, ours")[0], globals())
    for k, b in bounds.items():
        mmin = Fr(2 ** (k + 1)) / (1 + b)
        m0 = floor(mmin) + 1 if mmin.denominator == 1 else ceil(mmin)
        print(f"k={k}: unsatisfiable needs m >= {float(mmin):.3f}, so every formula with at most "
              f"{m0 - 1} clauses is satisfiable; degree {k}: all graphs with n <= {max_safe_n(k, m0 - 1)}")


if __name__ == "__main__":
    main()
