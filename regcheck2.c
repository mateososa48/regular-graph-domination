/* regcheck: read graph6 graphs (n <= 64, edges <= 64) on stdin; for each, compute
 *   ge  = gamma_e(G)  = minimum maximal matching = i(L(G))   (exact)
 * and decide whether i(G) <= ge (independent domination) and gamma(G) <= ge.
 * Prints any graph with i(G) > ge (and whether gamma(G) > ge too), plus summary stats.
 * Exact branch-and-bound over 64-bit vertex masks.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef unsigned __int128 u64;
static inline int pc128(u64 x){ return __builtin_popcountll((uint64_t)x) + __builtin_popcountll((uint64_t)(x>>64)); }
static inline int ctz128(u64 x){ uint64_t lo=(uint64_t)x; return lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll((uint64_t)(x>>64)); }
#define ONE ((u64)1)
static int N;              /* vertices of current search graph */
static u64 NB[128];         /* closed neighbourhoods */
static u64 OPEN[128];       /* open neighbourhoods */
static u64 ALL;
static int MAXCLOSED;      /* max |N[v]| */

static int pc(u64 x) { return pc128(x); }

/* exists dominating set S, |S| <= K, (independent if indep) given chosen count c, dominated mask dom, forbidden mask forb */
static int dfs(u64 dom, u64 forb, int c, int K, int indep) {
    if (dom == ALL) return 1;
    if (c >= K) return 0;
    u64 und = ALL & ~dom;
    int u = pc(und);
    if (c + (u + MAXCLOSED - 1) / MAXCLOSED > K) return 0;
    /* choose undominated vertex with fewest candidates */
    int best = -1, bestc = 1000; u64 bestcand = 0;
    u64 t = und;
    while (t) {
        int v = ctz128(t); t &= t - 1;
        u64 cand = NB[v] & ~forb;
        int cc = pc(cand);
        if (cc < bestc) { bestc = cc; best = v; bestcand = cand; if (cc <= 1) break; }
    }
    if (bestc == 0) return 0;
    u64 cand = bestcand;
    while (cand) {
        int w = ctz128(cand); cand &= cand - 1;
        u64 nforb = forb;
        if (indep) nforb |= NB[w];        /* no neighbour of w (nor w) may be chosen later */
        else nforb |= (ONE << w);
        if (dfs(dom | NB[w], nforb, c + 1, K, indep)) return 1;
        /* w not chosen in remaining branches: forbid w to avoid symmetric re-exploration */
        forb |= (ONE << w);
    }
    return 0;
}

static int exists_le(int K, int indep) { return dfs(0, 0, 0, K, indep); }

static int exact_min(int lo, int indep) {
    int K = lo;
    while (!exists_le(K, indep)) K++;
    return K;
}

/* graph6 parse */
static int g_n; static int adj[128][128];
static int parse_g6(const char *s) {
    const unsigned char *p = (const unsigned char *)s;
    if (*p == '>') p += 10; /* header >>graph6<< */
    int n = *p++ - 63;
    if (n > 62 || n < 1) return -1;
    g_n = n;
    memset(adj, 0, sizeof adj);
    int k = 6, x = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            if (k == 6) { x = *p++ - 63; k = 0; }
            int bit = (x >> (5 - k)) & 1; k++;
            if (bit) adj[i][j] = adj[j][i] = 1;
        }
    return n;
}

int main(int argc, char **argv) {
    char line[4096];
    long count = 0, bad_i = 0, bad_g = 0;
    long hist_slack[8] = {0}; long hist_gap[16] = {0}; int printed = 0; int maxprint = argc > 2 ? atoi(argv[2]) : 0;
    int Delta = argc > 1 ? atoi(argv[1]) : 4;
    while (fgets(line, sizeof line, stdin)) {
        size_t L = strlen(line); while (L && (line[L-1]=='\n'||line[L-1]=='\r')) line[--L] = 0;
        if (!L) continue;
        int n = parse_g6(line); if (n < 0) continue;
        /* edges */
        int eu[128], ev[128], m = 0;
        for (int i = 0; i < n; i++) for (int j = i+1; j < n; j++) if (adj[i][j]) {
            if (m >= 128) { fprintf(stderr, "too many edges\n"); return 1; }
            eu[m] = i; ev[m] = j; m++;
        }
        /* line graph */
        N = m; ALL = (m == 128) ? ~(u64)0 : ((ONE << m) - 1); MAXCLOSED = 0;
        for (int a = 0; a < m; a++) {
            u64 nb = ONE << a;
            for (int b = 0; b < m; b++) if (b != a &&
                (eu[a]==eu[b]||eu[a]==ev[b]||ev[a]==eu[b]||ev[a]==ev[b])) nb |= ONE << b;
            NB[a] = nb; if (pc(nb) > MAXCLOSED) MAXCLOSED = pc(nb);
        }
        int lo = (Delta * n + (4*Delta-2) - 1) / (4*Delta - 2);
        int ge = exact_min(lo, 1);
        /* original graph */
        N = n; ALL = ((ONE << n) - 1); MAXCLOSED = 0;
        for (int v = 0; v < n; v++) {
            u64 nb = ONE << v;
            for (int w = 0; w < n; w++) if (adj[v][w]) nb |= ONE << w;
            NB[v] = nb; if (pc(nb) > MAXCLOSED) MAXCLOSED = pc(nb);
        }
        count++;
        int s = ge - lo; if (s > 7) s = 7; hist_slack[s]++;
        { int iv = exact_min((n + Delta) / (Delta + 1), 1); int gap = ge - iv; if (gap < 0) gap = 0; if (gap > 15) gap = 15; hist_gap[gap]++;
          if (ge - iv == 0 && printed < maxprint) { printed++; printf("TIGHT n=%d ge=%d lb=%d i=%d %s\n", n, ge, lo, iv, line); } }
        if (!exists_le(ge, 1)) {
            bad_i++;
            int iv = exact_min(ge + 1, 1);
            int g_ok = exists_le(ge, 0);
            if (!g_ok) bad_g++;
            printf("COUNTEREXAMPLE_i n=%d ge=%d i=%d gamma<=ge:%s %s\n", n, ge, iv, g_ok ? "yes" : "NO", line);
            fflush(stdout);
        }
    }
    fprintf(stderr, "checked %ld graphs; i>ge: %ld; gamma>ge: %ld; ge-lowerbound histogram:", count, bad_i, bad_g);
    for (int s = 0; s < 8; s++) fprintf(stderr, " %ld", hist_slack[s]);
    fprintf(stderr, " | ge-i histogram:");
    for (int s = 0; s < 16; s++) fprintf(stderr, " %ld", hist_gap[s]);
    fprintf(stderr, "\n");
    return 0;
}
