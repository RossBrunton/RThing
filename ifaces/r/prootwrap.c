#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    char* env[] = {"PATH=/:/bin:/usr/bin", NULL};
    
    // Idiot proofing
    if(geteuid() == 0) {
        printf("Please don't run this as root\n");
        exit(1);
    }
    
    // Set real uid to effective uid
    setreuid(geteuid(), geteuid());
    
    // Lower priority
    nice(5);
    
    execve("/usr/bin/timeout", argv, env);
    perror("execve");
    return -1;
}
