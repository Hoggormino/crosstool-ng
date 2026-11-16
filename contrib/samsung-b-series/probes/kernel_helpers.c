#include <stdio.h>
int main(void) {
    /* Observation under QEMU only; this is not a TV helper-version probe. */
    printf("QEMU kuser_helper_version=%u\n", *(volatile unsigned *)0xffff0ffc);
    return 0;
}
