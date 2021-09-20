MAINFILE = arit2
PACKAGE = Arit2
MYNAME = JohnDoe

ifndef ANTLR4
$(error variable ANTLR4 is not set)
endif

$(PACKAGE)Listener.py $(PACKAGE)Lexer.py $(PACKAGE)Lexer.tokens $(PACKAGE)Parser.py $(PACKAGE).tokens: $(PACKAGE).g4
	$(ANTLR4) $< -Dlanguage=Python3

main-deps: $(PACKAGE)Lexer.py $(PACKAGE)Parser.py

#use pytest !!

run: $(MAINFILE).py main-deps
	python3 $<

TESTFILE=tests/test01.txt

print-tree: $(MAINFILE).py main-deps
	python3 $< $(TESTFILE) --debug

#Only if you have a full java distribution

$(PACKAGE).java: $(PACKAGE).g4
	$(ANTLR4)  $<
$(PACKAGE).class: $(PACKAGE).java
	javac $(PACKAGE)*.java
grun-gui: $(PACKAGE).class $(TESTFILE)
	java org.antlr.v4.gui.TestRig $(PACKAGE) prog -gui $(TESTFILE)



tests: test_ariteval.py main-deps
	python3 -m pytest -v $< 

tar: clean
	dir=$$(basename "$$PWD") && cd .. && \
	tar cvfz "$$dir.tgz" --exclude="*.riscv" --exclude=".git" --exclude=".pytest_cache"  \
	--exclude="htmlcov" "$$dir"

clean:
	rm -rf *~ $(PACKAGE)*.py $(PACKAGE)*.pyc *.tokens  __pycache* .cache *.interp *.java *.class
