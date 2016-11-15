#include <stdlib.h>

int main(int *argc, char **argv) {
    int     treads = atoi(argv[1]),
            len = atoi(argv[2]),
            rec_lim = atoi(argv[3]),
            i;
    int *a = malloc(sizeof(int) * len);
    srand(42);

    for (i = 0; i < len; i++)
        a[i] = rand();

    free(a);
    return 0;
}