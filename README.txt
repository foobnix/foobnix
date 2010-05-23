==MVN configuration==

1) Add Last.fm bindings to repository
mvn install:install-file -DgroupId=last-fm-bindings -DartifactId=last-fm-bindings -Dversion=7.3 -Dfile=last.fm-bindings.jar -DgeneratePom=true -Dpackaging=jar

2) Add QT libraries to configuration
mvn install:install-file -DgroupId=qt-jambi -DartifactId=qt-jambi -Dversion=4.5.2 -Dfile=qtjambi-4.5.2_01.jar -DgeneratePom=true -Dpackaging=jar
mvn install:install-file -DgroupId=qt-jambi -DartifactId=qt-jambi-linux32-gcc -Dversion=4.5.2 -Dfile=qtjambi-linux32-gcc-4.5.2_01.jar -DgeneratePom=true -Dpackaging=jar

==Eclipse Configuration==
1) Line width 120 symbols


