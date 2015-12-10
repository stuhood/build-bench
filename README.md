---
layout: default
---
# build-bench

A Benchmark setup for Java buildsystems.

See Github pages at: http://tkruse.github.io/build-bench

[![Build Status](https://travis-ci.org/tkruse/build-bench.svg)](https://travis-ci.org/tkruse/build-bench)

The different buildsystems are installed locally on demand by the makefiles.

Buildsystems:

* Apache Ant  (<http://ant.apache.org>)
* Gradle  (<https://gradle.org>)
* Apache Maven  (<http://maven.apache.org>)
* Apache Buildr (<http://buildr.apache.org>)
* Sbt  (<http://www.scala-sbt.org>)
* Leiningen  (<http://leiningen.org>)
* Buck  (<https://buckbuild.com>)
* Pants  (<https://pantsbuild.github.io>)
* Bazel  (<http://bazel.io>)

Also see [my notes](Buildsystems.md)

## Running

```bash
# to run all buildsystems
$ make

# to run all buildsystems freshly
$ make clean all

# to run for just selected buildsystems, e.g. maven vs. gradle:
$ make clean maven gradle

# to run for just selected buildsystems in particular versions
$ make clean maven3.3.3 gradle2.7
```

The process is configured using variables that can be changed, the configs folder has a `defauls.mk` file setting defaults, and some example files for different kinds of builds.

It is possible to run a custom Benchmark configuration using:

```bash
# to run specific configuration
$ make clean all CONFIG=configs/generated_multi.mk
```

## Prerequisites

* Java        (7 or 8, configure JAVA_HOME)
* bash        (the standard Ubuntu shell)
* GNU make    (should be present on any *nix)
* GNU time    (should be present on any *nix)
* Python      (2 or 3)
* jinja2      (if using templated sources, install via pip or apt-get)
* Ruby        (1 or 2, for Apache buildr, jruby should also work)

The whole setup is described [here](Design.md)

## Configuring Benchmarks

Custom configurations are loaded after the `defaults.mk` providing some convention over configuration. If present, a `custom.mk` in the project root will be loaded after `default.mk` but before specific configuration, allowing to override permanent defaults with your defaults.

## Motivation

While Maven and Gradle are used by most Java projects in the wild, there are many alternatives to choose from. Comparing those is difficult. This project is a setup to run a buildprocess for java projects using multiple buildsystems.

My main goal was to find out which buildsystem feature pays off under which circumstances (and under which it is irrelevant). As secondary independent goal is to get a feel for how much difference there is in performance for "realistic" isolated projects (like open-source projects). A comparison for huge mono-repo situations was not that interesting to me.

A single benchmark is driven by GNU make. The `Makefile` creates a `build` folder,
containing a folder structure for benchmarks. Subfolders follow the pattern `<benchmarkname>/<buildsystemname>`. Into those folders, Java source files and buildsystem specific files will be copied / generated. Then the buildsystem is invoked inside that folder and the time until completion is measured.

## Samples

The builds should work for any source tree that follows these conventions:

* Java 8 compliant code
* Java sources in src/main/java
* Test sources in src/test/java
* Other test resources in src/test/resources
* Tests written in JUnit4.11 compatible fashion, not requiring 4.12 (sbt issues)
* Test classes named *Test.java
* Abstract Test parent classes named *AbstractTest.java (to be excluded, some buildsystems fail else)
* Single module projects (as opposed to multi-project builds)
* No other dependencies than standard Java and JUnit4

## Output

Sample output: See http://tkruse.github.io/build-bench/commons-math

## Contributing

See [CONTRIBUTING](CONTRIBUTING.md)

## FAQ

### What influences performance?

JVM startup adds something like 3 seconds to the whole process. Several tools offer daemons to reduce this offset. Tools not written in JVM languages do not have this offset.

Parallel task execution: On machines with multiple cores, it may be possible to reduce build time by utilizing more than one CPU. However the build-time rarely is reduced by the number of CPUs. The overhead of finding out how to split tasks over several CPUs can eliminate benefits, and often there will be many dependencies that lead to tasks necessarily being build in sequence. Most buildtool will thus mostly offer to only build completely independent sub-modules in parallel. For single-module projects, no additional CPU is used then.
Some tasks may even only work when not run in parallel, so using parallel features also increases maintenance effort.

Compiler speed may differ for different compilers. The scala compiler and clojure compiler seemed slower than javac for compiling java sources.

Incremental re-compilation, meaning compiling only files that are affected by a change, can drastically reduce build times.

Incremental build steps beyond compilation help (e.g. Maven can compile incrementally, but not test incrementally).

Incremental builds for sub-module filesets. Several buildsystems can (re-)build only those submodules that have change, but cannot only (re-)build only half a submodule. Being able to incrementally rebuild smaller parts can speed up builds in specific situations.

Caching influences incremental builds. Several buildsystems have a simple caching strategy in that they will not run a task if the output still exist. This will improve performance for repeated builds.

Buck, Bazel and Pants were the only build system benchmarked here that offers advanced (true) caching of build results, in that the cache is an independent storage that maintains multiple versions of build results over time. This can dramatically reduce build times in many more situations than simple caching described before.

For large projects with plenty of subprojects and subtasks, performance can be gained by caching in a fine-grained way and reusing more previous artifacts. The example and setup used in this benchmark may not be optimal for any given buildsystem. In particular, Pants has some online examples defining plenty of smaller library targets for individual Java files, which might improve caching performance when rebuilding after a single java file changed (not sure what other advantage it could have).

### So which buildsystem should I use for Java projects?

It depends on what you need.

To choose, consider the following:

* Learning curve
* Maturity
* Performance (startup, parallelism, compiler, incremental builds, caching)
* Documentation
* Community size
* IDE support
* Plugin archives, integration with static code analysis, metrics, reports, etc.
* multi language support

### No really, which one should I use for Java projects?

Maven or Gradle are the default choice for most open-source Java projects and many businesses out there. Maven may still be more popular in the industry for stability, but Gradle has a stronger innovation drive. Both have hundreds of open-source plugins available, and both get special support from IDEs, Continuous integration servers, etc. I personally prefer Gradle and give some details about what I dislike about Maven below.

Buildr seems to be mostly similar to Gradle but written in Ruby, which offers some advantages and disadvantages. It does not seem to gain the kind of market share Gradle and Maven have established.

Ant is still being used, but it's unclear what advantages it offers. Maybe simplicity for creating many small unconventional tasks. Gant is built on top of ant and similar in purpose, but allowing to write in Groovy. Other buildsystems like make, rake or scons might be similar enough to ant, but they do not get further consideration here because they have little tradition for Java projects.

Leiningen and sbt are optimized (in usability) for Clojure and Scala respectively. If you only use Java, it probably does not pay off to use either of them, unless you wanted to learn / integrate those languages anyway.

Bazel and Pants are derived from Googles Blaze system optimized for huge monorepo corporate ecosystems, where thousands of projects with interdependencies are continuously build and deployed. Buck is used at Facebook, Pants at Twitter.
They shine in build speed and caching, but they require more developer attention and effort, because they are rule based, and have no high-level abstraction of a project object model like Gradle or Maven. And being still fairly new as open-source projects at this time, they do not have the mature support from other open-source tools. As an example, buck only lately got a feature to automatically download dependencies from central Maven repositories.
Since they have been used in a corporate setting where strict standards could be enforced, they are prone to detection of new bugs when being used in the wild by projects following a huge variety of conventions.

Buck is mainly targetted at building Java apps for Android, it is inspired by Blaze.

| Name      | Target                     | language   | Written in   | Since        | Support    | Caching    | Model |
| --------- | -------------------------- | ---------- | ------------ | ------------ | ---------- | ---------- | ----- |
| ant       | Java                       | XML        | Java         | 2000         | Apache     | None       | rules |
| maven     | Java (Scala, Ruby, C#)     | XML        | Java         | 2002         | Apache     | None       | POM   |
| gradle    | Java, Groovy (Scala, C++,) | Groovy     | Java, Groovy | 2007         | Gradleware | last build | POM   |
| buildr    | Java, Scala, Groovy        | Ruby       | Ruby         | 2010?        | Apache     | ?          | POM   |
| sbt       | Scala, Java                | Scala      | Scala        | 2010?        | ?          | ?          | POM   |
| leiningen | Clojure, Java              | Clojure    | Clojure      | 2009?        | ?          | ?          | POM   |
| buck      | Java (Android)             | Python-ish | Java, Python | 2012         | Facebook   | true cache | rules |
| bazel     | C++, Java, Python, Go      | Python-ish | C++, Java    | 2015 (2005?) | Google     | true cache | rules |
| pants     | Java, Scala, Python        | Python     | Python       | 2014 (2010)  | Twitter    | true cache | rules |

### Why are ant/sbt/leiningen so slow for clean testing of commons-math?

I do not know for sure. There must be some overhead not present in the other systems, maybe a new JVM process is started for each test.

Note that for sbt and leiningen, extra plugins were required to run JUnit tests written in Java. These buildsystems would specialize on tests written in Scala/Clojure, and the results here do not tell whether tests written in Scala or Clojure would have similar overheads.

### I get InstantiationExceptions with some buildsystem, what is going on?

java.lang.InstantiationException during tests is usually a sign that a TestRunner is trying to run a non-Testcase class (like abstract or util classes). Not all Buildsystems can cope well with that by default.

### Why GNU make?

I chose GNU make for this project because it is omnipresent in linux and very close to shell scripting.

### Why jinja2?

I needed some templating engine, and scripting in Python seemed the least effort. Jinja2 is popular and een around for a while. Mako and Genshi also seemed nice at a glance.

### Why commons-math?

I chose to test against commons-math because it is reasonably large, well tested, and has no dependencies outside the JDK. Other libraries working okay are commons-text, commons-io, commons-imaging, guava.

The main problems I had with commons-math was that the naming for the Testcases is not consistent. The commons-math ant file lists those rules:

```xml
    <include name="**/*Test.java"/>
    <include name="**/*TestBinary.java"/>
    <include name="**/*TestPermutations.java"/>
    <exclude name="**/*AbstractTest.java"/>
```

And even those do not cover all Testcases defined in the codebase.
