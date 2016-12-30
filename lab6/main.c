#include <stdlib.h>
#include <stdio.h>

#include "thqsort.h"
#include "wsqueue.h"
#include "thread_pool.h"

int main(int argc, char **argv) {
    struct ThreadPool pool;
    struct Task * task;
    int threads, len, rec_lim, i, *a;

    if (argc != 4){
        printf("Something's wrong...\n");
        return 0;
    }

    threads = atoi(argv[1]);
    len = atoi(argv[2]);
    rec_lim = atoi(argv[3]);

    a = malloc(sizeof(int) * len);
    srand(42);
    for (i = 0; i < len; i++){
        a[i] = rand();
    }

    task = create_qtask(a, len, rec_lim, &pool);

    thpool_init(&pool, threads);
    thpool_submit(&pool, task);
    tree_wait_for_all(task);
    thpool_finit(&pool);

    for (i = 1; i < len; i++)
        if (a[i - 1] > a[i]){
            printf("It's not sorted\n");
        }

    free(a);
    return 0;
}
