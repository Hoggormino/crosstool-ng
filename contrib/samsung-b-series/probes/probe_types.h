#ifndef SAMSUNG_MODERN_PROBE_TYPES_H
#define SAMSUNG_MODERN_PROBE_TYPES_H
struct Base { virtual ~Base() = default; };
struct Child : Base { int value = 17; };
Child *owned_dynamic_cast(Base *);
#endif
