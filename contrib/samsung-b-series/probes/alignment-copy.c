/* Regression for libstdc++ money_base::pattern: four bytes, byte alignment. */
struct pattern { char field[4]; };
_Static_assert(_Alignof(struct pattern) == 1, "pattern must be byte aligned");
void copy_pattern(struct pattern *destination, const struct pattern *source)
{
    *destination = *source;
}
