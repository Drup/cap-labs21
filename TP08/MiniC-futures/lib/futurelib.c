#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <stdlib.h>
#include <unistd.h>
#include "../include/futurelib.h"

FutureInt *All[70]; 
// a table of future pointers to store all the future created
// in a realistic scenario this would be a dynamic structure
int NbAll = 0;
// Number of future created

typedef struct 
// a structure for the argument of thread creation: function pointer and parameter
{
  FutureInt *fut;
  int (*fun)(int);
  int param;
} arg_struct;

void print_futureInt(FutureInt *f)
{
  // TODO FOR DEBUG
}

FutureInt *fresh_future_malloc()
{
  //TODO: use malloc(sizeof(FutureInt)) and reference created futures
}

void free_future(FutureInt *fut)
{
  free(fut);
}

void resolve_future(FutureInt *fut, int val)
{
  // TODO: fill fut accordingly
}

int Get(FutureInt *fut)
{
  //TODO
  // wait until future is resolved (do a sleep(1) between two checks)
  // do not forget to do a pthread_join(fut->tid, NULL);
  return 0;
}

void *runTask(void *param)
{
  //TODO
  // function that is launched by the created thread: should call the function and deal with the future
  // param can be cast to (arg_struct *)
  // this function should free the pointer param
  return NULL;
}

FutureInt *Async(int (*fun)(int), int p)
{
  // TODO
  // Main system call should be: int err = pthread_create(&fut->tid, NULL, &runTask, (args));
  // allocate a future
  // and space for arguments:  args=malloc(sizeof(arg_struct));
  // do not forget to populate args
  return NULL;
}

void freeAllFutures()
{
  // TODO:
  // 1-  wait for all futures (Get) to avoid dangling threads
  // 2 - call free_future for all futures
}
