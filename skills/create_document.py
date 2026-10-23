import os
import re
from pathlib import Path
from typing import Any


PYTHON_GUIDE = """# Python Programming Guide

## What is Python?

Python is a readable, general-purpose programming language used for automation, web development, data analysis, artificial intelligence, and desktop tools.

## Your first program

```python
print(\"Hello, world!\")
```

## Variables and data

```python
name = \"Ada\"
age = 36
languages = [\"Python\", \"SQL\"]
is_learning = True
```

Common types include strings, integers, floating-point numbers, booleans, lists, tuples, dictionaries, and sets.

## Conditions and loops

```python
for number in range(5):
    if number % 2 == 0:
        print(number, \"is even\")
```

## Functions

```python
def greet(person: str) -> str:
    return f\"Hello, {person}!\"
```

Functions make code reusable and easier to test.

## Modules and packages

Put reusable code in modules and install third-party packages with `pip` or `uv`. Use a virtual environment for each project:

```powershell
uv venv
uv pip install requests
```

## Good next steps

Learn data structures, exceptions, file handling, testing with `pytest`, and object-oriented programming. Then build small projects such as a command-line tool, file organizer, or web API.
"""

JAVASCRIPT_GUIDE = """# JavaScript Programming Guide

## What is JavaScript?

JavaScript is a programming language used to make web pages interactive. It also runs outside browsers through platforms such as Node.js.

## Your first program

```javascript
console.log("Hello, world!");
```

## Variables and data

```javascript
const name = "Ada";
let age = 36;
const languages = ["JavaScript", "Python"];
const developer = { name, age };
```

Use `const` by default and `let` when a value must change. Avoid `var` in modern JavaScript.

## Conditions and loops

```javascript
for (let number = 0; number < 5; number += 1) {
    if (number % 2 === 0) {
        console.log(`${number} is even`);
    }
}
```

## Functions

```javascript
function greet(person) {
    return `Hello, ${person}!`;
}

console.log(greet("Ada"));
```

Arrow functions are useful for short operations:

```javascript
const double = (number) => number * 2;
```

## Working with web pages

```javascript
const button = document.querySelector("button");
button.addEventListener("click", () => {
    document.body.style.backgroundColor = "lightblue";
});
```

## Asynchronous code

```javascript
async function loadUser() {
    const response = await fetch("https://api.example.com/user");
    return response.json();
}
```

## Good next steps

Learn arrays and objects, modules, error handling, DOM events, promises, Node.js, and testing. Build a calculator, to-do list, weather page, or small API client.
"""

JAVA_GUIDE = """# Java Programming Guide

## What is Java?

Java is a strongly typed, object-oriented programming language designed to run on many platforms through the Java Virtual Machine (JVM). It is widely used for enterprise software, Android applications, backend services, and large systems.

## Your first program

```java
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, world!");
    }
}
```

Save the file as `Main.java`, then compile and run it:

```powershell
javac Main.java
java Main
```

## Variables and data

```java
String name = "Ada";
int age = 36;
double temperature = 21.5;
boolean learning = true;
```

Common types include `int`, `double`, `boolean`, `char`, and `String`.

## Conditions and loops

```java
for (int number = 0; number < 5; number++) {
    if (number % 2 == 0) {
        System.out.println(number + " is even");
    }
}
```

## Methods and classes

```java
public class Greeter {
    public String greet(String person) {
        return "Hello, " + person + "!";
    }
}
```

Classes combine data and behavior. Objects are created from classes with `new`.

## Collections

```java
import java.util.ArrayList;

ArrayList<String> languages = new ArrayList<>();
languages.add("Java");
languages.add("Python");
System.out.println(languages);
```

## Good next steps

Learn object-oriented programming, interfaces, exceptions, collections, streams, files, testing with JUnit, and backend development with Spring Boot.
"""

ML_GUIDE = """# Machine Learning Topics

## What is machine learning?

Machine learning (ML) is a field of artificial intelligence where computers learn patterns from data and use those patterns to make predictions or decisions.

## Main types of machine learning

- **Supervised learning:** learns from labeled examples, such as predicting house prices.
- **Unsupervised learning:** finds patterns in unlabeled data, such as customer groups.
- **Reinforcement learning:** learns actions through rewards and penalties, such as game-playing agents.

## A simple supervised-learning example

```python
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit([[1], [2], [3]], [2, 4, 6])
prediction = model.predict([[4]])
print(prediction)
```

The model learns a relationship between input values and target values, then predicts the target for new input.

## Important ML topics

1. **Data preparation:** clean missing values, encode categories, and scale numeric features.
2. **Features and labels:** features are inputs; labels are the expected answers.
3. **Training and testing:** train on one part of the data and evaluate on unseen data.
4. **Overfitting:** a model memorizes training data and performs poorly on new data.
5. **Evaluation:** use metrics such as accuracy, precision, recall, mean squared error, or F1 score.
6. **Neural networks:** layered models useful for images, speech, and language.

## A practical workflow

Define the problem, collect representative data, clean it, split it into training and test sets, train a baseline model, evaluate it, improve it, and monitor it after deployment.

## Good next steps

Learn Python, NumPy, pandas, scikit-learn, probability, statistics, linear algebra, neural networks, and responsible AI practices.
"""


def _safe_filename(topic: str) -> str:
    filename = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    return (filename or "untitled-document")[:80] + ".md"


def _offline_document(topic: str) -> str:
    return f"""# {topic.title()}

## Overview

This document introduces **{topic}** and provides a starting point for further study.

## Key ideas

- Define the main purpose and scope of {topic}.
- Identify its important concepts, terminology, and practical uses.
- Compare common approaches and note their strengths and limitations.

## Practical considerations

When working with {topic}, begin with a small example, verify assumptions, and consult
reliable sources for current or specialized information.

## Suggested next steps

1. Learn the core terminology.
2. Study a beginner-friendly example.
3. Build or analyze a small practical project.
4. Review authoritative references and recent developments.

> This is an offline starter draft. Configure an LLM API key to generate a more detailed document.
"""


def _llm_document(topic: str, model: str, api_key_env: str) -> str | None:
    api_key = os.getenv(api_key_env)
    if not api_key:
        return None
    from openai import OpenAI

    response = OpenAI(api_key=api_key).chat.completions.create(
        model=model,
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": "Write a clear, accurate Markdown document for a general reader. Use a title, overview, key concepts, practical examples, and next steps. Do not invent sources or claim current facts without qualification.",
            },
            {"role": "user", "content": f"Create a document about: {topic}"},
        ],
    )
    content = response.choices[0].message.content
    return content.strip() if content else None


def run(parameters: dict[str, Any]) -> str:
    output_dir = Path(parameters.get("documents_dir", "documents")).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    topic = str(parameters.get("topic", "")).strip()
    normalized_topic = topic.lower()
    if "javascript" in normalized_topic or "java script" in normalized_topic:
        output_path = output_dir / "javascript-programming-guide.md"
        content = JAVASCRIPT_GUIDE
        subject = "JavaScript"
    elif "java" in normalized_topic:
        output_path = output_dir / "java-programming-guide.md"
        content = JAVA_GUIDE
        subject = "Java"
    elif "machine learning" in normalized_topic or "ml topics" in normalized_topic or normalized_topic.endswith(" ml"):
        output_path = output_dir / "machine-learning-topics.md"
        content = ML_GUIDE
        subject = "machine learning"
    else:
        if not topic:
            return "What topic should I write the document about?"
        output_path = output_dir / _safe_filename(topic)
        try:
            content = _llm_document(
                topic,
                str(parameters.get("llm_model", "gpt-4o-mini")),
                str(parameters.get("api_key_env", "OPENAI_API_KEY")),
            ) or _offline_document(topic)
        except Exception:
            content = _offline_document(topic)
        subject = topic
    output_path.write_text(content, encoding="utf-8")
    return f"I created a document about {subject} at {output_path}."