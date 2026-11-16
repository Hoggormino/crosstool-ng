#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include <sys/types.h>
#include <time.h>
/* Defined in another translation unit so the floating-point PCS is exercised. */
extern double fp_roundtrip(float, double, int);
int main(void) {
    char *p = malloc(256); assert(p); memset(p, 0x5a, 256);
    assert(p[255] == 0x5a); free(p);
    FILE *f = fopen("owned-probe.txt", "w+"); assert(f);
    assert(fputs("samsung\n", f) >= 0); rewind(f);
    char b[16]; assert(fgets(b, sizeof b, f)); assert(!strcmp(b, "samsung\n"));
    assert(!fclose(f)); assert(!unlink("owned-probe.txt"));
    assert(fp_roundtrip(1.25f, 2.5, 4) == 8.75);
    volatile double fractional = 2.75;
    assert((int)fractional == 2);
    double (*volatile library_sqrt)(double) = sqrt;
    assert(library_sqrt(2.25) == 1.5);
    assert(strtod("3.75", NULL) == 3.75);
    assert(snprintf(b, sizeof b, "%.2f", library_sqrt(2.25)) == 4);
    assert(!strcmp(b, "1.50"));
    printf("C allocation/files/softfp/libm passed; pointer=%u long=%u time_t=%u off_t=%u\n", (unsigned)sizeof(void*), (unsigned)sizeof(long), (unsigned)sizeof(time_t), (unsigned)sizeof(off_t));
    return 0;
}
