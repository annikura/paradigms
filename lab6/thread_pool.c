#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>
#include <pthread.h>
#include "wsqueue.h"
#include "thread_pool.h"

static void* thpool_go(void*);

void thpool_init(struct ThreadPool *pool, unsigned threads_nm) {
    unsigned i;
    pool->threads_nm = threads_nm;
    pool->threads = malloc(sizeof(pthread_t) * threads_nm);

    wsqueue_init(&pool->tasks);
    for (i = 0; i < threads_nm; i++) {
        assert(pthread_create(&pool->threads[i], NULL, thpool_go, pool) == 0);
    }
}

void thpool_submit(struct ThreadPool *pool, struct Task *task) {
    pthread_mutex_init(&task->guard, NULL);
    pthread_cond_init(&task->finished_cond, NULL);
    task->finished = false;
    wsqueue_push(&pool->tasks, &task->node);
}

void thpool_wait(struct Task *task) {
    pthread_mutex_lock(&task->guard);
    while (!task->finished) {
        pthread_cond_wait(&task->finished_cond, &task->guard);
    }
    pthread_mutex_unlock(&task->guard);
    pthread_cond_destroy(&task->finished_cond);
    pthread_mutex_destroy(&task->guard);
}

void thpool_finit(struct ThreadPool *pool) {
    unsigned i;
    struct Task *finit_tasks = malloc(sizeof(struct Task) * pool->threads_nm);
    for (i = 0; i < pool->threads_nm; i++) {
        finit_tasks[i].f = NULL;
        finit_tasks[i].arg = NULL;
        thpool_submit(pool, &finit_tasks[i]);
    }

    for (i = 0; i < pool->threads_nm; i++) {
        pthread_join(pool->threads[i], NULL);
    }
    free(pool->threads);
    free(finit_tasks);

    assert(wsqueue_pop(&pool->tasks) == NULL);
    wsqueue_finit(&pool->tasks);
}

void* thpool_go(void *arg) {
    struct ThreadPool *pool = arg;
    struct Task *task;
    for (;;) {
        wsqueue_wait(&pool->tasks);
        task = (struct Task*)wsqueue_pop(&pool->tasks);
        if (!task) {
            continue;
        }
        if (!task->f) {
            break;
        }
        task->f(task->arg);
        pthread_mutex_lock(&task->guard);
        task->finished = true;
        pthread_cond_signal(&task->finished_cond);
        pthread_mutex_unlock(&task->guard);
    }
    return NULL;
}
