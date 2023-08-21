# $Id$
me:= $(firstword $(MAKEFILE_LIST))

# Prints usage message and exits.
perl_usage=\
  BEGIN {\
    $$/ = "";\
    print "Usage: ${MAKE} -f ${me} TARGET";\
    print "Maintainer\047s makefile; the following targets are supported:";\
    print "";\
  }\
  /\#\s([^\n]+)\n(\.PHONY:|SC_RULES\+=)\s([\w-]+)\n/ and do {\
    my $$tgt = $$3;\
    my $$doc = $$1;\
    printf ("  %-20s  %s\n", $$tgt, $$doc);\
  };\
  END { print ""; }\
  ${NULL}

.PHONY: usage
usage:
	@perl -wnle '${perl_usage}' ${MAKEFILE_LIST}

CHECK_DEPS?= htmlcov-clean
CHECK_ISORT?= yes
CHECK_MYPY?= yes
COVERAGERC?= .coveragerc
DOCS_SRC?= docs
DOCS_TGT?= .docs
DOCS_TGT_BRANCH?= gh-pages
FLAKE8RC?= .flake8rc
ISORT_OPTIONS?= --check --diff
MANIFEST_IN?= Manifest.in
MANIFEST_IN_GIT_LS_FILES_PATHSPEC?=
MYPY_OPTIONS?= --show-error-context --show-error-codes
PERL?= perl
PYTEST_INI?= pytest.ini
PYTEST_OPTIONS?= -x
PYTHON?= python
TESTS?= tests
TOX_INI?= tox.ini

include Makefile.conf

CHECK_DEPS+= $(if $(filter yes,${CHECK_ISORT}),check-isort)
CHECK_DEPS+= $(if $(filter yes,${CHECK_MYPY}),check-mypy)
PYTEST_OPTIONS+= $(if $(filter yes,${CHECK_MYPY}),--mypy)

# run testsuite
.PHONY: check
check: ${CHECK_DEPS}
	pytest ${PYTEST_OPTIONS}

.PHONY: check-isort
check-isort:
	${PYTHON} -m isort ${ISORT_OPTIONS} ${PACKAGE} ${TESTS}

.PHONY: check-mypy
check-mypy:
	${PYTHON} -m mypy ${MYPY_OPTIONS} ${PACKAGE} ${TESTS}

# check copyright
.PHONY: check-copyright
check-copyright: check-copyright-python

.PHONY: check-copyright-python
check-copyright-python:
	@${CHECK_COPYRIGHT} `git ls-files '${PACKAGE}/*.py' '${TESTS}/*.py'`

CHECK_COPYRIGHT= ${PERL} -s -0777 -wnle '${perl_check_copyright}'
perl_check_copyright:=\
  BEGIN {\
    $$p = "\# " if !defined $$p;\
    $$q = $$p if !defined $$q;\
    $$h = "${COPYRIGHT}" if !defined $$h;\
    $$l = "SPDX-License-Identifier: ${LICENSE}" if !defined $$l;\
    $$regex = qr(\Q$$p\ECopyright \(C\) (20\d\d)(-(20\d\d))? \Q$$h\E\n\Q$$q$$l\E);\
    sub guess_year {\
      my $$date =\
        `git log --diff-filter=$$_[0] --follow --format=%as -1 -- $$ARGV`\
        || `date -I`;\
      $$date =~ /^(\d\d\d\d)/s;\
      return $$1;\
    }\
    $$errcnt = 0;\
    sub put_error {\
      warn("error:$$ARGV: $$_[0]\n");\
      $$errcnt++;\
    }\
  }\
  if (/$$regex/m) {\
    my $$start = $$1;\
    my $$end = $$3 if defined $$3;\
    my $$exp_start = guess_year("A");\
    if ($$start ne $$exp_start) {\
      put_error("bad start year: expected $$exp_start, got $$start");\
    } else {\
      my $$exp_end = guess_year("M");\
      if ($$exp_end eq $$exp_start) {\
        if (defined $$end) {\
          put_error("bad end year: expected none, got $$end");\
        }\
      } else {\
        if (!defined $$end) {\
          put_error("bad end year: expected $$exp_end, got none");\
        }\
      }\
    }\
  } else {\
    put_error("bad or missing license tag");\
  }\
  END { exit($$errcnt); }\
  ${NULL}

# remove generated files
.PHONY: clean
clean: docs-clean htmlcov-clean
	-${PYTHON} setup.py clean --all

.PHONY: htmlcov-clean
htmlcov-clean:
	-rm -rf ./htmlcov

# build docs
.PHONY: docs
docs:
	${MAKE} -C ./${DOCS_SRC} html\
	 PACKAGE='${PACKAGE}'\
	 COPYRIGHT='${COPYRIGHT}'\
	 COPYRIGHT_START_YEAR='${COPYRIGHT_START_YEAR}'
	@echo 'Index: file://${PWD}/${DOCS_SRC}/_build/html/index.html'

.PHONY: docs-clean
docs-clean:
	${MAKE} -C ./${DOCS_SRC} clean
	-rm -rf ./${DOCS_SRC}/generated

# initialize docs branch
.PHONY: docs-init
docs-init:
	if ! test -d ${DOCS_TGT}; then\
	 mkdir -p ${DOCS_TGT};\
	 cd ${DOCS_TGT};\
	 git init;\
	 git checkout --orphan ${DOCS_TGT_BRANCH};\
	 git remote add origin ${URL_SSH};\
	fi
	-cd ${DOCS_TGT} && git pull origin ${DOCS_TGT_BRANCH}

# build docs and copy them to ${DOCS_TGT}
.PHONY: docs-publish
docs-publish: docs-clean docs
	@if ! test -d ./${DOCS_TGT}; then\
	 echo 1>&2 "*** ERROR: ${DOCS_TGT} does not exist";\
	 exit 1;\
	fi
	touch ./${DOCS_TGT}/.nojekyll
	cp -a ./${DOCS_SRC}/_build/html/* ./${DOCS_TGT}
	cd ${DOCS_TGT} && git add .
	cd ${DOCS_TGT} && git commit -m 'Update docs'
	cd ${DOCS_TGT} && git push origin gh-pages

# run all gen-* targets
.PHONY: gen-all
gen-all: gen-coveragerc gen-flake8rc gen-manifest-in gen-pytest-ini gen-tox-ini

# generate .coveragerc
.PHONY: gen-coveragerc
gen-coveragerc:
	@echo 'generating ${COVERAGERC}'
	@echo '[report]' >${COVERAGERC}
	@echo 'exclude_lines =' >>${COVERAGERC}
	@echo '    pragma: no cover' >>${COVERAGERC}
	@echo '    def __repr__' >>${COVERAGERC}
	@echo '    def __str__' >>${COVERAGERC}
	@echo '    raise AssertionError' >>${COVERAGERC}
	@echo '    raise NotImplementedError' >>${COVERAGERC}
	@echo '    if 0:' >>${COVERAGERC}
	@echo '    if __name__ == .__main__.:' >>${COVERAGERC}
	@echo '    class .*\bProtocol\):' >>${COVERAGERC}
	@echo '    @(abc\.)?abstractmethod' >>${COVERAGERC}
	@echo '    should_not_get_here' >>${COVERAGERC}

# generate .flake8rc
.PHONY: gen-flake8rc
gen-flake8rc:
	@echo 'generating ${FLAKE8RC}'
	@echo '[flake8]' >${FLAKE8RC}
	@echo 'ignore = E741,F403,F405,W503' >>${FLAKE8RC}

# generate Manifest.in
.PHONY: gen-manifest-in
gen-manifest-in:
	@echo 'generating ${MANIFEST_IN}'
	@git ls-files ${MANIFEST_IN_GIT_LS_FILES_PATHSPEC} |\
	 sed 's,\(.*\),include \1,' >${MANIFEST_IN}

# generate pytest.ini
.PHONY: gen-pytest-ini
gen-pytest-ini:
	@echo 'generating ${PYTEST_INI}'
	@echo '[pytest]' >${PYTEST_INI}
	@echo 'addopts = -ra --cov=${PACKAGE} --cov-report=html' >>${PYTEST_INI}
	@echo 'testpaths = ${TESTS}' >>${PYTEST_INI}

# generate tox.ini
.PHONY: gen-tox-ini
gen-tox-ini:
	@echo 'generating ${TOX_INI}'
	@echo '[tox]' >${TOX_INI}
	@echo 'envlist = lint, type, py{39,310,311}' >>${TOX_INI}
	@echo 'skip_missing_interpreters = true' >>${TOX_INI}
	@echo '' >>${TOX_INI}
	@echo '[testenv]' >>${TOX_INI}
	@echo 'allowlist_externals = py.test' >>${TOX_INI}
	@echo 'commands = py.test {posargs}' >>${TOX_INI}
	@echo 'extras = test' >>${TOX_INI}

# refresh idents
.PHONY: ident
ident:
	for f in `grep ident .gitattributes | sed 's/\s*ident$$//'`; do\
	  touch $$f; git checkout $$f; echo "`head -n1 $$f` $$f";\
	done

# install package
.PHONY: install
install:
	pip install -e .

# install doc-build and test dependencies
.PHONY: install-deps
install-deps:
	pip install -e '.[docs]'
	pip install -e '.[tests]'

# uninstall package
.PHONY: uninstall
uninstall:
	${PYTHON} setup.py develop -u
