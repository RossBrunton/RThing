#include <unistd.h>
#include <stdio.h>
#include <sys/resource.h>

int main(int argc, char *argv[]) {
    char* args[] = {"--no-save", "-e", argv[1], NULL};
    char* env[] = {"PATH=/:/bin", NULL};
    
    execve("/Rscript", args, env);
    perror("execve");
    return -1;
}
