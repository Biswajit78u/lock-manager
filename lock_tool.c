#include <windows.h>
#include <stdio.h>
#include <string.h>

__declspec(dllexport) int lock_path(const char* path) {
    char command[600];
    snprintf(command, sizeof(command), "icacls \"%s\" /deny Everyone:(F)", path);
    int result = system(command);
    return result;
}

__declspec(dllexport) int unlock_path(const char* path) {
    char command[600];
    snprintf(command, sizeof(command), "icacls \"%s\" /remove:d Everyone", path);
    int result = system(command);
    return result;
}