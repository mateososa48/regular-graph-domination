"""Numerical sanity checks for the counting identities used in README items 8 and 9.

N(x) = number of clauses falsified by the assignment x.

1. Second moment:  sum_x N(N-1) = sum over ordered pairs of different, non-clashing
   clauses (C, C') of 2^(n - |C u C'|)   (|C u C'| = number of distinct literals).
2. Parity flats: if C_1..C_k are clauses on pairwise disjoint sets of variables and no
   other clause uses exactly the same variable set as some C_i, then on the set of
   assignments where the parity of each C_i's variables differs from the parity at which
   C_i fails, the average of N is exactly (m - k)/16.

Both are checked by brute force over all 2^n assignments on random formulas
(clauses of width 4, every literal used at most 3 times).
"""
import itertools
import random


def random_formula(n, m, rng, max_lit=3, tries=2000):
    for _ in range(tries):
        used = {}
        clauses = []
        ok = True
        for _ in range(m):
            for _ in range(200):
                vs = rng.sample(range(n), 4)
                lits = tuple(sorted(v if rng.random() < 0.5 else ~v for v in vs))
                if all(used.get(l, 0) < max_lit for l in lits):
                    for l in lits:
                        used[l] = used.get(l, 0) + 1
                    clauses.append(lits)
                    break
            else:
                ok = False
                break
        if ok:
            return clauses
    return None


def var(l):
    return l if l >= 0 else ~l


def falsified(clause, x):
    # literal v is false when x_v = 0; literal ~v is false when x_v = 1
    return all((x >> var(l)) & 1 == (0 if l >= 0 else 1) for l in clause)


def clash(c1, c2):
    s1 = set(c1)
    return any(~l in s1 for l in c2)


def counts(clauses, n):
    return [sum(falsified(c, x) for c in clauses) for x in range(1 << n)]


def check_second_moment(clauses, n, N):
    lhs = sum(v * (v - 1) for v in N)
    rhs = 0
    for i, c in enumerate(clauses):
        for j, d in enumerate(clauses):
            if i != j and not clash(c, d):
                rhs += 1 << (n - len(set(c) | set(d)))
    return lhs == rhs


def check_parity_flat(clauses, n, N, rng):
    m = len(clauses)
    varsets = [frozenset(map(var, c)) for c in clauses]
    private = [i for i in range(m) if varsets.count(varsets[i]) == 1]
    rng.shuffle(private)
    chosen, covered = [], set()
    for i in private:
        if not (varsets[i] & covered):
            chosen.append(i)
            covered |= varsets[i]
    if not chosen:
        return None
    # parity of the falsifying point of clause i: sum over its variables of the falsifying value
    bad = {i: sum(0 if l >= 0 else 1 for l in clauses[i]) % 2 for i in chosen}
    pts = [x for x in range(1 << n)
           if all(sum((x >> v) & 1 for v in varsets[i]) % 2 != bad[i] for i in chosen)]
    total = sum(N[x] for x in pts)
    # average = total / len(pts) should equal (m - k)/16
    return total * 16 == (m - len(chosen)) * len(pts), len(chosen)


def main():
    rng = random.Random(2026)
    done = 0
    ks = {}
    for trial in range(300):
        n = rng.randint(8, 13)
        m = rng.randint(6, min(18, (6 * n) // 4))
        F = random_formula(n, m, rng)
        if F is None:
            continue
        N = counts(F, n)
        assert check_second_moment(F, n, N), (n, F)
        r = check_parity_flat(F, n, N, rng)
        if r is not None:
            ok, k = r
            assert ok, (n, F)
            ks[k] = ks.get(k, 0) + 1
        done += 1
    print(f"second-moment identity: OK on {done} random formulas")
    print(f"parity-flat average (m - k)/16: OK; number of disjoint private clauses used: {dict(sorted(ks.items()))}")


if __name__ == "__main__":
    main()
