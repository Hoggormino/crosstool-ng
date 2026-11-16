"""Owned declaration/link probes for the C++17 and C99 math interfaces."""
PRECISIONS = [('float', 'f'), ('double', ''), ('long double', 'l')]

# name, arguments, return type (T is the tested precision), standard group.
SCALAR = []
for names, args, result, group in [
    ('acos asin atan cos sin tan cosh sinh tanh exp log log10 sqrt ceil floor fabs', 'x', 'T', 'classic'),
    ('atan2 pow fmod', 'x,y', 'T', 'classic'),
    ('frexp', 'x,&exponent', 'T', 'classic'),
    ('ldexp', 'x,exponent', 'T', 'classic'),
    ('modf', 'x,&part', 'T', 'classic'),
    ('acosh asinh atanh exp2 expm1 log1p log2 logb cbrt erf erfc tgamma lgamma nearbyint rint round trunc', 'x', 'T', 'c99'),
    ('hypot remainder copysign nextafter fdim fmax fmin', 'x,y', 'T', 'c99'),
    ('ilogb', 'x', 'int', 'c99'),
    ('scalbn', 'x,exponent', 'T', 'c99'),
    ('scalbln', 'x,long_exponent', 'T', 'c99'),
    ('lrint lround', 'x', 'long', 'c99'),
    ('llrint llround', 'x', 'long long', 'c99'),
    ('remquo', 'x,y,&quotient', 'T', 'c99'),
    ('nexttoward', 'x,direction', 'T', 'c99'),
    ('fma', 'x,y,z', 'T', 'c99'),
    ('nan', '""', 'T', 'c99'),
]:
    SCALAR.extend((name, args, result, group) for name in names.split())

CLASSIFY = 'fpclassify isfinite isinf isnan isnormal signbit'.split()
COMPARE = 'isgreater isgreaterequal isless islessequal islessgreater isunordered'.split()
COMPLEX_C = 'cacos casin catan cacosh casinh catanh ccos csin ctan ccosh csinh ctanh cexp clog cpow csqrt cabs carg conj cproj creal cimag'.split()
COMPLEX_CPP = 'acos asin atan acosh asinh atanh cos cosh exp log log10 sin sinh sqrt tan tanh abs arg norm real imag conj proj polar pow'.split()
SPECIAL = []
for names, args in [
    ('assoc_laguerre assoc_legendre sph_legendre', 'order,degree,x'),
    ('hermite laguerre legendre sph_bessel sph_neumann', 'order,x'),
    ('beta cyl_bessel_i cyl_bessel_j cyl_bessel_k cyl_neumann ellint_1 ellint_2', 'x,y'),
    ('comp_ellint_1 comp_ellint_2 expint riemann_zeta', 'x'),
    ('comp_ellint_3', 'x,y'), ('ellint_3', 'x,y,z'),
]:
    SPECIAL.extend((name, args) for name in names.split())
FENV = {'feclearexcept':'FE_ALL_EXCEPT', 'fegetexceptflag':'&flags,FE_ALL_EXCEPT',
        'feraiseexcept':'FE_ALL_EXCEPT', 'fesetexceptflag':'&flags,FE_ALL_EXCEPT',
        'fetestexcept':'FE_ALL_EXCEPT', 'fegetround':'', 'fesetround':'FE_TONEAREST',
        'fegetenv':'&env', 'feholdexcept':'&env', 'fesetenv':'&env', 'feupdateenv':'&env'}

def catalog():
    cases = []
    def add(section, family, form, precision, expression, expected, symbol=None):
        cases.append(dict(id=f'case-{len(cases):04d}', section=section, family=family,
                          form=form, precision=precision, expression=expression,
                          expected=expected, c_symbol_hint=symbol))
    for typ, suffix in PRECISIONS:
        for name, args, result, group in SCALAR:
            expected = typ if result == 'T' else result
            symbol = name + suffix
            if name != 'nan':
                add('cmath', name, 'std_overload', typ, f'std::{name}({args})', expected, symbol)
            if suffix or name == 'nan':
                add('cmath', name, 'std_named', typ, f'std::{symbol}({args})', expected, symbol)
            add('cmath', name, 'global_cpp', typ, f'::{symbol}({args})', expected, symbol)
            add('math_c', name, 'c_header', typ, f'{symbol}({args})', expected, symbol)
        add('cmath', 'abs', 'std_overload', typ, 'std::abs(x)', typ)
        add('cmath', 'hypot3', 'std_overload', typ, 'std::hypot(x,y,z)', typ)
        for name in CLASSIFY + COMPARE:
            args = 'x,y' if name in COMPARE else 'x'
            result = 'int' if name == 'fpclassify' else 'bool'
            add('cmath', name, 'std_overload', typ, f'std::{name}({args})', result)
            add('math_c', name, 'c_macro', typ, f'{name}({args})', 'int')
        for name in COMPLEX_C:
            args = 'a,b' if name == 'cpow' else 'a'
            expected = typ if name in ('cabs','carg','creal','cimag') else typ+' _Complex'
            add('complex_c', name, 'c_header', typ, f'{name+suffix}({args})', expected, name+suffix)
        for name in COMPLEX_CPP:
            args = 'a,b' if name == 'pow' else 'x,y' if name == 'polar' else 'a'
            expected = typ if name in ('abs','arg','norm','real','imag') else f'std::complex<{typ}>'
            add('complex_cpp', name, 'std_complex', typ, f'std::{name}({args})', expected)
        for name, args in SPECIAL:
            add('cmath', name, 'std_special', typ, f'std::{name}({args})', typ)
            if suffix:
                add('cmath', name, 'std_special_named', typ, f'std::{name+suffix}({args})', typ)
    for name, args, result, group in SCALAR:
        if name in ('modf','nan'): continue
        expected = 'double' if result == 'T' else result
        add('cmath', name, 'std_integer', 'int', f'std::{name}({args})', expected)
    for name, args in FENV.items():
        add('cfenv', name, 'std_fenv', 'double', f'std::{name}({args})', 'int', name)
        add('fenv_c', name, 'c_header', 'double', f'{name}({args})', 'int', name)
    for typ in ('float_t','double_t'):
        add('cmath', typ, 'std_type', 'double', f'sizeof(std::{typ})', 'std::size_t')
        add('math_c', typ, 'c_type', 'double', f'sizeof({typ})', 'size_t')
    # Explicit prototypes are diagnostic probes, never changes to target headers.
    for original in list(cases):
        if original['section'] not in ('math_c','complex_c') or original['form'] != 'c_header': continue
        case = dict(original, id=f'case-{len(cases):04d}', form='abi_decl_c')
        args = case['expression'].split('(',1)[1][:-1]
        typ = case['precision'];ct = typ+' _Complex'
        mapping = dict(x=typ,y=typ,z=typ,exponent='int',long_exponent='long',direction='long double',a=ct,b=ct)
        mapping.update({'&exponent':'int*','&quotient':'int*','&part':typ+'*','""':'const char*'})
        params = ','.join(mapping[arg] for arg in args.split(','))
        case['prototype'] = (f'extern {case["expected"]} owned_symbol({params}) __asm__("{case["c_symbol_hint"]}");\n'
                             f'{case["expected"]} (* volatile owned_function)({params}) = &owned_symbol;\n')
        case['expression'] = 'owned_function('+args+')'
        cases.append(case)
    return cases

HEADERS = {'cmath': '#include <cmath>\n#include <type_traits>\n#include <cstddef>\n',
           'complex_cpp': '#include <complex>\n#include <type_traits>\n',
           'cfenv': '#include <cfenv>\n#include <type_traits>\n',
           'math_c': '#include <math.h>\n#include <stddef.h>\n',
           'complex_c': '#include <complex.h>\n', 'fenv_c': '#include <fenv.h>\n'}

def body(case, check_type=True):
    typ = case['precision'];cpp = case['section'] in ('cmath','complex_cpp','cfenv')
    code = f'volatile {typ} owned_x=0.5, owned_y=0.25, owned_z=0.75;\nint main(void) {{\n'
    code += f'{typ} x=owned_x,y=owned_y,z=owned_z,part=0; int exponent=2,quotient=0; long long_exponent=2; long double direction=0.75L; unsigned order=2,degree=1;\n'
    if case['section'] == 'complex_cpp': code += f'std::complex<{typ}> a(x,y),b(y,z);\n'
    if case['section'] == 'complex_c': code += f'{typ} _Complex a=x+y*I,b=y+z*I;\n'
    if case['section'] in ('cfenv','fenv_c'):
        ns = 'std::' if cpp else ''
        code += ns+'fenv_t env={0}; '+ns+'fexcept_t flags={0};\n'
    expr = case['expression']
    if cpp and check_type:
        code += f'static_assert(std::is_same<decltype({expr}), {case["expected"]}>::value,"return_type_mismatch");\n'
    code += f'volatile {case["expected"]} result = {expr}; (void)result; return 0;\n}}\n'
    return code
