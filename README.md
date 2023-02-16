# Equation Modeling Language Solver/Compiler API
This mess is a heavily modified version of [fourFN](https://github.com/pyparsing/pyparsing/blob/master/examples/fourFn.py), a calculator example for [PyParsing](https://pypi.org/project/pyparsing/) package. It is a mess, but it works. There will be no further development of this version, and it will be retired as soon as version 2.0 has matured. The API is built using [Flask](https://pypi.org/project/Flask/).

Notably, this version does support standard math functions from Python's library, user defined functions, and if-else statements:
```
function fact(n:fn){
    if( n <= 1){
        fn = n
    } else {
        fn = n*fact(n-1)
    }
}

a = fact(3)
```
