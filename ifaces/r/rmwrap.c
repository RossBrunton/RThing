#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>

int main(int argc, char *argv[]) {
    char* env[] = {NULL};
    
    // Idiot proofing
    if(geteuid() == 0) {
        printf("Please don't run this as root\n");
        exit(1);
    }
    
    // Set real uid to effective uid
    setreuid(geteuid(), geteuid());
    
    execve("/bin/rm", argv, env);
    perror("execve");
    return -1;
}
