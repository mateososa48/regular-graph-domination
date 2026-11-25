// Exhaustive search for cores: unsatisfiable CNFs on r variables, clause widths WMIN..K, every literal in at
// most L clauses, total deficit D = sum (K - width) <= DMAX.   (D = 0 would be an unsatisfiable (K,L,L)-formula.)
//
// View a clause as the subcube of assignments that falsify it; the formula is unsatisfiable iff the subcubes
// cover {0,1}^r.  DFS: take the smallest uncovered point a and branch over every clause that is false at a
// (its variable set S determines it, since the signs are forced by a).  This is complete: some clause of any
// cover contains a.  Symmetry: variables that occur in no clause so far are interchangeable (the uncovered set
// is a cylinder over them and a is 0 there), so new variables are taken in index order.
// Pruning: literal bound, deficit budget, and a counting bound on what the remaining literal slots can cover.
//
// usage: coredfs K L DMAX r [WMIN=2] [mode: 0=stop at first, 1=count all] [split_depth split_index split_total]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define RMAX 16
int K,L,DMAX,R,WMIN=2,MODE=0,SPLITD=0,SPLITI=0,SPLITN=1,HIT=0;
static uint8_t *cnt; static long U;            // cover multiplicity, number of uncovered points
static int pos[RMAX],neg[RMAX],usedv[RMAX];
static unsigned __int128 sig[RMAX];        // occurrence pattern of each variable over the clauses so far
static double captab[200][40];
static int dleft,sleft;                          // deficit budget left, literal slots left
static int cl[64][RMAX+1],ncl=0;                 // clauses as signed literals
static unsigned long long nodes=0,found=0,leafctr=0;
static void apply(int *S,int w,long a,int delta){
  // subcube: variables in S fixed to a's values, others free
  long fixedmask=0; for(int i=0;i<w;i++) fixedmask|=1L<<S[i];
  long base=a&fixedmask, freemask=((1L<<R)-1)&~fixedmask;
  long sub=0;
  do{ long p=base|sub;
      if(delta>0){ if(cnt[p]++==0) U--; } else { if(--cnt[p]==0) U++; }
      sub=(sub-freemask)&freemask; } while(sub);
}
static int overlaps(int *S,int w,long a){
  long fixedmask=0; for(int i=0;i<w;i++) fixedmask|=1L<<S[i];
  long base=a&fixedmask, freemask=((1L<<R)-1)&~fixedmask, sub=0;
  do{ if(cnt[base|sub]) return 1; sub=(sub-freemask)&freemask; } while(sub);
  return 0;
}
static void report(void){
  found++;
  if(MODE==0||found<=5){ printf("CORE r=%d clauses=%d D=%d:",R,ncl,DMAX-dleft);
    for(int i=0;i<ncl;i++){ printf(" ("); for(int j=1;j<=cl[i][0];j++) printf(j>1?",%d":"%d",cl[i][j]); printf(")"); } printf("\n"); fflush(stdout); }
  if(MODE==0) exit(0);
}
static void dfs(long start,int depth);
static void choose(long a,int w,int from,int k,int *S,int newcount,long start,int depth){
  // pick w variables; S[0..k-1] chosen so far (increasing); unused variables must be taken in index order
  if(k==w){
    if(HIT && overlaps(S,w,a)) return;
    for(int i=0;i<w;i++){ int j=S[i]; if((a>>j)&1) neg[j]++; else pos[j]++; usedv[j]++; }
    cl[ncl][0]=w; for(int i=0;i<w;i++) cl[ncl][i+1]=((a>>S[i])&1)?-(S[i]+1):(S[i]+1);
    unsigned __int128 save[RMAX]; for(int i=0;i<w;i++){ int j=S[i]; save[i]=sig[j]; sig[j]|=((unsigned __int128)(((a>>j)&1)?2:1))<<(2*ncl); }
    ncl++;
    dleft-=K-w; sleft-=w; apply(S,w,a,+1);
    dfs(start,depth+1);
    apply(S,w,a,-1); dleft+=K-w; sleft+=w; ncl--;
    for(int i=0;i<w;i++) sig[S[i]]=save[i];
    for(int i=0;i<w;i++){ int j=S[i]; if((a>>j)&1) neg[j]--; else pos[j]--; usedv[j]--; }
    return;
  }
  for(int j=from;j<R;j++){
    if(R-j<w-k) break;
    if((a>>j)&1){ if(neg[j]>=L) continue; } else { if(pos[j]>=L) continue; }
    // twin symmetry: variables with the same occurrence pattern and the same value in a are interchangeable
    // (swapping them fixes the current formula and the point a), so take twins in index order.
    int ok=1;
    for(int q=0;q<j;q++) if(sig[q]==sig[j] && (((a>>q)^(a>>j))&1)==0){ int in=0; for(int i=0;i<k;i++) if(S[i]==q) in=1; if(!in){ok=0;break;} }
    if(!ok) continue;
    S[k]=j; choose(a,w,j+1,k+1,S,newcount,start,depth);
  }
}
static void dfs(long start,int depth){
  nodes++;
  if(U==0){ report(); return; }
  if(SPLITD && depth==SPLITD){ if((long)(leafctr++ % SPLITN)!=SPLITI) return; }
  // counting bound: c clauses use 4c - sum(u) <= sleft slots, sum(u) <= dleft, cover <= sum 2^(R-K+u)
  double unit=(double)(1L<<R)/(double)(1L<<K);
  if((double)U>unit*captab[sleft][dleft]+1e-9) return;
  // fail-first: among uncovered points pick one with the fewest literals still available (ties: smallest
  // index, which is 0 on all unused variables, so the symmetry rule in choose() stays valid).  If some
  // uncovered point cannot be covered by any admissible clause, prune.
  long Xp=0,Xn=0; for(int j=0;j<R;j++){ if(pos[j]>=L) Xp|=1L<<j; if(neg[j]>=L) Xn|=1L<<j; }
  int wneed = (K-dleft>WMIN)?(K-dleft):WMIN;
  long a=-1; int best=RMAX+1; long N=1L<<R, full=N-1;
  for(long p=0;p<N;p++) if(!cnt[p]){
    int av=R-__builtin_popcountl(((~p)&full&Xp)|(p&Xn));
    if(av<wneed) return;
    if(av<best){ best=av; a=p; if(best==wneed) break; }
  }
  int S[RMAX];
  for(int w=K; w>=WMIN; w--){
    if(K-w>dleft || w>sleft) continue;
    choose(a,w,0,0,S,0,a,depth);
  }
}
int main(int argc,char**argv){
  K=atoi(argv[1]);L=atoi(argv[2]);DMAX=atoi(argv[3]);R=atoi(argv[4]);
  if(argc>5)WMIN=atoi(argv[5]); if(argc>6)MODE=atoi(argv[6]);
  if(argc>9){SPLITD=atoi(argv[7]);SPLITI=atoi(argv[8]);SPLITN=atoi(argv[9]);}
  if(getenv("HIT")) HIT=atoi(getenv("HIT"));
  // captab[s][d] = max total of 2^(u_i) over clause multisets with sum (K-u_i) <= s and sum u_i <= d
  for(int ss=0;ss<=2*L*R;ss++) for(int d=0;d<=DMAX;d++){ double best=0;
    for(int u=0;u<=K-WMIN;u++) if(K-u<=ss && u<=d){ double vv=(double)(1<<u)+captab[ss-(K-u)][d-u]; if(vv>best) best=vv; }
    captab[ss][d]=best; }
  cnt=calloc(1L<<R,1); U=1L<<R; dleft=DMAX; sleft=2*L*R;
  dfs(0,0);
  printf("DONE K=%d L=%d DMAX=%d r=%d WMIN=%d HIT=%d: cores found=%llu nodes=%llu\n",K,L,DMAX,R,WMIN,HIT,found,nodes);
  return 0;
}
