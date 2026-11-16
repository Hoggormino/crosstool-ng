# Math capability table

C99 scalar and complex functions, all three target precisions. `C decl` tests the native header; `ABI link` uses a separate explicit-prototype probe with a forced symbol relocation. Both rebuilt and preserved OE links pass for every row. No target execution or numerical accuracy claim is made.

| C symbol | C decl | OE symbol/version | Double alias | C++ overload | C++ named |
| --- | --- | --- | --- | --- | --- |
| `acosf` | yes | `GLIBC_2.4` | — | yes | yes |
| `asinf` | yes | `GLIBC_2.4` | — | yes | yes |
| `atanf` | yes | `GLIBC_2.4` | — | yes | yes |
| `cosf` | yes | `GLIBC_2.4` | — | yes | yes |
| `sinf` | yes | `GLIBC_2.4` | — | yes | yes |
| `tanf` | yes | `GLIBC_2.4` | — | yes | yes |
| `coshf` | yes | `GLIBC_2.4` | — | yes | yes |
| `sinhf` | yes | `GLIBC_2.4` | — | yes | yes |
| `tanhf` | yes | `GLIBC_2.4` | — | yes | yes |
| `expf` | yes | `GLIBC_2.4` | — | yes | yes |
| `logf` | yes | `GLIBC_2.4` | — | yes | yes |
| `log10f` | yes | `GLIBC_2.4` | — | yes | yes |
| `sqrtf` | yes | `GLIBC_2.4` | — | yes | yes |
| `ceilf` | yes | `GLIBC_2.4` | — | yes | yes |
| `floorf` | yes | `GLIBC_2.4` | — | yes | yes |
| `fabsf` | yes | `GLIBC_2.4` | — | yes | yes |
| `atan2f` | yes | `GLIBC_2.4` | — | yes | yes |
| `powf` | yes | `GLIBC_2.4` | — | yes | yes |
| `fmodf` | yes | `GLIBC_2.4` | — | yes | yes |
| `frexpf` | yes | `GLIBC_2.4` | — | yes | yes |
| `ldexpf` | yes | `GLIBC_2.4` | — | yes | yes |
| `modff` | yes | `GLIBC_2.4` | — | yes | yes |
| `acoshf` | yes | `GLIBC_2.4` | — | missing | missing |
| `asinhf` | yes | `GLIBC_2.4` | — | missing | missing |
| `atanhf` | yes | `GLIBC_2.4` | — | missing | missing |
| `exp2f` | yes | `GLIBC_2.4` | — | missing | missing |
| `expm1f` | yes | `GLIBC_2.4` | — | missing | missing |
| `log1pf` | yes | `GLIBC_2.4` | — | missing | missing |
| `log2f` | yes | `GLIBC_2.4` | — | missing | missing |
| `logbf` | yes | `GLIBC_2.4` | — | missing | missing |
| `cbrtf` | yes | `GLIBC_2.4` | — | missing | missing |
| `erff` | yes | `GLIBC_2.4` | — | missing | missing |
| `erfcf` | yes | `GLIBC_2.4` | — | missing | missing |
| `tgammaf` | yes | `GLIBC_2.4` | — | missing | missing |
| `lgammaf` | yes | `GLIBC_2.4` | — | missing | missing |
| `nearbyintf` | yes | `GLIBC_2.4` | — | missing | missing |
| `rintf` | yes | `GLIBC_2.4` | — | missing | missing |
| `roundf` | yes | `GLIBC_2.4` | — | missing | missing |
| `truncf` | yes | `GLIBC_2.4` | — | missing | missing |
| `hypotf` | yes | `GLIBC_2.4` | — | missing | missing |
| `remainderf` | yes | `GLIBC_2.4` | — | missing | missing |
| `copysignf` | yes | `GLIBC_2.4` | — | missing | missing |
| `nextafterf` | yes | `GLIBC_2.4` | — | missing | missing |
| `fdimf` | yes | `GLIBC_2.4` | — | missing | missing |
| `fmaxf` | yes | `GLIBC_2.4` | — | missing | missing |
| `fminf` | yes | `GLIBC_2.4` | — | missing | missing |
| `ilogbf` | yes | `GLIBC_2.4` | — | missing | missing |
| `scalbnf` | yes | `GLIBC_2.4` | — | missing | missing |
| `scalblnf` | yes | `GLIBC_2.4` | — | missing | missing |
| `lrintf` | yes | `GLIBC_2.4` | — | missing | missing |
| `lroundf` | yes | `GLIBC_2.4` | — | missing | missing |
| `llrintf` | yes | `GLIBC_2.4` | — | missing | missing |
| `llroundf` | yes | `GLIBC_2.4` | — | missing | missing |
| `remquof` | yes | `GLIBC_2.4` | — | missing | missing |
| `nexttowardf` | yes | `GLIBC_2.4` | — | missing | missing |
| `fmaf` | yes | `GLIBC_2.4` | — | missing | missing |
| `nanf` | yes | `GLIBC_2.4` | — | missing | missing |
| `cacosf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `casinf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `catanf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `cacoshf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `casinhf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `catanhf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `ccosf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `csinf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `ctanf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `ccoshf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `csinhf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `ctanhf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `cexpf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `clogf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `cpowf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `csqrtf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `cabsf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `cargf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `conjf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `cprojf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `crealf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `cimagf` | yes | `GLIBC_2.4` | — | yes | not applicable |
| `acos` | yes | `GLIBC_2.4` | — | yes | yes |
| `asin` | yes | `GLIBC_2.4` | — | yes | yes |
| `atan` | yes | `GLIBC_2.4` | — | yes | yes |
| `cos` | yes | `GLIBC_2.4` | — | yes | yes |
| `sin` | yes | `GLIBC_2.4` | — | yes | yes |
| `tan` | yes | `GLIBC_2.4` | — | yes | yes |
| `cosh` | yes | `GLIBC_2.4` | — | yes | yes |
| `sinh` | yes | `GLIBC_2.4` | — | yes | yes |
| `tanh` | yes | `GLIBC_2.4` | — | yes | yes |
| `exp` | yes | `GLIBC_2.4` | — | yes | yes |
| `log` | yes | `GLIBC_2.4` | — | yes | yes |
| `log10` | yes | `GLIBC_2.4` | — | yes | yes |
| `sqrt` | yes | `GLIBC_2.4` | — | yes | yes |
| `ceil` | yes | `GLIBC_2.4` | — | yes | yes |
| `floor` | yes | `GLIBC_2.4` | — | yes | yes |
| `fabs` | yes | `GLIBC_2.4` | — | yes | yes |
| `atan2` | yes | `GLIBC_2.4` | — | yes | yes |
| `pow` | yes | `GLIBC_2.4` | — | yes | yes |
| `fmod` | yes | `GLIBC_2.4` | — | yes | yes |
| `frexp` | yes | `GLIBC_2.4` | — | yes | yes |
| `ldexp` | yes | `GLIBC_2.4` | — | yes | yes |
| `modf` | yes | `GLIBC_2.4` | — | yes | yes |
| `acosh` | yes | `GLIBC_2.4` | — | missing | missing |
| `asinh` | yes | `GLIBC_2.4` | — | missing | missing |
| `atanh` | yes | `GLIBC_2.4` | — | missing | missing |
| `exp2` | yes | `GLIBC_2.4` | — | missing | missing |
| `expm1` | yes | `GLIBC_2.4` | — | missing | missing |
| `log1p` | yes | `GLIBC_2.4` | — | missing | missing |
| `log2` | yes | `GLIBC_2.4` | — | missing | missing |
| `logb` | yes | `GLIBC_2.4` | — | missing | missing |
| `cbrt` | yes | `GLIBC_2.4` | — | missing | missing |
| `erf` | yes | `GLIBC_2.4` | — | missing | missing |
| `erfc` | yes | `GLIBC_2.4` | — | missing | missing |
| `tgamma` | yes | `GLIBC_2.4` | — | missing | missing |
| `lgamma` | yes | `GLIBC_2.4` | — | missing | missing |
| `nearbyint` | yes | `GLIBC_2.4` | — | missing | missing |
| `rint` | yes | `GLIBC_2.4` | — | missing | missing |
| `round` | yes | `GLIBC_2.4` | — | missing | missing |
| `trunc` | yes | `GLIBC_2.4` | — | missing | missing |
| `hypot` | yes | `GLIBC_2.4` | — | missing | missing |
| `remainder` | yes | `GLIBC_2.4` | — | missing | missing |
| `copysign` | yes | `GLIBC_2.4` | — | missing | missing |
| `nextafter` | yes | `GLIBC_2.4` | — | missing | missing |
| `fdim` | yes | `GLIBC_2.4` | — | missing | missing |
| `fmax` | yes | `GLIBC_2.4` | — | missing | missing |
| `fmin` | yes | `GLIBC_2.4` | — | missing | missing |
| `ilogb` | yes | `GLIBC_2.4` | — | missing | missing |
| `scalbn` | yes | `GLIBC_2.4` | — | missing | missing |
| `scalbln` | yes | `GLIBC_2.4` | — | missing | missing |
| `lrint` | yes | `GLIBC_2.4` | — | missing | missing |
| `lround` | yes | `GLIBC_2.4` | — | missing | missing |
| `llrint` | yes | `GLIBC_2.4` | — | missing | missing |
| `llround` | yes | `GLIBC_2.4` | — | missing | missing |
| `remquo` | yes | `GLIBC_2.4` | — | missing | missing |
| `nexttoward` | yes | `GLIBC_2.4` | — | missing | missing |
| `fma` | yes | `GLIBC_2.4` | — | missing | missing |
| `nan` | yes | `GLIBC_2.4` | — | missing | missing |
| `cacos` | yes | `GLIBC_2.4` | — | yes | yes |
| `casin` | yes | `GLIBC_2.4` | — | yes | yes |
| `catan` | yes | `GLIBC_2.4` | — | yes | yes |
| `cacosh` | yes | `GLIBC_2.4` | — | yes | yes |
| `casinh` | yes | `GLIBC_2.4` | — | yes | yes |
| `catanh` | yes | `GLIBC_2.4` | — | yes | yes |
| `ccos` | yes | `GLIBC_2.4` | — | yes | yes |
| `csin` | yes | `GLIBC_2.4` | — | yes | yes |
| `ctan` | yes | `GLIBC_2.4` | — | yes | yes |
| `ccosh` | yes | `GLIBC_2.4` | — | yes | yes |
| `csinh` | yes | `GLIBC_2.4` | — | yes | yes |
| `ctanh` | yes | `GLIBC_2.4` | — | yes | yes |
| `cexp` | yes | `GLIBC_2.4` | — | yes | yes |
| `clog` | yes | `GLIBC_2.4` | — | yes | yes |
| `cpow` | yes | `GLIBC_2.4` | — | yes | yes |
| `csqrt` | yes | `GLIBC_2.4` | — | yes | yes |
| `cabs` | yes | `GLIBC_2.4` | — | yes | yes |
| `carg` | yes | `GLIBC_2.4` | — | yes | yes |
| `conj` | yes | `GLIBC_2.4` | — | yes | yes |
| `cproj` | yes | `GLIBC_2.4` | — | yes | yes |
| `creal` | yes | `GLIBC_2.4` | — | yes | yes |
| `cimag` | yes | `GLIBC_2.4` | — | yes | yes |
| `acosl` | hidden | `GLIBC_2.4` | acos | yes | missing |
| `asinl` | hidden | `GLIBC_2.4` | asin | yes | missing |
| `atanl` | hidden | `GLIBC_2.4` | atan | yes | missing |
| `cosl` | hidden | `GLIBC_2.4` | cos | yes | missing |
| `sinl` | hidden | `GLIBC_2.4` | sin | yes | missing |
| `tanl` | hidden | `GLIBC_2.4` | tan | yes | missing |
| `coshl` | hidden | `GLIBC_2.4` | cosh | yes | missing |
| `sinhl` | hidden | `GLIBC_2.4` | sinh | yes | missing |
| `tanhl` | hidden | `GLIBC_2.4` | tanh | yes | missing |
| `expl` | hidden | `GLIBC_2.4` | exp | yes | missing |
| `logl` | hidden | `GLIBC_2.4` | log | yes | missing |
| `log10l` | hidden | `GLIBC_2.4` | log10 | yes | missing |
| `sqrtl` | hidden | `GLIBC_2.4` | sqrt | yes | missing |
| `ceill` | hidden | `GLIBC_2.4` | ceil | yes | missing |
| `floorl` | hidden | `GLIBC_2.4` | floor | yes | missing |
| `fabsl` | hidden | `GLIBC_2.4` | fabs | yes | missing |
| `atan2l` | hidden | `GLIBC_2.4` | atan2 | yes | missing |
| `powl` | hidden | `GLIBC_2.4` | pow | yes | missing |
| `fmodl` | hidden | `GLIBC_2.4` | fmod | yes | missing |
| `frexpl` | hidden | `GLIBC_2.4` | frexp | yes | missing |
| `ldexpl` | hidden | `GLIBC_2.4` | ldexp | yes | missing |
| `modfl` | hidden | `GLIBC_2.4` | modf | yes | missing |
| `acoshl` | hidden | `GLIBC_2.4` | acosh | missing | missing |
| `asinhl` | hidden | `GLIBC_2.4` | asinh | missing | missing |
| `atanhl` | hidden | `GLIBC_2.4` | atanh | missing | missing |
| `exp2l` | hidden | `GLIBC_2.4` | exp2 | missing | missing |
| `expm1l` | hidden | `GLIBC_2.4` | expm1 | missing | missing |
| `log1pl` | hidden | `GLIBC_2.4` | log1p | missing | missing |
| `log2l` | hidden | `GLIBC_2.4` | log2 | missing | missing |
| `logbl` | hidden | `GLIBC_2.4` | logb | missing | missing |
| `cbrtl` | hidden | `GLIBC_2.4` | cbrt | missing | missing |
| `erfl` | hidden | `GLIBC_2.4` | erf | missing | missing |
| `erfcl` | hidden | `GLIBC_2.4` | erfc | missing | missing |
| `tgammal` | hidden | `GLIBC_2.4` | tgamma | missing | missing |
| `lgammal` | hidden | `GLIBC_2.4` | lgamma | missing | missing |
| `nearbyintl` | hidden | `GLIBC_2.4` | nearbyint | missing | missing |
| `rintl` | hidden | `GLIBC_2.4` | rint | missing | missing |
| `roundl` | hidden | `GLIBC_2.4` | round | missing | missing |
| `truncl` | hidden | `GLIBC_2.4` | trunc | missing | missing |
| `hypotl` | hidden | `GLIBC_2.4` | hypot | missing | missing |
| `remainderl` | hidden | `GLIBC_2.4` | remainder | missing | missing |
| `copysignl` | hidden | `GLIBC_2.4` | copysign | missing | missing |
| `nextafterl` | hidden | `GLIBC_2.4` | nextafter | missing | missing |
| `fdiml` | hidden | `GLIBC_2.4` | fdim | missing | missing |
| `fmaxl` | hidden | `GLIBC_2.4` | fmax | missing | missing |
| `fminl` | hidden | `GLIBC_2.4` | fmin | missing | missing |
| `ilogbl` | hidden | `GLIBC_2.4` | ilogb | missing | missing |
| `scalbnl` | hidden | `GLIBC_2.4` | scalbn | missing | missing |
| `scalblnl` | hidden | `GLIBC_2.4` | scalbln | missing | missing |
| `lrintl` | hidden | `GLIBC_2.4` | lrint | missing | missing |
| `lroundl` | hidden | `GLIBC_2.4` | lround | missing | missing |
| `llrintl` | hidden | `GLIBC_2.4` | llrint | missing | missing |
| `llroundl` | hidden | `GLIBC_2.4` | llround | missing | missing |
| `remquol` | hidden | `GLIBC_2.4` | remquo | missing | missing |
| `nexttowardl` | hidden | `GLIBC_2.4` | nexttoward | missing | missing |
| `fmal` | hidden | `GLIBC_2.4` | fma | missing | missing |
| `nanl` | hidden | `GLIBC_2.4` | nan | missing | missing |
| `cacosl` | hidden | `GLIBC_2.4` | cacos | yes | not applicable |
| `casinl` | hidden | `GLIBC_2.4` | casin | yes | not applicable |
| `catanl` | hidden | `GLIBC_2.4` | catan | yes | not applicable |
| `cacoshl` | hidden | `GLIBC_2.4` | cacosh | yes | not applicable |
| `casinhl` | hidden | `GLIBC_2.4` | casinh | yes | not applicable |
| `catanhl` | hidden | `GLIBC_2.4` | catanh | yes | not applicable |
| `ccosl` | hidden | `GLIBC_2.4` | ccos | yes | not applicable |
| `csinl` | hidden | `GLIBC_2.4` | csin | yes | not applicable |
| `ctanl` | hidden | `GLIBC_2.4` | ctan | yes | not applicable |
| `ccoshl` | hidden | `GLIBC_2.4` | ccosh | yes | not applicable |
| `csinhl` | hidden | `GLIBC_2.4` | csinh | yes | not applicable |
| `ctanhl` | hidden | `GLIBC_2.4` | ctanh | yes | not applicable |
| `cexpl` | hidden | `GLIBC_2.4` | cexp | yes | not applicable |
| `clogl` | hidden | `GLIBC_2.4` | clog | yes | not applicable |
| `cpowl` | hidden | `GLIBC_2.4` | cpow | yes | not applicable |
| `csqrtl` | hidden | `GLIBC_2.4` | csqrt | yes | not applicable |
| `cabsl` | hidden | `GLIBC_2.4` | cabs | yes | not applicable |
| `cargl` | hidden | `GLIBC_2.4` | carg | yes | not applicable |
| `conjl` | hidden | `GLIBC_2.4` | conj | yes | not applicable |
| `cprojl` | hidden | `GLIBC_2.4` | cproj | yes | not applicable |
| `creall` | hidden | `GLIBC_2.4` | creal | yes | not applicable |
| `cimagl` | hidden | `GLIBC_2.4` | cimag | yes | not applicable |
