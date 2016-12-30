#include <stdio.h>
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

void tree_wait_for_all(struct Task *task){
    if (!task)
        return;
    if (!task->finished)
        thpool_wait(task);
    tree_wait_for_all(((struct q_arg*)task->arg)->lc);
    tree_wait_for_all(((struct q_arg*)task->arg)->rc);
    free(task->arg), free(task);
}

struct q_arg *create_qarg(int *st, int len, int left, struct ThreadPool *pool){
    struct q_arg *arg;
    arg = malloc(sizeof(struct q_arg));
    arg->st = st;
    arg->len = len;
    arg->left = left;
    arg->pool = pool;
    arg->lc = NULL, arg->rc = NULL;
    return arg;
}

struct Task *create_qtask(int *st, int len, int left, struct ThreadPool *pool){
    struct Task *task = malloc(sizeof(struct Task));
    task->arg = (void *)create_qarg(st, len, left, pool);
    task->f = thsort;
    return task;
}

void thsort(void *data){
    struct q_arg *arg = data;
    int pointer = 0, i, mid = arg->st[arg->len / 2];
    struct Task *task1, *task2;

    if (arg->left == 0 || arg->len < 4096){
        if (arg->len > 1)
            qsort(arg->st, arg->len, sizeof(int), cmp);
        return;
    }

    for (i = 0; i < arg->len; i++)
        if (arg->st[i] <= mid)
            swap(arg->st + i, arg->st + pointer++);

    task1 = create_qtask(arg->st, pointer, arg->left - 1, arg->pool);
    task2 = create_qtask(arg->st + pointer, arg->len - pointer, arg->left - 1, arg->pool);
    arg->lc = task1, arg->rc = task2;
    thpool_submit(arg->pool, task1);
    thpool_submit(arg->pool, task2);
}
