#ifndef __THREAD_SORT_H__
#define __THREAD_SORT_H__

#include <stdlib.h>
#include "wsqueue.h"
#include "thread_pool.h"

struct q_arg{
    int *l, *r;
    int left;
    struct ThreadPool * pool;
};

int cmp(const void *a, const void *b);
struct Task * create_qtask(int *l, int *r, int left, struct ThreadPool *pool);
void thsort(void * data);

#endif
