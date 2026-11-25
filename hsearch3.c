/* Search for an unsatisfiable formula H consisting of T clauses of size 3 and m4 clauses of size 4
 * on nv variables, in which every literal occurs at most LB times (default 3).
 * Such an H yields a block B = H with a fresh input literal appended to each 3-clause; B forces
 * (X1 v ... v XT).  Substituting a block for every clause of an unsatisfiable T-CNF with literal
 * occurrences <= LB gives an unsatisfiable 4-CNF with literal occurrences <= LB.
 * Energy = number of satisfying assignments (exact).  usage: hsearch nv m4 T LB seed steps T0
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

static int nv, m4, T3, LB, mcl, T2, SM, BG;
static int *len, *lit;      /* clause j: len[j] literals at lit[j*4 + t]; literal = 2*v + s (s=1 pos) */
static int *occ;            /* occurrences per literal */
static uint8_t *cnt; static long long models;
static uint64_t rs;
static inline uint64_t rnd(void){ rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline double urand(void){ return (rnd() >> 11) * (1.0/9007199254740992.0); }

static long long apply(int j, int delta){
    uint64_t fixmask = 0, fixval = 0;
    for (int t = 0; t < len[j]; t++){ int v = lit[j*4+t] >> 1, s = lit[j*4+t] & 1; fixmask |= 1ULL << v; if (!s) fixval |= 1ULL << v; }
    uint64_t freem = ((1ULL << nv) - 1) & ~fixmask; long long dm = 0; uint64_t sub = 0;
    do { uint64_t a = sub | fixval;
         if (delta > 0){ if (cnt[a] == 0) dm--; cnt[a]++; } else { cnt[a]--; if (cnt[a] == 0) dm++; }
         sub = (sub - freem) & freem; } while (sub);
    return dm;
}
static int clause_has_var(int j, int v, int skip){ for (int t = 0; t < len[j]; t++) if (t != skip && (lit[j*4+t]>>1) == v) return 1; return 0; }

static int init(void){
    memset(occ, 0, sizeof(int)*2*nv);
    for (int j = 0; j < mcl; j++){
        for (int t = 0; t < len[j]; t++){
            int tries = 0, l;
            do { l = rnd() % (2*nv); tries++; } while ((occ[l] >= LB || clause_has_var(j, l>>1, t) ) && tries < 10000);
            if (tries >= 10000) return 0;
            lit[j*4+t] = l; occ[l]++;
        }
    }
    return 1;
}
int main(int argc, char **argv){
    nv = atoi(argv[1]); m4 = atoi(argv[2]); T3 = atoi(argv[3]); LB = atoi(argv[4]); T2 = argc > 8 ? atoi(argv[8]) : 0; BG = argc > 9 ? atoi(argv[9]) : 4; SM = BG - 1;
    rs = 0x9E3779B97F4A7C15ULL ^ ((uint64_t)atoll(argv[5]) * 0xD1B54A32D192ED03ULL);
    long long steps = atoll(argv[6]); double T0 = atof(argv[7]);
    mcl = T2 + T3 + m4;
    if ((SM-1)*T2 + SM*T3 + BG*m4 > 2*nv*LB){ fprintf(stderr, "too many literal slots\n"); return 1; }
    len = malloc(sizeof(int)*mcl); lit = malloc(sizeof(int)*mcl*4); occ = malloc(sizeof(int)*2*nv);
    for (int j = 0; j < mcl; j++) len[j] = (j < T2) ? SM-1 : (j < T2 + T3) ? SM : BG;
    cnt = calloc(1ULL << nv, 1);
    for (int restart = 0; ; restart++){
        while (!init());
        memset(cnt, 0, 1ULL << nv); models = 1LL << nv;
        for (int j = 0; j < mcl; j++) models += apply(j, +1);
        long long best = models;
        for (long long s = 0; s < steps; s++){
            double Tt = T0 * (1.0 - (double)s/steps) + 0.03;
            if (rnd() & 1) {
            int j = rnd() % mcl, t = rnd() % len[j]; int old = lit[j*4+t];
            int nl = rnd() % (2*nv);
            if (nl == old || occ[nl] >= LB || clause_has_var(j, nl>>1, t)) continue;
            long long dm = apply(j, -1); lit[j*4+t] = nl; occ[old]--; occ[nl]++; dm += apply(j, +1);
            if (dm <= 0 || urand() < exp(-(double)dm / Tt)) { models += dm; }
            else { apply(j, -1); lit[j*4+t] = old; occ[nl]--; occ[old]++; apply(j, +1); }
            } else {  /* swap two literal slots between different clauses (keeps occurrence counts) */
            int i = rnd() % mcl, j = rnd() % mcl; if (i == j) continue;
            int p = rnd() % len[i], q = rnd() % len[j]; int a = lit[i*4+p], b = lit[j*4+q];
            if (a == b || clause_has_var(i, b>>1, p) || clause_has_var(j, a>>1, q)) continue;
            long long dm = apply(i, -1) + apply(j, -1); lit[i*4+p] = b; lit[j*4+q] = a; dm += apply(i, +1) + apply(j, +1);
            if (dm <= 0 || urand() < exp(-(double)dm / Tt)) { models += dm; }
            else { apply(i, -1); apply(j, -1); lit[i*4+p] = a; lit[j*4+q] = b; apply(i, +1); apply(j, +1); }
            }
            if (models < best) best = models;
            if (models == 0) break;
        }
        if (models == 0){
            printf("UNSAT nv=%d T3=%d m4=%d LB=%d :", nv, T3, m4, LB);
            for (int j = 0; j < mcl; j++){ printf(" ["); for (int t = 0; t < len[j]; t++){ int l = lit[j*4+t]; printf("%s%d", t?",":"", (l&1)?(l>>1)+1:-((l>>1)+1)); } printf("]"); }
            printf("\n"); fflush(stdout); return 0;
        }
        { static long long gbest = -1; if (gbest < 0 || best < gbest) gbest = best; fprintf(stderr, "restart %d best models %lld (overall %lld)\n", restart, best, gbest); }
        if (restart >= 200) break;
    }
    return 0;
}
