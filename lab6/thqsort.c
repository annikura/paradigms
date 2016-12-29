#include "thqsort.h"
#include "thread_pool.h"

static void swap(int * x, int * y){
    int tmp;
    tmp = *x, *x = *y, *y = tmp;
}

int cmp(const void *a, const void *b){
    int x = *(int*)a;
    int y = *(int*)b;
    if (x == y)
        return 0;
    return (x < y ? -1 : 1);
}

struct q_arg create_qarg(int *l, int * r, int left, struct ThreadPool *pool){
    struct q_arg arg;
    arg.l = l;
    arg.r = r;
    arg.left = left;
    arg.pool = pool;
    return arg;
}

struct Task *create_qtask(int *l, int *r, int left, struct ThreadPool *pool){
    struct Task *task = malloc(sizeof(struct Task));

    task->arg = malloc(sizeof(struct q_arg));
    *(struct q_arg*)task->arg = create_qarg(l, r, left, pool);

    task->f = thsort;
    return task;
}

void thsort(void *data){
    struct q_arg *arg = data, tmp;
    int *pointer, *i;
    struct Task *task;

    if (arg->l >= arg->r - 1)
        return;
    if (arg->left){
        qsort(arg->l, arg->r - arg->l, sizeof(int), cmp);
        return;
    }

    pointer = arg->l;
    for (i = arg->l; i < arg->r; i++)
        if (*i <= *arg->l)
            swap(i, pointer++);

    task = create_qtask(pointer, arg->r, arg->left - 1, arg->pool);
    thpool_submit(arg->pool, task);

    tmp = create_qarg(arg->l, pointer, arg->left - 1, arg->pool);
    thsort((void *)&tmp);

    thpool_wait(task);
    free(task->arg), free(task);
}
