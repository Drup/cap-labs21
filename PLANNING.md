# Planning of the compilation course (CAP, Compilation and Program Analysis)
_Academic first semester 2021-2022_

* MCC (final grade computation) : 
```
let ccgrade = average(Lab3, Lab5, Lab6, partial)
in (finalnote + ccgrade)/2
```
* The partial exam is this academic year replaced by a written housework ("DM").

* The final exam will be done "physically" in January. It will last three (3) hours. No authorized documents.

# Week 1: 

- :book: First Course session: Tuesday 7/9/2021, 15h45-17h45. Amphi B (Gabriel Radanne)
  
  * Introduction: [transparents](course/capmif_cours01_intro_et_archi.pdf).
  * ISA [ref pdf RISCV](course/riscv_isa.pdf).
  * [Demo Assembly](course/demo20.s).
  * Lexing, Parsing, [slides](course/capmif_cours02_lexing_parsing.pdf).
  * [Demo Parsing](course/ANTLRExamples.tar.xz).

- :book: Second Course session: Friday 10/9/2021, 10:15. Amphi B (Gabriel Radanne)

  * Interpreters [slides in english](course/capmif_cours03_interpreters.pdf).
  * [Demo files](course/ANTLRExamples.tar.xz)
  * [Grammar exercise](course/TD2.pdf).

- :rocket: Additional ressources (mainly in english)

	* A nice YT video on [structural induction](https://www.youtube.com/watch?v=2o3EzvfgTiQ) by F. Pereira.
	* Fernando Pereira's other videos on operational semantics : [video1](https://www.youtube.com/watch?v=bOzbRhXvtlY), [video2](https://www.youtube.com/watch?v=aiBKOuM5iEA)

# Week 2:

- :hammer: Lab 1: Tuesday 14/9/2021, 15h45-17h45. Salle E001 (Nicolas Chappe, Remi Di Guardia)

    * Introduction to RISCV [TP01](TP01/tp1.pdf)
    * Code in [TP01/](TP01/)
    * ISA [ref pdf RISCV](course/riscv_isa.pdf).

- :book: Third Course session: Friday 17/9/2021, 10:15. Amphi B (Ludovic Henrio)

    * Formal Semantics [slides](course/cap_cours03b_semantics.pdf)

# Week 3:

- :hammer: Lab 2: Tuesday 21/9/2021, 15h45-17h45. Salle E001 (Nicolas Chappe, Remi Di Guardia)

    * Lexing & Parsing with ANTLR4 [TP02](TP02/tp2.pdf)
    * Code in [TP02/](TP02/).
    
- :book: Fourth Course session: Friday 24/9/2021, 10:15. Amphi B (Ludovic Henrio)
    
    * Typing [slides](course/CAP_cours04_typing.pdf)

# Week 4:

- :hammer: Lab 3: Tuesday 28/9/2021, 15h45-17h45. Salle E001 (Nicolas Chappe, Remi Di Guardia)

    * Interpreter & Typer [TP03](TP03/tp3.pdf)
    * Code in [TP03/](TP03/) and [MiniC/TP03/](MiniC/TP03/).
    * Graded lab due on https://etudes.ens-lyon.fr/course/view.php?id=4814 before 2021-10-04 23:59

- :book: Fifth Course session: Friday 1/10/2021, 10:15. Amphi B (Gabriel Radanne)

  * 3 address code generation [slides in english](course/capmif_cours05_3ad_codegen.pdf)

# Week 5:

- :hammer: Lab 4: Tuesday 5/10/2021, 15h45-17h45. Salle E001 (Nicolas Chappe, Remi Di Guardia)

    * Syntax directed code generation [TP04](MiniC/TP04/tp4.pdf)
    * Code in [MiniC/TP04/](MiniC/TP04/).

- :book: Sixth Course session: Friday 8/10/2021, 10:15. Amphi B (Gabriel Radanne)

    * Intermediate Representation: CFG [slides in english](course/capmif_cours06_irs.pdf)

# Week 6:

- :book: Seventh Course session: Tuesday 12/10/2021, 15:45. Amphi B (Gabriel Radanne)

    * SSA [slides in english](course/cap_cours06a_ssa.pdf)

- :book: Eight Course session: Friday 15/10/2021, 10:15. Amphi B (Gabriel Radanne)

    * Register allocation [slides in english](course/cap_cours07_regalloc.pdf)

# Week 7:

- :hammer: Lab 5a: Tuesday 19/10/2021, 15h45-17h45. Salle E001 (Nicolas Chappe, Remi Di Guardia)

    * Control Flow Graph in SSA Form [TP05a](MiniC/TP05/tp5a.pdf)
    * Code in [MiniC/TP05/](MiniC/TP05/).

- :book: Nineth Course session: Friday 22/10/2021, 10:15. Amphi B (Gabriel Radanne)

    * Register allocation, 2nd part [slides in english](course/cap_cours07_regalloc.pdf)

# Week 8:

- :hammer: Lab 5b: Tuesday 26/10/2021, 15h45-17h45. Salles E001 (Nicolas Chappe) & 029 (Remi Di Guardia)

    * Smart Register Allocation [TP05b](MiniC/TP05/tp5b.pdf)
    * Code in [MiniC/TP05/](MiniC/TP05/).

- :book: Tenth Course session: Friday 29/10/2021, 10:15. Amphi B (Gabriel Radanne)

    * SSA for Fun and Optimisations, 2nd part [slides in english](course/cap_cours06b_ssa_optim.pdf)

# Week 9:

- :hammer: Lab 5: Tuesday 09/11/2021, 15h45-17h45. Salles E001 (Nicolas Chappe) & 029 (Remi Di Guardia)

    * Code in [MiniC/TP05/](MiniC/TP05/).

# Week 10:

- :book: Course session: Tuesday 16/11/2021 - 8:00. Salle MGN1.422 - UMPA - salle 435 (Ludovic Henrio)

    * Functions: code generation and typing [slides in english](course/2021-cap_cours09A_func_codegen_typing.pdf)

- :hammer: Lab 6(1/2): Tuesday 16/11/2021, 15h45-17h45. Salles E001 (Nicolas Chappe) & 029 (Remi Di Guardia)

    * Code generation for functions [TP06](MiniC/TP06/tp6.pdf)

- :book: Course session: Friday 19/11/2021 - 10:15. Amphi B (Ludovic Henrio)

    * Functions: semantics and safety [slides in english](course/2021-cap_cours09B_funsem.pdf)

# Week 11

- :hammer: Lab 6(2/2): Tuesday 23/11/2021, 15h45-17h45. Salles E001 (Nicolas Chappe) & 029 (Remi Di Guardia)

    * Code generation for functions [TP06](MiniC/TP06/tp6.pdf)

- :book: Course session: Friday 26/11/2021 - 10:15. Amphi B (Ludovic Henrio)

    * Parallelism 1/2 [slides in english](course/cap_cours10_parallelism.pdf)


# Week 12

- :hammer: Lab 6(3/2!): Tuesday 30/11/2021, 15h45-17h45. Salles E001 (Nicolas Chappe) & 029 (Remi Di Guardia)

    * Code generation for functions [TP06](MiniC/TP06/tp6.pdf)

- :book: Course session: Friday 3/12/2021 - 10:15. Amphi B (Ludovic Henrio)

    * Parallelism 2/2 [slides in english](course/cap_cours10_parallelism.pdf)


# Week 13

- :hammer: Lab 5c: Tuesday 7/12/2021, 15h45-17h45. Salles E001 (Nicolas Chappe) & 029 (Remi Di Guardia)

    * Optimisation under SSA form [TP05c](MiniC/TP05c/tp5c.pdf)
    * Code in [MiniC/TP05c/OptimSSA.py](MiniC/TP05c/OptimSSA.py)

- :hammer: Lab Futur: Friday 10/12/2021, 10h15-12h15. Salles E001 (Nicolas Chappe) & Grenat (Remi Di Guardia)

    * Futur [TP08](TP08/tp8.pdf)
    * Code in [TP08/MiniC-futures](TP08/MiniC-futures)


# !!! Homework !!!

- Homework is [here](DM/dm_cap.pdf) Deadline: 10/12/2021 10:15 (during the last lab) --  paper version (possibly printed)
