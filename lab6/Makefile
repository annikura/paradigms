CC      ?= gcc
CFLAGS  ?= -Wall -Wextra -Werror -Wshadow -ansi -pedantic
LDFLAGS ?= -lpthread

all: main

main: main.o linkedlist.o queue.o squeue.o wsqueue.o thqsort.o thread_pool.o
	$(CC) main.o linkedlist.o queue.o squeue.o wsqueue.o thqsort.o thread_pool.o \
		$(LDFLAGS) -o main

main.o: main.c
	$(CC) -c main.c $(CFLAGS) -o main.o

linkedlist.o: linkedlist.c
	$(CC) -c linkedlist.c $(CFLAGS) -o linkedlist.o

queue.o: queue.c 	queue.h
	$(CC) -c queue.c $(CFLAGS) -o queue.o

squeue.o: squeue.c squeue.h
	$(CC) -c squeue.c $(CFLAGS) -o squeue.o

wsqueue.o: wsqueue.c wsqueue.h
	$(CC) -c wsqueue.c $(CFLAGS) -o wsqueue.o

thqsort.o: thqsort.c thqsort.h
	$(CC) -c thqsort.c $(CFLAGS) -o thqsort.o


thread_pool.o: thread_pool.c thread_pool.h
	$(CC) -c thread_pool.c $(CFLAGS) -o thread_pool.o


clean:
	rm *.o main

.PHONY: clean
