#ifndef __THREAD_SORT_H__
#define __THREAD_SORT_H__

#include <stdlib.h>
#include "wsqueue.h"
#include "thread_pool.h"

struct q_arg{
    int *st;
    int left, len;
    struct Task *lc, *rc;
    struct ThreadPool * pool;
};

void tree_wait_for_all(struct Task *task);
int cmp(const void *a, const void *b);
struct Task *create_qtask(int *st, int len, int left, struct ThreadPool *pool);
void thsort(void * data);

#endif
