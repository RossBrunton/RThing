#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>

int main(int argc, char *argv[]) {
    char* env[] = {"PATH=/:/bin:/usr/bin", NULL};
    
    // Memory limit
    const struct rlimit mlimit = {
        .rlim_cur = 1024 * 1024 * 150,
        .rlim_max = 1024 * 1024 * 160
    };
    setrlimit(RLIMIT_AS, &mlimit);
    
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
    return 1;
}
