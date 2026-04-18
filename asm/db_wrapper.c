extern long long check_rowcount(long long value);
extern long long choose_field(long long value);

__declspec(dllexport)
int check_rowcount_wrapper(long long value) {
    return (int)check_rowcount(value);
}

__declspec(dllexport)
int choose_field_wrapper(long long is_int) {
    return (int)choose_field(is_int);
}