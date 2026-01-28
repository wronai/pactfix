FROM eclipse-temurin:21-jdk-jammy
WORKDIR /app
COPY . .
RUN if [ -f "pom.xml" ]; then ./mvnw package -DskipTests 2>/dev/null || mvn package -DskipTests; fi
RUN if [ -f "build.gradle" ]; then ./gradlew build -x test 2>/dev/null || gradle build -x test; fi
CMD ["java", "-jar", "target/*.jar", "||", "java", "Main"]
