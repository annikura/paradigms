#ifndef _THREAD_POOL_H
#define _THREAD_POOL_H

#include "squeue.h"

struct Task{
    void (*f)(void *);
    void* arg;
};

struct ThreadPool{
    pthread_t *ths;
    size_t threads_nm;
    struct squeue tasks;
    pthread_cond_t cond;
    int left;
    int destruction_time;
};

void thpool_init(struct ThreadPool* pool, size_t threads_nm);
// инициализирует пул потоков, threads_nm -- число потоков
void thpool_submit(struct ThreadPool* pool, struct Task* task);
// добавляет задачу на выполнение в пул потоков
void thpool_wait(struct Task* task);
// возвращает управление только после того, как задача task завершилась
void thpool_finit(struct ThreadPool* pool);
// финализирует пул потоков, дожидается завершения всех задач в пуле,
// затем освобождает ресурсы, потребляемые пулом потоков

void do_smth(void *data);
void *sit_and_wait(void *data);


#endif //_THREAD_POOL_H
