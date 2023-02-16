# Equation Modeling Language Solver/Compiler API
This is not what actually powers the [website](https://matrix.vlatur.com/) today. That unmaintainable and unmanageable spaghetti code is located in the main branch. The develop branch contains a much better planned out version 2.0. Unfortunately, I currently do not have the time to bring it to feature parity with the main branch and deploy it.

# Equation Modeling Language
The idea behind Equation Modeling Language is fairly simple - take C/C++ style grammar and use equations instead of assignments as the main building block. The equations will then be iteratively solved using Broyden's method to find the roots. The goal would be to use as much of the functionality of the underlying language (currently Python) as possible to have support for mathematical functions, arrays, user-defined functions, loops, conditional statements, etc. The loops and conditions would direct the flow of computations between different equation blocks, which contain equations, which contain variables, number literals, array elements, and function calls (user functions are essentially blocks of equations themselves). Even though the idea is simple, it results in a very powerful modeling tool for all sorts of equation-based modeling.

# The Program Structure
- The lexer and parser for this grammar are built using Lex and Yacc from [PLY](https://ply.readthedocs.io/en/latest/index.html) Python package. There is a great [documentation/guide](https://www.dabeaz.com/ply/ply.html) and a great book [lex & yacc](https://www.oreilly.com/library/view/lex-yacc/9781565920002/) which helped me tremendously to write my grammar.
- Each parsing rule has actions associated with them (Syntax-directed Translation). These rules build an Abstract Syntax Tree (AST) which contains different types of nodes like:
  - **EquationBlock** - contains all the logic associated with finding roots utilizing [scipy](https://pypi.org/project/scipy/) Python package
  - **Equation** - during the solution stage, computes the (LHS - RHS) and returns that value to the EquationBlock
  - **BinOp** - binary operator for "-", "+", "/", "*", and "^"
  - **FuncOp** - meant to hold data associated with function calls (still in development)
  - **NumNode** - number node; all numbers are doubles
  - **VarNode** - variable node
- All of the variable values are stored in a **DataStorage** class (symbol table)

# How It works
The program is essentially a compiler for Equation Modeling Language. Unlike a typical compiler, which produces an executable, this compiler produces a dictionary of variable values that solve the system of equations defined by the user.
- The parser builds an AST. During the construction of AST, algebraic expressions are simplified and some equations of type "variable = value" are marked as assignments. These equations do not take part in the following solution procedure.
- All variable values in **DataStorage** are populated using guess values (value is 1 if not provided)
- **EquationBlock** then attempts to iteratively solve the system of equations, modifying the values in **DataStorage** and getting back LHS - RHS values from each of the equations.
- A dictionary of variable values is produced and then sent out as a response.

# Learning Outcomes
This project was a great opportunity to learn about compilers. I have gained experience with Lex, Yacc, ASTs, and Python packages PLY and scipy.

# Possible Development
I think this is a great project for high-school students, scientific researchers, and anyone in between. I imagine that people could create packages for different classes of problems, i.e. physics, engineering, chemistry, thermodynamics, finance, and computer science, which will make solving problems and modeling real-world phenomena a lot easier.
