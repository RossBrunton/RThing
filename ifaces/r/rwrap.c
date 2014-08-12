#include <unistd.h>
#include <stdio.h>
#include <sys/resource.h>

int main(int argc, char *argv[]) {
    char* args[] = {"--no-save", "-e", argv[1], NULL};
    char* env[] = {"PATH=/:/bin:/usr/bin", NULL};
    
    execve("/usr/bin/Rscript", args, env);
    perror("execve");
    return -1;
}
