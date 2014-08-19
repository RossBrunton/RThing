#include <unistd.h>
#include <stdio.h>
#include <sys/resource.h>
#include <stdlib.h>
#include <signal.h>

int main(int argc, char *argv[]) {
    char* env[] = {"PATH=/:/bin:/usr/bin", NULL};
    
    // Set real uid to effective uid
    setreuid(geteuid(), geteuid());
    
    // Lower priority
    nice(5);
    
    execve("/usr/bin/timeout", argv, env);
    perror("execve");
    return -1;
}
