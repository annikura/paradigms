#include <stdlib.h>
#include "thread_pool.h"

void *sit_and_wait(void *data){
    struct ThreadPool *pool = data;
    pthread_mutex_lock(&pool->tasks.mutex);

    while (!pool->destruction_time || pool->left ||
           queue_size(&pool->tasks.queue)) {
        while (queue_size(&pool->tasks.queue) == 0 &&
               (!pool->destruction_time || pool->left))
            pthread_cond_wait(&pool->cond, &pool->tasks.mutex);

        pthread_mutex_unlock(&pool->tasks.mutex);

        do_smth(data);

        pthread_mutex_lock(&pool->tasks.mutex);
    }
    pthread_mutex_unlock(&pool->tasks.mutex);
    pthread_cond_broadcast(&pool->cond);
    return NULL;
}

void do_smth(void * data){
    struct ThreadPool *pool = data;

    while (1) {
        pthread_mutex_lock(&pool->tasks.mutex);

        if (queue_size(&pool->tasks.queue) == 0) {
            pthread_mutex_unlock(&pool->tasks.mutex);
            break;
        }
        struct Task *task = squeue_pop(&pool->tasks.queue);
        pool->left += 1;
        pthread_mutex_unlock(&pool->tasks.mutex);

        task->f(task->arg);

        pthread_mutex_lock(&pool->tasks.mutex);
        pool->left -= 1;
        pthread_mutex_unlock(&pool->tasks.mutex);
    }
}


void thpool_init(struct ThreadPool *pool, size_t threads_nm) {
    int i;

    pthread_mutex_lock(&pool->tasks.mutex);

    pool->destruction_time = 0;
    pool->ths = malloc(sizeof(pthread_t) * threads_nm);

    squeue_init(&pool->tasks);
    pthread_cond_init(&pool->cond, NULL);

    for (i = 0; i < threads_nm; i++)
        pthread_create(&pool->ths[i], NULL, sit_and_wait, pool);

    pool->threads_nm = threads_nm;
    pool->left = 0;

    pthread_mutex_unlock(&pool->tasks.mutex);
}

void thpool_submit(struct ThreadPool* pool, struct Task* task){

    pthread_mutex_lock(&pool->tasks.mutex);

    queue_push(&pool->tasks.queue, task);
    pthread_cond_signal(&pool->cond);

    pthread_mutex_unlock(&pool->tasks.mutex);

}


void thpool_finit(struct ThreadPool* pool) {
    int i;

    pool->destruction_time = 1;
    pthread_cond_broadcast(&pool->cond);

    for (i = 0; i < pool->threads_nm; i++)
        pthread_join(pool->ths[i], NULL);

    pthread_cond_destroy(&pool->cond);
    squeue_finit(&pool->tasks);

    free(pool->ths);
}
