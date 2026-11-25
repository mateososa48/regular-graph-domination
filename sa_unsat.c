/* Simulated annealing over "balanced" K-CNFs: c clauses of size K on k variables, distinct
 * variables per clause, every literal occurring exactly B times (c*K = 2*k*B).
 * Energy = number of satisfying assignments (exact, maintained incrementally via a per-assignment
 * count of falsified clauses).  Goal: energy 0, i.e. an UNSAT formula.
 * usage: sa_unsat K B k seed steps [T0]
 * Output: DIMACS-like clause lines of every UNSAT formula found (one per restart).
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

static int K, B, k, c;
static int *cl;            /* c*K literals: lit = 2*v + s, s=1 positive */
static uint8_t *cnt;       /* cnt[a] = #clauses falsified by assignment a */
static long long models;

static uint64_t rs;
static inline uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline double urand(void) { return (rnd() >> 11) * (1.0 / 9007199254740992.0); }

/* enumerate assignments falsifying clause (fixed bits) and add delta */
static long long apply_clause(const int *lits, int delta) {
    /* falsified: positive lit v -> bit v = 0 ; negative lit v -> bit v = 1 */
    uint64_t fixmask = 0, fixval = 0;
    for (int t = 0; t < K; t++) { int v = lits[t] >> 1, s = lits[t] & 1; fixmask |= 1ULL << v; if (!s) fixval |= 1ULL << v; }
    uint64_t free = ((1ULL << k) - 1) & ~fixmask;
    long long dm = 0;
    /* iterate over subsets of free (Gosper-free subset enumeration) */
    uint64_t sub = 0;
    do {
        uint64_t a = sub | fixval;
        if (delta > 0) { if (cnt[a] == 0) dm--; cnt[a]++; }
        else { cnt[a]--; if (cnt[a] == 0) dm++; }
        sub = (sub - free) & free;
    } while (sub != 0);
    return dm;
}

static int clause_has_var(const int *lits, int v, int skip) {
    for (int t = 0; t < K; t++) if (t != skip && (lits[t] >> 1) == v) return 1;
    return 0;
}

static int init_random(void) {
    int L = 2 * k, tot = c * K;
    int *stubs = malloc(sizeof(int) * tot);
    for (int tries = 0; tries < 100000; tries++) {
        int p = 0;
        for (int l = 0; l < L; l++) for (int r = 0; r < B; r++) stubs[p++] = l;
        for (int i = tot - 1; i > 0; i--) { int j = rnd() % (i + 1); int t = stubs[i]; stubs[i] = stubs[j]; stubs[j] = t; }
        /* repair duplicates by random swaps */
        memcpy(cl, stubs, sizeof(int) * tot);
        int bad = 1, it = 0;
        while (bad && it < 100000) {
            bad = 0;
            for (int i = 0; i < c && !bad; i++)
                for (int t = 0; t < K && !bad; t++)
                    if (clause_has_var(cl + i * K, cl[i * K + t] >> 1, t)) {
                        bad = 1;
                        int j = rnd() % tot; int x = cl[i * K + t]; cl[i * K + t] = cl[j]; cl[j] = x;
                    }
            it++;
        }
        if (!bad) { free(stubs); return 1; }
    }
    free(stubs); return 0;
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: K B k seed steps [T0]\n"); return 1; }
    K = atoi(argv[1]); B = atoi(argv[2]); k = atoi(argv[3]); rs = 88172645463325252ULL ^ (uint64_t)atoll(argv[4]) * 2654435761ULL;
    long long steps = atoll(argv[5]); double T0 = argc > 6 ? atof(argv[6]) : 2.0;
    if ((2 * k * B) % K) { fprintf(stderr, "bad params\n"); return 1; }
    c = 2 * k * B / K;
    cl = malloc(sizeof(int) * c * K);
    cnt = calloc(1ULL << k, 1);
    int restarts = 0, found = 0;
    while (1) {
        memset(cnt, 0, 1ULL << k);
        if (!init_random()) { fprintf(stderr, "init failed\n"); return 1; }
        models = 1LL << k;
        for (int i = 0; i < c; i++) models += apply_clause(cl + i * K, +1);
        long long best = models;
        double T = T0;
        for (long long s = 0; s < steps; s++) {
            int i = rnd() % c, j = rnd() % c; if (i == j) continue;
            int p = rnd() % K, q = rnd() % K;
            int *ci = cl + i * K, *cj = cl + j * K;
            int a = ci[p], b = cj[q];
            if (a == b) continue;
            if (clause_has_var(ci, b >> 1, p) || clause_has_var(cj, a >> 1, q)) continue;
            long long dm = 0;
            dm += apply_clause(ci, -1); dm += apply_clause(cj, -1);
            ci[p] = b; cj[q] = a;
            dm += apply_clause(ci, +1); dm += apply_clause(cj, +1);
            if (dm <= 0 || urand() < exp(-(double)dm / T)) { models += dm; }
            else { /* revert */
                apply_clause(ci, -1); apply_clause(cj, -1);
                ci[p] = a; cj[q] = b;
                apply_clause(ci, +1); apply_clause(cj, +1);
            }
            if (models < best) best = models;
            if (models == 0) break;
            if ((s & 1023) == 0) T = T0 * (1.0 - (double)s / steps) + 0.05;
        }
        restarts++;
        if (models == 0) {
            found++;
            printf("UNSAT k=%d c=%d restart=%d :", k, c, restarts);
            for (int i = 0; i < c; i++) { printf(" ["); for (int t = 0; t < K; t++) { int v = cl[i*K+t] >> 1; printf("%s%d", t ? "," : "", (cl[i*K+t] & 1) ? v + 1 : -(v + 1)); } printf("]"); }
            printf("\n"); fflush(stdout);
        } else {
            fprintf(stderr, "restart %d: best models %lld final %lld\n", restarts, best, models);
        }
        if (restarts >= 1000000) break;
    }
    return 0;
}
